from dataclasses import dataclass
from enum import Enum
from typing import Optional

from math_2d import Vector2D, Geometry2D


@dataclass
class Node:
    node_id: int
    vertex: Vector2D
    elements: list["Element"]
    elem_count: int
    u: float
    count: int


class BoundaryType(Enum):
    not_a_bound = 0  # не граница
    const_bound = 1  # задана температура на границе
    bound_insulated = 2  # поток = 0 через грань (изолирована)


class Face:
    def __init__(
            self,
            v1: Vector2D,
            v2: Vector2D
    ):
        self.vertex: list[Vector2D] = [v1, v2]
        self.is_boundary: bool = False
        self.bound_domain: int = -1
        self.bound_group: int = -1

        self.id: int = 0
        self.point_id_1: int = 0
        self.point_id_2: int = 0
        self.owner: Optional[Element] = None
        self.neighbour_elem: Optional[Element] = None
        self.centroid: Vector2D = Vector2D(0, 0)
        #  единичный вектор нормали к грани (вне элемента-владельца)
        self.normal: Vector2D = Vector2D(0, 0)
        self.sf: Vector2D = Vector2D(0, 0)  # surface?
        self.face_interpol_coeff: float = 0
        self.area: float = 0
        self.k: float = 0
        self.u: float = 0
        self.boundary_type: BoundaryType = BoundaryType.not_a_bound
        self.bound_u: float = 0
        self.bound_flux: float = 0
        self.htrans_coeff: float = 0

    @staticmethod
    def get_face_str_id(p1_index: int, p2_index: int) -> str:
        if p1_index > p2_index:
            p1_index, p2_index = p2_index, p1_index
        return str(p1_index) + "_" + str(p2_index)

    def set_boundary(self, boundary_type: BoundaryType, value: float, hcoeff: float = 0) -> None:
        self.boundary_type = boundary_type
        self.is_boundary = True
        self.htrans_coeff = hcoeff
        if boundary_type == BoundaryType.const_bound:
            self.bound_u = value

    def calc(self) -> None:
        self.area = (self.vertex[0] - self.vertex[1]).__len__()
        self.centroid = (self.vertex[0] + self.vertex[1]) / 2
        self.normal = Geometry2D.line_normal(self.vertex[0], self.vertex[1])
        self.sf = Geometry2D.surface_normal(self.vertex[0], self.vertex[1])

        if self.neighbour_elem is not None:
            self.face_interpol_coeff = self.owner.volume / (self.owner.volume + self.neighbour_elem.volume)
            self.k = (
                    self.owner.k * self.neighbour_elem.k /
                    (
                        (1 - self.face_interpol_coeff) * self.owner.k +
                        self.face_interpol_coeff * self.neighbour_elem.k
                    )
            )
        else:
            self.k = self.owner.k


class Element:
    def __init__(
            self,
            vcount: int
    ):
        self.u: float = 0
        self.k: float = 0
        self.id: int = -1

        self.list_length = vcount
        self.faces: list[Optional["Face"]] = [None for _ in range(vcount)]
        self.neighbours: list[Optional["Element"]] = [None for _ in range(vcount)]
        self.vertex: list[Optional[Vector2D]] = [None for _ in range(vcount)]  # от левой нижней против часовой
        self.nodes: list[Optional["Node"]] = [None for _ in range(vcount)]
        #  вектор до центра объема соседей
        self.center_neighbour_dist: list[Optional[Vector2D]] = [None for _ in range(vcount)]
        self.node_distances: list[Optional[float]] = [None for _ in range(vcount)]
        #  вектор от центра до центра граней
        self.center_face_dist: list[Optional[Vector2D]] = [None for _ in range(vcount)]
        #  вектор от центра соседа до центра граней
        self.neighbour_face_dist: list[Optional[Vector2D]] = [None for _ in range(vcount)]
        #  для интерполяции значений на грани между элементами по значениям в элементах
        self.geom_interpolate_factor: list[Optional[float]] = [None for _ in range(vcount)]
        self.flux: list[Optional[float]] = [None for _ in range(vcount)]

        self.node_count: int = 0
        self.volume: float = 0
        self.centroid: Vector2D = Vector2D(0, 0)

    def set_polygon(self, vertexs: list[Vector2D]) -> None:
        self.vertex = vertexs

    def face_local_id(self, face: Face) -> int:
        for i in range(self.list_length):
            if self.faces[i] is face or self.faces[i] == face:
                return i
        return -1

    def precalc(self) -> None:
        self.centroid = Geometry2D.polygon_centroid(self.vertex)
        self.volume = Geometry2D.polygon_area(self.vertex)

    def calc_fluxes(self):
        for num_face in range(self.list_length):
            face = self.faces[num_face]

            # some magic
            sf: Vector2D = face.sf.clone()
            dcf: Vector2D = self.center_face_dist[num_face].clone()
            if sf * dcf < 0:
                sf = -sf
            e1: Vector2D = dcf.get_normalize()
            ef: Vector2D = e1 * (e1 * sf)

            if face.is_boundary:
                if face.boundary_type == BoundaryType.const_bound:
                    self.flux[num_face] = self.k * (ef.__len__() / dcf.__len__())
                elif face.boundary_type == BoundaryType.bound_insulated:
                    self.flux[num_face] = 0
            else:
                self.flux[num_face] = -self.k * (ef.__len__() / dcf.__len__())

    def calc(self) -> None:
        for num_face in range(self.list_length):
            if self.faces[num_face].owner is self:
                self.faces[num_face].calc()

            neighbour = self.neighbours[num_face]
            self.center_face_dist[num_face] = self.faces[num_face].centroid - self.centroid

            if neighbour is not None:
                self.center_neighbour_dist[num_face] = neighbour.centroid - self.centroid
                self.node_distances[num_face] = self.center_neighbour_dist[num_face].__len__()
                self.neighbour_face_dist[num_face] = neighbour.centroid - self.faces[num_face].centroid

                self.geom_interpolate_factor[num_face] = (
                        self.center_face_dist[num_face].__len__() /
                        (self.center_face_dist[num_face].__len__() + self.neighbour_face_dist[num_face].__len__())
                )
            else:
                self.center_neighbour_dist[num_face] = self.faces[num_face].centroid - self.centroid
                self.node_distances[num_face] = self.center_neighbour_dist[num_face].__len__()

from typing import Optional

from element import Element, Face, BoundaryType
from loader import load_from_file
from math_2d import Vector2D
from periodic_boundary import periodic_boundary_condition


class HeatEquationSolver:
    def __init__(self, domain: str):
        self.element_count: int = 0
        self.elements: list[Element] = list()
        self.faces: list[Face] = list()
        self.bound_faces: list[Face] = list()
        self.node_count: int = 0
        self.delta: float = 0
        self.domain: str = domain
        self.iteration_count: int = 0

    def set_initial_boundary(self) -> None:
        for e in range(self.element_count):
            self.elements[e].u = 0
        self.set_periodic_boundary()

    def set_periodic_boundary(self) -> None:
        for face in self.bound_faces:
            face.set_boundary(
                BoundaryType.const_bound,
                periodic_boundary_condition(self.domain, face.bound_domain, face.bound_group)
            )

    def calc(self):
        bc: float = 0
        ac: float = 0
        sumflux: float = 0
        aa: list[float] = [0 for _ in range(6)]  # seems like useless
        bb: list[float] = [0 for _ in range(6)]  # seems like useless

        for elem in self.elements:
            bc = 0
            ac = 0
            sumflux = 0
            for num_face in range(elem.vertex.__len__()):
                face: Face = elem.faces[num_face]
                neighbour: Element = elem.neighbours[num_face]
                if face.is_boundary:
                    ac += elem.flux[num_face]
                    bc += elem.flux[num_face] * face.bound_u
                    bb[num_face] = elem.flux[num_face]
                else:
                    sumflux += elem.flux[num_face] * neighbour.u
                    ac += -elem.flux[num_face]
                    aa[num_face] = -elem.flux[num_face]
            elem.u = elem.u + self.delta * (bc - sumflux - ac * elem.u)

    def set_parameters(self):
        self.delta = 0.015

    def create_volume_decomposition(
            self,
            points: list[list[float | int]],
            polys:  list[list[float | int]],
            bound:  list[list[float | int]]
    ):
        face_dict: dict[str, Face] = dict()

        self.set_parameters()

        self.element_count = len(polys[0])
        vertex_count: int = len(polys) - 1
        self.elements: list[Element] = [None for _ in range(self.element_count)]

        face_id: int = 0
        for e in range(self.element_count):
            self.elements[e] = Element(vertex_count)
            self.elements[e].id = e
            self.elements[e].k = 1

            vertex: list[Vector2D] = [None for _ in range(vertex_count)]
            for v in range(vertex_count):
                p1_index: int = int(polys[v][e])  # first point index
                p2_index = int(polys[(v + 1) % vertex_count][e])  # second point index

                vertex[v] = Vector2D(points[0][p1_index], points[1][p1_index])
                face_str = Face.get_face_str_id(p1_index, p2_index)

                if not face_str in face_dict.keys():
                    face: Face = Face(
                        Vector2D(points[0][p1_index], points[1][p1_index]),
                        Vector2D(points[0][p2_index], points[1][p2_index])
                    )
                    face.id = face_id
                    face.point_id_1 = p1_index
                    face.point_id_2 = p2_index
                    face.owner = self.elements[e]
                    face_id += 1
                    face_dict[face_str] = face
                    self.elements[e].faces[v] = face
                else:
                    face: Face = face_dict[face_str]
                    face.neighbour_elem = self.elements[e]
                    self.elements[e].faces[v] = face
                    owner: Element = face.owner
                    self.elements[e].neighbours[v] = owner
                    owner.neighbours[owner.face_local_id(face)] = self.elements[e]

            self.elements[e].set_polygon(vertex)
            self.elements[e].precalc()

        self.faces: list[Optional[Face]] = [None for _ in range(len(face_dict))]
        self.bound_faces: list[Optional[Face]] = [None for _ in range(len(bound[0]))]

        for key, value in face_dict.items():
            self.faces[value.id] = value

        for e in range(self.element_count):
            self.elements[e].calc()

        for f in range(len(bound[0])):
            face_str = Face.get_face_str_id(int(bound[0][f]), int(bound[1][f]))
            face: Face = face_dict[face_str]
            face.bound_domain = int(bound[5][f])
            face.bound_group = int(bound[4][f])
            face.is_boundary = True
            self.bound_faces[f] = face

        self.set_initial_boundary()

        for elem in self.elements:
            elem.calc_fluxes()

    def run_physics(self) -> None:
        self.iteration_count += 1
        self.set_periodic_boundary()
        self.calc()

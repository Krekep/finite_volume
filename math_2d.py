from typing import Union

import numpy as np
from numpy.linalg import norm


class Vector2D:
    def __init__(self, x: float | np.float64, y: float | np.float64):
        self.data: np.ndarray[np.float64] = np.array([x, y], dtype=np.float64)

    def clone(self) -> "Vector2D":
        return Vector2D(self.data[0], self.data[1])

    def __getitem__(self, i: int) -> np.float64:
        return self.data[i]

    def __setitem__(self, key: int, value: float | np.float64):
        self.data[key] = value

    def __len__(self) -> float:
        return np.sqrt(np.sum(self.data ** 2))

    def get_normalize(self) -> "Vector2D":
        new_data = self.data / np.sqrt(np.sum(self.data ** 2))
        return Vector2D(new_data[0], new_data[1])

    def normalize(self):
        self.data = self.data / np.sqrt(np.sum(self.data ** 2))

    def __mul__(self, other) -> Union["Vector2D", float]:
        if isinstance(other, (int, float)):
            return Vector2D(self.data[0] * other, self.data[1] * other)
        if isinstance(other, Vector2D):
            return self.data[0] * other.data[0] + self.data[1] * other.data[1]
        raise ValueError(f"Cannot multiply Vector2d with {type(other)}")

    def __add__(self, other) -> "Vector2D":
        if isinstance(other, (int, float)):
            return Vector2D(self.data[0] + other, self.data[1] + other)
        if isinstance(other, Vector2D):
            return Vector2D(self.data[0] + other.data[0], self.data[1] + other.data[1])
        raise ValueError(f"Cannot summary Vector2d with {type(other)}")

    def __sub__(self, other) -> "Vector2D":
        if isinstance(other, (int, float)):
            return Vector2D(self.data[0] - other, self.data[1] - other)
        if isinstance(other, Vector2D):
            return Vector2D(self.data[0] - other.data[0], self.data[1] - other.data[1])
        raise ValueError(f"Cannot substract Vector2d with {type(other)}")

    def __truediv__(self, other) -> "Vector2D":
        if isinstance(other, (int, float)):
            return Vector2D(self.data[0] / other, self.data[1] / other)
        if isinstance(other, Vector2D):
            return Vector2D(self.data[0] / other.data[0], self.data[1] / other.data[1])
        raise ValueError(f"Cannot substract Vector2d with {type(other)}")

    def __neg__(self) -> "Vector2D":
        return Vector2D(-self.x, -self.y)

    @property
    def x(self) -> np.float64:
        return self.data[0]

    @property
    def y(self) -> np.float64:
        return self.data[1]

class Geometry2D:

    @staticmethod
    def triangle_area(v1: Vector2D, v2: Vector2D, v3: Vector2D) -> float:
        triarea = abs(
            v1.x * (v2.y - v3.y) +
            v2.x * (v3.y - v1.y) +
            v3.x * (v1.y - v2.y)
        ) / 2
        return triarea

    @staticmethod
    def triangle_center(v1: Vector2D, v2: Vector2D, v3: Vector2D) -> Vector2D:
        return (v1 + v2 + v3) / 3

    @staticmethod
    def line_normal(v1: Vector2D, v2: Vector2D) -> Vector2D:
        diff = v2 - v1
        return Vector2D(diff.y, -diff.x).get_normalize()

    @staticmethod
    def surface_normal(v1: Vector2D, v2: Vector2D) -> Vector2D:
        diff = v2 - v1
        return Vector2D(diff.y, -diff.x)

    @staticmethod
    def polygon_centroid(vertex: list[Vector2D]) -> Vector2D:
        poly_geom_center = Vector2D(0, 0)
        for v in vertex:
            poly_geom_center += v
        poly_geom_center /= len(vertex)

        polygon_center = Vector2D(0, 0)
        polygon_area = 0

        for i in range(len(vertex)):
            v1 = vertex[i]
            v2 = vertex[(i + 1) % len(vertex)]
            triangle_geom_center = Geometry2D.triangle_center(v1, v2, poly_geom_center)
            triarea = Geometry2D.triangle_area(v1, v2, poly_geom_center)
            polygon_area += triarea
            polygon_center += triangle_geom_center * triarea

        polygon_center /= polygon_area

        return polygon_center

    @staticmethod
    def polygon_area(vertex: list[Vector2D]) -> float:
        poly_geom_center = Vector2D(0, 0)
        for v in vertex:
            poly_geom_center += v
        poly_geom_center /= len(vertex)

        polygon_area = 0
        for i in range(len(vertex)):
            v1 = vertex[i]
            v2 = vertex[(i + 1) % len(vertex)]
            triarea = Geometry2D.triangle_area(v1, v2, poly_geom_center)
            polygon_area += triarea
        return polygon_area

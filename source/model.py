from __future__ import annotations

import math
from _decimal import Decimal
from typing import Optional, List

from pydantic import confloat, ConfigDict, model_validator
from pydantic.dataclasses import dataclass

default_config = dict(
    slots=True,
    config=ConfigDict(validate_assignment=True, arbitrary_types_allowed=True),
)


@dataclass(**default_config)
class Vertex:
    x: Decimal
    y: Decimal
    z: Decimal
    normal: Optional[Normal] = None  # This can allow to cache the normal

    def __add__(self, other):
        return Vertex(x=self.x + other.x, y=self.y + other.y, z=self.z + other.z)

    def vector(self) -> Vector3d:
        return Vector3d(float(self.x), float(self.y), float(self.z))

    def __eq__(self, other):
        if not isinstance(other, Vertex):
            return False
        return self.x == other.x and self.y == other.y and self.z == other.z


@dataclass(**default_config)
class Normal:
    x: confloat(ge=-1, le=1)
    y: confloat(ge=-1, le=1)
    z: confloat(ge=-1, le=1)


@dataclass(**default_config)
class Face:
    vertices: List[Vertex]


@dataclass(**default_config)
class Polyhedron:
    faces: List[Face]

    def __eq__(self, other):
        if not isinstance(other, Polyhedron):
            return False
        return self.faces == other.faces


@dataclass(**default_config)
class SliceInterval:
    x0: Decimal = None
    x1: Decimal = None
    y0: Decimal = None
    y1: Decimal = None
    z0: Decimal = None
    z1: Decimal = None

    @model_validator(mode="after")
    @classmethod
    def check_order(cls, slice):
        # This might make the logic easier to implement? For me it is not a problem to have this enforced
        if all([slice.x0, slice.x1]) and slice.x0 > slice.x1:
            raise ValueError("x0 should be smaller than x1")
        if all([slice.y0, slice.y1]) and slice.y0 > slice.y1:
            raise ValueError("y0 should be smaller than y1")
        if all([slice.z0, slice.z1]) and slice.z0 > slice.z1:
            raise ValueError("z0 should be smaller than z1")

        return slice


@dataclass
class Slice:
    x: Decimal = None
    y: Decimal = None
    z: Decimal = None


@dataclass(**default_config)
class Vector3d:
    x: float
    y: float
    z: float

    def __add__(self, other):
        return Vector3d(x=self.x + other.x, y=self.y + other.y, z=self.z + other.z)

    def __sub__(self, other):
        return Vector3d(x=self.x - other.x, y=self.y - other.y, z=self.z - other.z)

    def __mul__(self, other):
        return Vector3d(x=self.x * other, y=self.y * other, z=self.z * other)

    def __truediv__(self, other):
        return self * (1 / other)

    def dotProduct(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def crossProduct(self, other):
        return Vector3d(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def squaredLength(self):
        return self.dotProduct(self)

    def length(self):
        return math.sqrt(self.squaredLength())

    def normalized(self):
        return self / self.length()


@dataclass(**default_config)
class Plane3d:
    origin: Vector3d
    normal: Vector3d


@dataclass(**default_config)
class Line3d:
    origin: Vector3d
    direction: Vector3d

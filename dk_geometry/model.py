from __future__ import annotations

import math
from enum import Enum
from typing import List

from pydantic import confloat, ConfigDict, model_validator
from pydantic.dataclasses import dataclass

default_config = dict(
    slots=True,
    config=ConfigDict(
        validate_assignment=True, arbitrary_types_allowed=True, frozen=True
    ),
)


@dataclass(**default_config)
class Normal:
    x: confloat(ge=-1, le=1)
    y: confloat(ge=-1, le=1)
    z: confloat(ge=-1, le=1)


@dataclass(**default_config)
class Face:
    vertices: List[Vector3d]

    @property
    def plane(self):
        from .general import calculate_contour_normal

        return Plane3d(
            origin=self.vertices[0],
            normal=calculate_contour_normal(self.vertices),
        )

    @property
    def orientation(self) -> Orientation:
        return self.plane.orientation


@dataclass(**default_config)
class Polyhedron:
    faces: List[Face]

    def __deepcopy__(self, memodict=None) -> Polyhedron:
        memodict = {}
        for face in self.faces:
            for vector in face.vertices:
                if not (id(vector) in memodict):
                    memodict[id(vector)] = Vector3d(vector.x, vector.y, vector.z)
        return Polyhedron(
            faces=[
                Face(vertices=[memodict[id(v)] for v in face.vertices])
                for face in self.faces
            ]
        )


@dataclass(**default_config)
class SliceInterval:
    x0: float = None
    x1: float = None
    y0: float = None
    y1: float = None
    z0: float = None
    z1: float = None

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
    x: float = None
    y: float = None
    z: float = None


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

    @property
    def squaredLength(self):
        return self.dotProduct(self)

    @property
    def length(self):
        return math.sqrt(self.squaredLength)

    @property
    def normalized(self):
        return self / self.length


class Orientation(Enum):
    """Indicates which absolute normals are different from 0"""

    X = "X"  # Vertical - typically used for tops, bottoms and shelves
    Y = "Y"  # Horizontal - typically used for sides
    Z = "Z"  # Depth - typically used for front and backpanels
    XY = "XY"  # Sloped panels in XY
    YZ = "YZ"  # Sloped panels in YZ
    OTHER = "OTHER"  # Other orientation

    def __neg__(self):
        if self.name == "X":
            return Orientation.Y
        if self.name == "Y":
            return Orientation.X
        else:
            raise NotImplemented


@dataclass(**default_config)
class Plane3d:
    origin: Vector3d
    normal: Vector3d

    @property
    def orientation(self) -> Orientation:
        normal_length = self.normal.length * 0.99
        types = []

        abs_x = math.fabs(self.normal.x)
        if abs_x > normal_length:
            return Orientation.X
        abs_y = math.fabs(self.normal.y)
        if abs_y > normal_length:
            return Orientation.Y
        abs_z = math.fabs(self.normal.z)
        if abs_z > normal_length:
            return Orientation.Z
        if abs_x + abs_y > normal_length:
            return Orientation.XY
        if abs_y + abs_z > normal_length:
            return Orientation.YZ
        return Orientation.OTHER


@dataclass(**default_config)
class Line3d:
    origin: Vector3d
    direction: Vector3d

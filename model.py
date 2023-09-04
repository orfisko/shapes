from __future__ import annotations

from _decimal import Decimal
from typing import Optional, List

from pydantic import confloat, ConfigDict, model_validator, conint
from pydantic.dataclasses import dataclass

from geometry import Vector3d

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

    def vector(self):
        return Vector3d(self.x, self.y, self.z)


@dataclass(**default_config)
class Normal:
    x: confloat(ge=-1, le=1)
    y: confloat(ge=-1, le=1)
    z: confloat(ge=-1, le=1)


@dataclass(**default_config)
class Face:
    vertices: List[Vertex]
    index: conint(ge=0) = 0


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

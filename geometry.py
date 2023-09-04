from __future__ import annotations

from pydantic import confloat, ConfigDict, model_validator
from pydantic.dataclasses import dataclass

import math

default_config = dict(
    slots=True,
    config=ConfigDict(validate_assignment=True, arbitrary_types_allowed=True),
)

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
        return Vector3d(x=self.x*other, y=self.y*other, z=self.z*other)
    def __truediv__(self, other):
        return self*(1/other)
    def dotProduct(self, other):
        return self.x*other.x + self.y*other.y + self.z*other.z
    def crossProduct(self, other):
        return Vector3d(
            self.y*other.z - self.z*other.y,
            self.z*other.x - self.x*other.z,
            self.x*other.y - self.y*other.x)
    def squaredLength(self):
        return self.dotProduct(self)
    def length(self):
        return math.sqrt(self.squaredLength())

def calculate_contour_normal(points):
    sum = Vector3d(0, 0, 0)
    for index in range(len(points)):
        next = (index+1)%len(points)
        sum += points[index].crossProduct(points[next])
    return sum / sum.length()

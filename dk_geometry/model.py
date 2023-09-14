from __future__ import annotations

import math

from pydantic import confloat, ConfigDict, model_validator
from pydantic.dataclasses import dataclass

from dk_geometry.enums import FaceNormal

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
    vertices: list[Vector3d]

    @dataclass(**default_config)
    class LWDimensions:
        length: float
        width: float

        def __iter__(self):
            return iter((self.length, self.width))

    @property
    def plane(self):
        return Plane3d(
            origin=self.vertices[0],
            normal=self.areaVector.normalized,
        )

    @property
    def areaVector(self) -> Vector3d:
        area = Vector3d(0, 0, 0)
        for e in range(len(self.vertices)):
            edge = self.get_edge(e)
            area += edge[0].crossProduct(edge[1]) / 2
        return area

    @property
    def surfaceArea(self) -> float:
        return self.areaVector.length

    @property
    def faceNomal(self) -> FaceNormal:
        return self.plane.faceNormal

    @property
    def min_x(self):
        return min([v.x for v in self.vertices])

    @property
    def max_x(self):
        return max([v.x for v in self.vertices])

    @property
    def min_y(self):
        return min([v.y for v in self.vertices])

    @property
    def max_y(self):
        return max([v.y for v in self.vertices])

    @property
    def min_z(self):
        return min([v.z for v in self.vertices])

    @property
    def max_z(self):
        return max([v.z for v in self.vertices])

    @property
    def lw_dimensions(self) -> Face.LWDimensions:
        """
        Assuming the face has long and narrow shape, returns its length and width.
        """
        longest_edge = max(
            [self.get_edge(i) for i in range(len(self.vertices))],
            key=lambda edge: (edge[1] - edge[0]).length,
        )
        length_direction = (longest_edge[1] - longest_edge[0]).normalized
        width_direction = self.plane.normal.crossProduct(length_direction)

        def measure_size(vertices, direction):
            parameters = [v.dotProduct(direction) for v in vertices]
            return max(parameters) - min(parameters)

        return Face.LWDimensions(
            length=measure_size(self.vertices, length_direction),
            width=measure_size(self.vertices, width_direction),
        )

    def get_edge(self, index: int) -> tuple[Vector3d, Vector3d]:
        return self.vertices[index], self.vertices[(index + 1) % len(self.vertices)]


@dataclass(**default_config)
class Polyhedron:
    faces: list[Face]

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

    @property
    def min_x(self):
        return min([v.min_x for v in self.faces])

    @property
    def max_x(self):
        return max([v.max_x for v in self.faces])

    @property
    def min_y(self):
        return min([v.min_y for v in self.faces])

    @property
    def max_y(self):
        return max([v.max_y for v in self.faces])

    @property
    def min_z(self):
        return min([v.min_z for v in self.faces])

    @property
    def max_z(self):
        return max([v.max_z for v in self.faces])

    @property
    def boundingBox(self) -> Polyhedron:
        """Insert wizardry here"""

    @property
    def volume(self) -> float:
        volume = 0
        for face in self.faces:
            for index in range(len(face.vertices) - 2):
                a = face.vertices[index]
                b = face.vertices[index + 1]
                c = face.vertices[index + 2]
                volume += a.crossProduct(b).dotProduct(c) / 6
        return volume

    def get_face_indices_by_orientation(self, orientation: FaceNormal) -> list[int]:
        return [
            idx for idx, face in enumerate(self.faces) if face.faceNomal == orientation
        ]


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


@dataclass(**default_config)
class Plane3d:
    origin: Vector3d
    normal: Vector3d

    @property
    def faceNormal(self) -> FaceNormal:
        types = []

        if self.normal.x > 0:
            types.append("R")
        if self.normal.x < 0:
            types.append("L")
        if self.normal.y < 0:
            types.append("B")
        if self.normal.z > 0:
            types.append("F")
        if self.normal.y > 0:
            types.append("T")
        if self.normal.z < 0:
            types.append("BK")

        return FaceNormal.from_stringlist(types)


@dataclass(**default_config)
class Line3d:
    origin: Vector3d
    direction: Vector3d

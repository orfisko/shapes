from __future__ import annotations

import math
from _decimal import Decimal
from collections import defaultdict
from copy import deepcopy
from typing import Optional, List, DefaultDict

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


@dataclass(**default_config)
class Normal:
    x: confloat(ge=-1, le=1)
    y: confloat(ge=-1, le=1)
    z: confloat(ge=-1, le=1)


@dataclass(**default_config)
class Face:
    vertices: List[Vertex]

    def compute_plane(self):
        from source.geometry import calculate_contour_normal

        return Plane3d(
            origin=self.vertices[0].vector(),
            normal=calculate_contour_normal([v.vector() for v in self.vertices]),
        )


@dataclass(**default_config)
class Polyhedron:
    faces: List[Face]

    def __deepcopy__(self, memodict=None) -> Polyhedron:
        memodict = {}
        for face in self.faces:
            for vertex in face.vertices:
                if not (id(vertex) in memodict):
                    memodict[id(vertex)] = Vertex(vertex.x, vertex.y, vertex.z)
        return Polyhedron(
            faces=[
                Face(vertices=[memodict[id(v)] for v in face.vertices])
                for face in self.faces
            ]
        )

    def apply_offset(
        self,
        offset: Optional[Decimal] = None,
        offset_map: Optional[dict[int, Decimal]] = None,
    ) -> Polyhedron:
        """
        Generates a new polyhedron with the offset applied to the vertices. The offset is applied to all faces unless
        an offset_map is supplied. The offset_map is a dictionary with the face index as key and the offset as value.
        Args:
            polyhedron: the polyhedron for which the offset needs to be applied
            offset: global offset for all faces, defaults to 0 if offset_map is supplied
            offset_map: offset to apply on the face with the specified index as key. Missing values are filled with the
                offset value

        Returns:
            a new polyhedron with the offset applied
        """
        from source.geometry import compute_three_planes_intersection

        if not any((offset, offset_map)):
            raise ValueError("Either offset or offset_map needs to be supplied")
        if offset_map is None:
            offset_map = dict()
        if offset is None:
            offset = Decimal(0)
        # Fill the offset_map with the offset if it is not supplied.
        offset_map.update(
            {
                loc: offset
                for loc in range(0, len(self.faces))
                if loc not in offset_map.keys()
            }
        )

        offset_poly = deepcopy(self)

        vertex_to_face_indices: DefaultDict[int, List[int]] = defaultdict(list)
        vertices = []
        for face_index in range(len(offset_poly.faces)):
            for vertex in offset_poly.faces[face_index].vertices:
                if not (id(vertex) in vertex_to_face_indices):
                    # vertex_to_face_indices[id(vertex)] = []
                    vertices.append(vertex)
                vertex_to_face_indices[id(vertex)].append(face_index)

        for vertex in vertices:
            adjacent_face_indices = vertex_to_face_indices[id(vertex)]
            if len(adjacent_face_indices) != 3:
                raise ValueError(
                    "Some polyhedron vertex does not have exactly 3 adjacent faces"
                )
            planes = []
            for face_index in adjacent_face_indices:
                plane = self.faces[face_index].compute_plane()
                face_offset = float(offset_map[face_index])
                plane.origin += plane.normal.normalized() * face_offset
                planes.append(plane)
            new_position = compute_three_planes_intersection(
                planes[0], planes[1], planes[2]
            )
            vertex.x = Decimal(round(new_position.x, 1))
            vertex.y = Decimal(round(new_position.y, 1))
            vertex.z = Decimal(round(new_position.z, 1))
        return offset_poly


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
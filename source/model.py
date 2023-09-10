from __future__ import annotations

import math
from _decimal import Decimal
from collections import defaultdict
from copy import deepcopy
from enum import Enum
from typing import Optional, List, DefaultDict

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
    vectors: List[Vector3d]

    @property
    def plane(self):
        from source.general import calculate_contour_normal

        return Plane3d(
            origin=self.vectors[0],
            normal=calculate_contour_normal(self.vectors),
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
            for vector in face.vectors:
                if not (id(vector) in memodict):
                    memodict[id(vector)] = vector
        return Polyhedron(
            faces=[
                Face(vectors=[memodict[id(v)] for v in face.vectors])
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
            offset: global offset for all faces, defaults to 0 if offset_map is supplied
            offset_map: offset to apply on the face with the specified index as key. Missing values are filled with the
                offset value

        Returns:
            a new polyhedron with the offset applied
        """
        from source.general import compute_three_planes_intersection

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
            for vertex in offset_poly.faces[face_index].vectors:
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
                plane = self.faces[face_index].plane
                face_offset = float(offset_map[face_index])
                plane.origin += plane.normal.normalized * face_offset
                planes.append(plane)
            new_position = compute_three_planes_intersection(
                planes[0], planes[1], planes[2]
            )
            vertex.x = Decimal(round(new_position.x, 1))
            vertex.y = Decimal(round(new_position.y, 1))
            vertex.z = Decimal(round(new_position.z, 1))
        for index in range(len(self.faces)):
            original_normal = self.faces[index].plane.normal
            offset_normal = offset_poly.faces[index].plane.normal
            if original_normal.dotProduct(offset_normal) < 0:
                raise ValueError("offset completely removed one face")
        return offset_poly


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

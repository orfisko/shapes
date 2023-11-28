from __future__ import annotations

import math
from decimal import Decimal

from pydantic import confloat, ConfigDict, BaseModel
from pydantic.dataclasses import dataclass

from dk_geometry.enums import AngleType, FaceNormal

default_config = dict(
    config=ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
        frozen=True,
        extra="forbid",
    ),
)


@dataclass(**default_config)
class Vector3d:
    x: float
    y: float
    z: float

    def __post_init__(self):
        # Round the float attributes to a certain number of decimal places
        self.x = round(self.x, 5)
        self.y = round(self.y, 5)
        self.z = round(self.z, 5)

    def __add__(self, other):
        return Vector3d(x=self.x + other.x, y=self.y + other.y, z=self.z + other.z)

    def __sub__(self, other):
        return Vector3d(x=self.x - other.x, y=self.y - other.y, z=self.z - other.z)

    def __neg__(self):
        return Vector3d(x=-self.x, y=-self.y, z=-self.z)

    def __mul__(self, other):
        return Vector3d(x=self.x * other, y=self.y * other, z=self.z * other)

    def __truediv__(self, other):
        return self * (1 / other)

    def __eq__(self, other):
        return (
            round(self.x, 2) == round(other.x, 2)
            and round(self.y, 2) == round(other.y, 2)
            and round(self.z, 2) == round(other.z, 2)
        )

    def __hash__(self):
        return hash((round(self.x,2), round(self.y,2), round(self.z,2)))

    def dotProduct(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def crossProduct(self, other):
        return Vector3d(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def as_tuple(self) -> tuple[Decimal, Decimal, Decimal]:
        # Scales the coordinates and return a tuple of decimals
        SCALE_FACTOR = 1000
        return (
            Decimal(round(self.x, 1) / SCALE_FACTOR),
            Decimal(round(self.y, 1) / SCALE_FACTOR),
            Decimal(round(self.z, 1) / SCALE_FACTOR),
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

        if round(self.normal.x, 3) < 0:
            types.append("L")  # left
        if round(self.normal.x, 3) > 0:
            types.append("R")  # right
        if round(self.normal.y, 3) < 0:
            types.append("B")  # bottom
        if round(self.normal.y, 3) > 0:
            types.append("T")  # top
        if round(self.normal.z, 3) < 0:
            types.append("BK")  # Back
        if round(self.normal.z, 3) > 0:
            types.append("F")  # Front

        return FaceNormal.from_stringlist(types)

    @property
    def inversedFaceNormal(self) -> FaceNormal:
        types = []
        if round(self.normal.x, 3) < 0:
            types.append("L")
        if round(self.normal.x, 3) > 0:
            types.append("R")
        if round(self.normal.y, 3) < 0:
            types.append("B")
        if round(self.normal.y, 3) > 0:
            types.append("T")
        if round(self.normal.z, 3) < 0:
            types.append("BK")
        if round(self.normal.z, 3) > 0:
            types.append("F")

        return FaceNormal.from_stringlist(types)


@dataclass(**default_config)
class Line3d:
    origin: Vector3d
    direction: Vector3d


@dataclass(**default_config)
class FaceOverlap:
    poly_index: int
    face_index: int
    area: float


@dataclass(**default_config)
class Normal:
    x: confloat(ge=-1, le=1)
    y: confloat(ge=-1, le=1)
    z: confloat(ge=-1, le=1)


@dataclass(**default_config)
class Face:
    vertices: list[Vector3d]

    def __eq__(self, other):
        sorted_vertices = sorted(self.vertices, key=lambda v: (v.x, v.y, v.z))
        sorted_other_vertices = sorted(other.vertices, key=lambda v: (v.x, v.y, v.z))
        return (
            sorted_vertices == sorted_other_vertices
            and self.faceNormal == other.faceNormal
        )

    @dataclass(**default_config)
    class LWDimensions:
        length: float
        width: float

        def __iter__(self):
            return iter((self.length, self.width))

    @property
    def plane(self) -> Plane3d:
        return Plane3d(
            origin=self.vertices[0],
            normal=self.areaVector.normalized,
        )

    @property
    def triangles(self) -> list[list[Vector3d]]:
        def are_points_on_the_same_side_of_line(point1:Vector3d, point2:Vector3d, line:Line3d):
            normal1=(point1-line.origin).crossProduct(line.direction)
            normal2=(point2-line.origin).crossProduct(line.direction)
            return normal1.dotProduct(normal2)>0
        def is_point_in_triangle(point:Vector3d, triangle:list[Vector3d], tolerance):
            for edge_index in range(3):
                line = Line3d(
                    triangle[edge_index],
                    triangle[(edge_index+1)%3]-triangle[edge_index])
                third_point = triangle[(edge_index+2)%3]
                if not are_points_on_the_same_side_of_line(point, third_point, line):
                    if (point-line.origin).crossProduct(line.direction).length>tolerance*line.direction.length:
                        return False
            return True
        face_normal = self.plane.normal
        contour = self.vertices[:]
        triangles = []
        while len(contour)>3:
            for corner_index in range(len(contour)):
                previous_index = (corner_index-1)%len(contour)
                next_index = (corner_index+1)%len(contour)
                triangle = [
                    contour[previous_index],
                    contour[corner_index],
                    contour[next_index]
                ]
                if Face(vertices=triangle).areaVector.dotProduct(face_normal)<0:
                    continue
                can_be_cut = True
                for another_index in range(len(contour)):
                    if another_index in [corner_index, previous_index, next_index]:
                        continue
                    if is_point_in_triangle(contour[another_index], triangle, 0.001):
                        can_be_cut = False
                        break
                if not can_be_cut:
                    continue
                triangles.append(triangle)
                contour.pop(corner_index)
                break
        triangles.append(contour)
        return triangles

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
    def faceNormal(self) -> FaceNormal:
        return self.plane.faceNormal

    @property
    def inversedFaceNormal(self) -> FaceNormal:
        return self.plane.inversedFaceNormal

    @property
    def min_x(self) -> float:
        return min([v.x for v in self.vertices])

    @property
    def max_x(self) -> float:
        return max([v.x for v in self.vertices])

    @property
    def min_y(self) -> float:
        return min([v.y for v in self.vertices])

    @property
    def max_y(self) -> float:
        return max([v.y for v in self.vertices])

    @property
    def min_z(self) -> float:
        return min([v.z for v in self.vertices])

    @property
    def max_z(self) -> float:
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

    def get_angle_type(self, other: Face) -> AngleType:
        cos = self.plane.normal.normalized.dotProduct(other.plane.normal.normalized)
        threshold = math.cos(89 * math.pi / 180)
        if cos < -threshold:
            return AngleType.SHARP
        if cos > threshold:
            return AngleType.OBTUSE
        return AngleType.ORTHOGONAL


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

    def __iter__(self):
        return iter(self.faces)

    def __len__(self):
        return len(self.faces)

    @property
    def min_x(self) -> float:
        return min([v.min_x for v in self.faces])

    @property
    def max_x(self) -> float:
        return max([v.max_x for v in self.faces])

    @property
    def min_y(self) -> float:
        return min([v.min_y for v in self.faces])

    @property
    def max_y(self) -> float:
        return max([v.max_y for v in self.faces])

    @property
    def min_z(self) -> float:
        return min([v.min_z for v in self.faces])

    @property
    def max_z(self) -> float:
        return max([v.max_z for v in self.faces])

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

    @property
    def indexedFaceNormals(self) -> dict[int, FaceNormal]:
        return {idx: face.faceNormal for idx, face in enumerate(self.faces)}

    def get_face_indices_by_facenormal(self, *args, strict=False) -> set[int]:
        """
        Get the indices of the faces with the given face normals
        Args:
            face_normal: FaceNormal to match
            strict: if this flag is set to true, the passed facenormal needs to be strictly equal to the facenormal of
            the face. If False, the passed FaceNormal needs to be 'in' the facenormal of the face.

        Returns:
            set of indices of the faces with the given face normals
        """
        for arg in args:
            assert isinstance(arg, FaceNormal)
        if strict:
            return {
                idx for idx, face in enumerate(self.faces) if face.faceNormal in args
            }
        else:
            idxs = set()
            args_normals = {iter_normal for arg in args for iter_normal in arg.split()}
            for idx, face in enumerate(self.faces):
                if len(set(args_normals).intersection(set(face.faceNormal.split()))):
                    idxs.add(idx)
            return idxs

    def get_faces_by_facenormal(self, *args, strict=False) -> list[Face]:
        return [
            self.faces[idx]
            for idx in self.get_face_indices_by_facenormal(*args, strict=strict)
        ]


class SliceInterval(BaseModel):
    min_x: float = None  # smaller
    max_x: float = None  # bigger
    min_y: float = None  # smaller
    max_y: float = None  # bigger
    min_z: float = None  # smaller
    max_z: float = None  # bigger
    model_config: ConfigDict = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )


@dataclass
class Slice:
    x: float = None
    y: float = None
    z: float = None

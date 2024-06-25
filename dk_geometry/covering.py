# Copyright: 2024 BV De Kastenman

from dk_geometry.general import calculate_signed_distance_to_plane, cut_face_by_plane
from dk_geometry.model import Face, Plane3d, Vector3d
from pydantic.dataclasses import dataclass
import math


@dataclass
class Rectangle:
    min_x: float
    max_x: float
    min_y: float
    max_y: float


def measure_range_of_faces(faces: list[Face], origin: Vector3d, direction: Vector3d):
    values = [(v - origin).dotProduct(direction) for f in faces for v in f.vertices]
    return min(values), max(values)


def get_bounding_rectangle(
    faces: list[Face], origin: Vector3d, x: Vector3d, y: Vector3d
) -> Rectangle:
    (min_x, max_x) = measure_range_of_faces(faces, origin, x)
    (min_y, max_y) = measure_range_of_faces(faces, origin, y)
    rectangle = Rectangle(
        min_x=min_x,
        max_x=max_x,
        min_y=min_y,
        max_y=max_y,
    )
    return rectangle


def make_rectangular_face(
    rectangle: Rectangle, origin: Vector3d, x: Vector3d, y: Vector3d
) -> Face:
    return Face(
        vertices=[
            origin + x * rectangle.min_x + y * rectangle.min_y,
            origin + x * rectangle.max_x + y * rectangle.min_y,
            origin + x * rectangle.max_x + y * rectangle.max_y,
            origin + x * rectangle.min_x + y * rectangle.max_y,
        ]
    )


def is_face_behind_plane(face: Face, plane: Plane3d, tolerance: float) -> bool:
    return all(
        [
            calculate_signed_distance_to_plane(v, plane) < tolerance
            for v in face.vertices
        ]
    )


def cover_faces(faces: list[Face]) -> Face:
    """
    Will cover the provided faces with one big convex face (without
    inner corners). The input faces must be in one plane. The added
    edges will be vertical/horizontal, the edges of the input faces
    will be extended where appropriate.
    """
    for face1 in faces:
        normal1 = face1.plane.normal
        for face2 in faces:
            normal2 = face2.plane.normal
            if math.fabs(normal1.dotProduct(normal2)) < 0.9:
                raise ValueError("cover_faces: the input faces have different normals")
    origin = faces[0].vertices[0]
    plane_normal = faces[0].plane.normal
    y = Vector3d(0, 1, 0)
    x = y.crossProduct(plane_normal)
    brect = get_bounding_rectangle(faces, origin, x, y)
    result = make_rectangular_face(brect, origin, x, y)
    for face in faces:
        for edge_index in range(len(face.vertices)):
            edge = face.get_edge(edge_index)
            cutting_plane = Plane3d(
                origin=edge[0], normal=(edge[1] - edge[0]).crossProduct(plane_normal)
            )
            if is_face_behind_plane(result, cutting_plane, 0.01):
                continue  # the edge is already on the edge of the rectangle
            can_cut = all([is_face_behind_plane(f, cutting_plane, 0.01) for f in faces])
            if not can_cut:
                continue  # cutting by this edge would cut some input faces
            result = cut_face_by_plane(result, cutting_plane, {}, {})
    return result

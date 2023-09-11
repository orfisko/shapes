from __future__ import annotations

from pydantic import ConfigDict

from dk_geometry.model import Vector3d, Plane3d, Line3d, Face, Polyhedron

default_config = dict(
    slots=True,
    config=ConfigDict(validate_assignment=True, arbitrary_types_allowed=True),
)


def calculate_contour_normal(points: list[Vector3d]):
    sum = Vector3d(0, 0, 0)
    for index in range(len(points)):
        next = (index + 1) % len(points)
        sum += points[index].crossProduct(points[next])
    return sum / sum.length


def compute_line_plane_intersection(line: Line3d, plane: Plane3d) -> Vector3d:
    # P=line.origin+t*line.direction
    # (P-plane.origin).dot(plane.normal)=0
    # (line.origin+t*line.direction-plane.origin).dot(plane.normal)=0
    # t*line.direction.dot(plane.normal)=(plane.origin-line.origin).dot(plane.normal)
    # t=(plane.origin-line.origin).dot(plane.normal)/line.direction.dot(plane.normal)
    t = (plane.origin - line.origin).dotProduct(
        plane.normal
    ) / line.direction.dotProduct(plane.normal)
    return line.origin + line.direction * t


def compute_two_planes_intersection(plane1: Plane3d, plane2: Plane3d) -> Line3d:
    line_direction = plane1.normal.crossProduct(plane2.normal).normalized
    line_position = compute_line_plane_intersection(
        Line3d(plane1.origin, line_direction.crossProduct(plane1.normal).normalized),
        plane2,
    )
    return Line3d(line_position, line_direction)


def compute_three_planes_intersection(
    plane1: Plane3d, plane2: Plane3d, plane3: Plane3d
) -> Vector3d:
    return compute_line_plane_intersection(
        compute_two_planes_intersection(plane1, plane2), plane3
    )


def calculate_signed_distance_to_plane(
    point: Vector3d, plane: Plane3d
) -> float:
    return (point - plane.origin).dotProduct(plane.normal.normalized)


def calculate_polyhedron_signed_volume(polyhedron: Polyhedron) -> float:
    volume = 0
    for face in polyhedron.faces:
        for index in range(len(face.vertices)-2):
            a = face.vertices[index]
            b = face.vertices[index+1]
            c = face.vertices[index+2]
            volume += a.crossProduct(b).dotProduct(c)
    return volume


def make_polyhedron_between_faces(
    outer_face_contour: List[Vector3d], inner_face_contour: List[Vector3d]
) -> Polyhedron:
    if len(outer_face_contour) != len(inner_face_contour):
        raise ValueError(
            "make_plate: outer and inner contours have different number of vertices"
        )
    result = Polyhedron(faces=[])
    result.faces.append(Face(vertices=outer_face_contour))
    for edge_index in range(len(outer_face_contour)):
        next_index = (edge_index + 1) % len(outer_face_contour)
        result.faces.append(
            Face(
                vertices=[
                    outer_face_contour[next_index],
                    outer_face_contour[edge_index],
                    inner_face_contour[edge_index],
                    inner_face_contour[next_index],
                ]
            )
        )
    result.faces.append(Face(vertices=inner_face_contour[::-1]))
    return result


def make_plate(face: Face, offset: float) -> Polyhedron:
    if offset<0:
        return make_plate(Face(vertices = face.vertices[::-1]), -offset)
    shift = face.plane.normal.normalized * offset
    shifted_face = Face(vertices=[v+shift for v in face.vertices])
    return make_polyhedron_between_faces(shifted_face.vertices, face.vertices)

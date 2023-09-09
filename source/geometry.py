from __future__ import annotations

from pydantic import ConfigDict

from source.model import Vector3d, Plane3d, Line3d

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

# Copyright: 2024 BV De Kastenman
from __future__ import annotations

from typing import Optional

from pydantic import ConfigDict

from dk_geometry.model import Vector3d, Plane3d, Line3d, Face, Polyhedron

default_config = dict(
    slots=True,
    config=ConfigDict(validate_assignment=True, arbitrary_types_allowed=True),
)


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


def calculate_signed_distance_to_plane(point: Vector3d, plane: Plane3d) -> float:
    return (point - plane.origin).dotProduct(plane.normal.normalized)


def make_polyhedron_between_faces(
    outer_face_contour: list[Vector3d], inner_face_contour: list[Vector3d]
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


def extrude_polyhedron_from_face(face: Face, offset: float) -> Polyhedron:
    if offset < 0:
        return extrude_polyhedron_from_face(Face(vertices=face.vertices[::-1]), -offset)
    # avoid reusing the input vertices
    face = Face(vertices=[Vector3d(v.x, v.y, v.z) for v in face.vertices])
    shift = face.plane.normal.normalized * offset
    shifted_face = Face(vertices=[v + shift for v in face.vertices])
    return make_polyhedron_between_faces(shifted_face.vertices, face.vertices)


def create_cube(centre: Vector3d, size: float) -> Polyhedron:
    v = [
        centre + Vector3d(-1, -1, -1) * size / 2,
        centre + Vector3d(1, -1, -1) * size / 2,
        centre + Vector3d(-1, 1, -1) * size / 2,
        centre + Vector3d(1, 1, -1) * size / 2,
        centre + Vector3d(-1, -1, 1) * size / 2,
        centre + Vector3d(1, -1, 1) * size / 2,
        centre + Vector3d(-1, 1, 1) * size / 2,
        centre + Vector3d(1, 1, 1) * size / 2,
    ]
    return Polyhedron(
        faces=[
            Face(vertices=[v[0], v[2], v[3], v[1]]),  # front
            Face(vertices=[v[2], v[6], v[7], v[3]]),  # top
            Face(vertices=[v[6], v[4], v[5], v[7]]),  # back
            Face(vertices=[v[4], v[0], v[1], v[5]]),  # bottom
            Face(vertices=[v[1], v[3], v[7], v[5]]),  # right
            Face(vertices=[v[2], v[0], v[4], v[6]]),  # left
        ]
    )


def cut_face_by_plane(
    face: Face,
    plane: Plane3d,
    vertex_is_behind_cache: Optional[dict[int, bool]] = None,
    edge_split_vertices_cache: Optional[dict[(int, int), Vector3d]] = None,
) -> Face:
    """
    Returns the part of the given face which is behind (on the negative side) of
    the given plane. It may be the whole face if it's completely behind. It may
    be an empty face (without vertices) if it's completely in front.
    Will fail if the plane cuts the face in more than two vertices.
    No new objects is created for the vertices behind the plane.

    vertex_is_behind_cache and edge_split_vertices_cache are to ensure consistency
    of vertex connections within a polyhedron, not needed if only a geometry of a
    single cuut face is needed.
    """
    if vertex_is_behind_cache is None:
        vertex_is_behind_cache = {}
    if edge_split_vertices_cache is None:
        edge_split_vertices_cache = {}

    def is_vertex_behind(vertex):
        if id(vertex) not in vertex_is_behind_cache:
            behind = calculate_signed_distance_to_plane(vertex, plane) < 0
            vertex_is_behind_cache[id(vertex)] = behind
        return vertex_is_behind_cache[id(vertex)]

    def get_edge_splitting_vertex(v1: Vector3d, v2: Vector3d) -> Vector3d:
        key = (id(v1), id(v2))
        if key not in edge_split_vertices_cache:
            distance1 = calculate_signed_distance_to_plane(v1, plane)
            distance2 = calculate_signed_distance_to_plane(v2, plane)
            position = v1 + (v2 - v1) * (-distance1 / (distance2 - distance1))
            edge_split_vertices_cache[key] = position
            inverted_key = (id(v2), id(v1))
            edge_split_vertices_cache[inverted_key] = position
        return edge_split_vertices_cache[key]

    if all([is_vertex_behind(v) for v in face.vertices]):
        return face
    if not any([is_vertex_behind(v) for v in face.vertices]):
        return Face(vertices=[])
    front_to_back = []  # edges which go from the cut area to the uncut one
    for edge_index in range(len(face.vertices)):
        start = face.vertices[edge_index]
        finish = face.vertices[(edge_index + 1) % len(face.vertices)]
        if not is_vertex_behind(start) and is_vertex_behind(finish):
            front_to_back.append(edge_index)
    if len(front_to_back) != 1:
        raise ValueError("a face is cut more than once by a plane")
    vertices = (
        face.vertices[front_to_back[0] :]
        + face.vertices[: front_to_back[0]]
        + [face.vertices[front_to_back[0]]]
    )
    while not is_vertex_behind(vertices[-2]):
        vertices.pop(len(vertices) - 1)
    vertices[0] = get_edge_splitting_vertex(vertices[0], vertices[1])
    vertices[-1] = get_edge_splitting_vertex(vertices[-2], vertices[-1])
    return Face(vertices=vertices)


def find_hole_in_polyhedron(polyhedron: Polyhedron) -> list[Vector3d]:
    """
    Finds a hole in the polyhedron suurface or returns an empty list.
    If the polyhedron has multiple holes, an arbitrary one will be returned.
    """
    edges = {}  # (id(start),id(finish))->(start,finish)
    for face in polyhedron.faces:
        for index in range(len(face.vertices)):
            start = face.vertices[index]
            finish = face.vertices[(index + 1) % len(face.vertices)]
            if (id(finish), id(start)) in edges:
                del edges[(id(finish), id(start))]
            else:
                edges[(id(start), id(finish))] = (start, finish)
    if len(edges) == 0:
        return []
    connections = {}
    for ids, vertices in edges.items():
        connections[ids[0]] = vertices[1]
    hole = [next(iter(connections.values()))]
    while True:
        next_vertex = connections[id(hole[-1])]
        if next_vertex is hole[0]:
            break
        hole.append(next_vertex)
    return hole[::-1]


def cut_polyhedron_by_plane(polyhedron: Polyhedron, plane: Plane3d) -> Polyhedron:
    """
    Will leave only the part on the side inverse to the normal of the plane.
    Will fail if the polyhedron is cut in two non-connected places.
    Will fail if one of the faces is cut in two places.
    Args:
        polyhedron: polyedron to cut
        plane: plane to cut with
    Returns:
        Will return a polyhedron without faces if it's completely in front of the plane.
        Treats the polyhedron as a solid, so will close the hole made by the cut.
    """
    vertex_is_behind_cache = {}
    edge_split_vertices_cache = {}
    cut_faces = []
    for face in polyhedron.faces:
        cut_face = cut_face_by_plane(
            face, plane, vertex_is_behind_cache, edge_split_vertices_cache
        )
        if len(cut_face.vertices) > 0:
            cut_faces.append(cut_face)
    hole = find_hole_in_polyhedron(Polyhedron(faces=cut_faces))
    if len(hole) > 0:
        cut_faces.append(Face(vertices=hole))
    return Polyhedron(faces=cut_faces)


def get_adjacent_faces(polyhedron: Polyhedron, reference_face_index: int) -> list[int]:
    edge_to_face_index = {}
    for face_index, face in enumerate(polyhedron.faces):
        for edge_index in range(len(face.vertices)):
            edge = face.get_edge(edge_index)
            key = (id(edge[0]), id(edge[1]))
            edge_to_face_index[key] = face_index
    reference_face = polyhedron.faces[reference_face_index]
    neighbours = []
    for edge_index in range(len(reference_face.vertices)):
        edge = reference_face.get_edge(edge_index)
        inverted_edge = (edge[1], edge[0])
        key = (id(inverted_edge[0]), id(inverted_edge[1]))
        if key in edge_to_face_index:
            neighbours.append(edge_to_face_index.get(key))
    return neighbours

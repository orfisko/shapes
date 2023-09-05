from _decimal import Decimal
from collections import defaultdict
from typing import Optional, DefaultDict, List

from model import Polyhedron, Vertex, Face
from geometry import *


def deep_copy(polyhedron: Polyhedron) -> Polyhedron:
    vertex_copies = {}
    for face in polyhedron.faces:
        for vertex in face.vertices:
            if not (id(vertex) in vertex_copies):
                vertex_copies[id(vertex)] = Vertex(vertex.x, vertex.y, vertex.z)
    return Polyhedron(
        faces=[
            Face(vertices=[vertex_copies[id(v)] for v in face.vertices])
            for face in polyhedron.faces
        ]
    )


def compute_face_plane(face: Face):
    return Plane3d(
        origin=face.vertices[0].vector(),
        normal=calculate_contour_normal([v.vector() for v in face.vertices]),
    )


def apply_offset(
    polyhedron: Polyhedron,
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
            for loc in range(0, len(polyhedron.faces))
            if loc not in offset_map.keys()
        }
    )

    offset_poly = deep_copy(polyhedron)

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
            plane = compute_face_plane(polyhedron.faces[face_index])
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

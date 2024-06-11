import math
from _decimal import Decimal
from collections import defaultdict
from copy import deepcopy
from typing import DefaultDict, List

from dk_geometry.general import *
from dk_geometry.model import Face, Polyhedron


def are_faces_different(face1: Face, face2: Face, tolerance: float) -> bool:
    distance = calculate_signed_distance_to_plane(face2.vertices[0], face1.plane)
    return math.fabs(distance) > tolerance


def swap_list_elements(list, index1, index2):
    if index1 != index2:
        list[index1], list[index2] = list[index2], list[index1]


def put_value_at_start(list, value):
    swap_list_elements(list, 0, list.index(value))


def find_common_edge_direction(face1: Face, face2: Face) -> Vector3d:
    for edge_index in range(len(face1.vertices)):
        edge = face1.get_edge(edge_index)
        if not (edge[0] in face2.vertices):
            continue
        if not (edge[1] in face2.vertices):
            continue
        return edge[1] - edge[0]
    raise ValueError("find_common_edge_direction: the given faces are not adjacent")


def is_angle_internal(face1: Face, face2: Face) -> bool:
    normal1 = face1.plane.normal
    normal2 = face2.plane.normal
    edge = find_common_edge_direction(face1, face2)
    return normal1.crossProduct(normal2).dotProduct(edge) > 0


def is_face_corner_concave(face: Face, corner_index: int) -> bool:
    normal = face.plane.normal
    previous_index = (corner_index - 1) % len(face.vertices)
    next_index = (corner_index + 1) % len(face.vertices)
    previous_vector = face.vertices[corner_index] - face.vertices[previous_index]
    next_vector = face.vertices[next_index] - face.vertices[corner_index]
    return previous_vector.crossProduct(next_vector).dotProduct(normal) < 0


def select_inner_vertex_position(
    outer_polyhedron: Polyhedron,
    inner_polyhedron: Polyhedron,
    face_indices: [int],  # the active face is the first one
    priorities: [int],
) -> Vector3d:
    """
    Prefers inner planes, but cuts through panels with lower priority
    """
    planes = [inner_polyhedron.faces[face_indices[0]].plane]
    for c in range(1, 3):
        surface = inner_polyhedron
        invertor = 1
        if is_angle_internal(
            outer_polyhedron.faces[face_indices[0]],
            outer_polyhedron.faces[face_indices[c]],
        ):
            invertor = -1
        if priorities[0] == 1000:
            if invertor == -1:
                surface = outer_polyhedron
            else:
                surface = inner_polyhedron
        elif priorities[c] * invertor > priorities[0] * invertor:
            surface = outer_polyhedron
        planes.append(surface.faces[face_indices[c]].plane)
    return compute_three_planes_intersection(planes[0], planes[1], planes[2])


def select_outer_vertex_position(
    outer_polyhedron: Polyhedron,
    inner_polyhedron: Polyhedron,
    face_indices: [int],  # the active face is the first one
    priorities: [int],
) -> Vector3d:
    """
    Prefers inner planes, but cuts through panels with lower priority
    """
    planes = [outer_polyhedron.faces[face_indices[0]].plane]
    for c in range(1, 3):
        surface = outer_polyhedron
        invertor = 1
        if is_angle_internal(
            outer_polyhedron.faces[face_indices[0]],
            outer_polyhedron.faces[face_indices[c]],
        ):
            invertor = -1
        if priorities[0] == 1000:
            if invertor == -1:
                surface = outer_polyhedron
            else:
                surface = inner_polyhedron
        elif priorities[c] * invertor < priorities[0] * invertor:
            surface = inner_polyhedron
        planes.append(surface.faces[face_indices[c]].plane)
    return compute_three_planes_intersection(planes[0], planes[1], planes[2])


def generate_offset(
    poly: Polyhedron,
    offset: Optional[float] = None,
    offset_map: Optional[dict[int, float]] = None,
) -> Polyhedron:
    """
    Generates a new polyhedron with the offset applied to the vertices. The offset is applied to all faces unless
    an offset_map is supplied. The offset_map is a dictionary with the face index as key and the offset as value.
    Args:
        poly: polyehedron to offset
        offset: global offset for all faces, defaults to 0 if offset_map is supplied
        offset_map: offset to apply on the face with the specified index as key. Missing values are filled with the
            offset value

    Returns:
        a new polyhedron with the offset applied
    """
    from .general import compute_three_planes_intersection

    if not any((offset, offset_map)):
        raise ValueError("Either offset or offset_map needs to be supplied")
    if offset_map is None:
        offset_map = dict()
    if offset is None:
        offset = 0
    # Fill the offset_map with the offset if it is not supplied.
    offset_map.update(
        {
            loc: offset
            for loc in range(0, len(poly.faces))
            if loc not in offset_map.keys()
        }
    )

    offset_poly = deepcopy(poly)

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
            plane = poly.faces[face_index].plane
            face_offset = float(offset_map[face_index])
            plane.origin += plane.normal.normalized * face_offset
            planes.append(plane)
        new_position = compute_three_planes_intersection(
            planes[0], planes[1], planes[2]
        )
        vertex.x = round(new_position.x, 1)
        vertex.y = round(new_position.y, 1)
        vertex.z = round(new_position.z, 1)
    for index in range(len(poly.faces)):
        original_normal = poly.faces[index].plane.normal
        offset_normal = offset_poly.faces[index].plane.normal
        if original_normal.dotProduct(offset_normal) < 0:
            raise ValueError("offset completely removed one face")
    return offset_poly


def generate_delta_polyhedra(
    outer_polyhedron: Polyhedron, inner_polyhedron: Polyhedron, prioritizer
) -> dict[int, Polyhedron]:
    """
    Generates panel shapes using inner and outer polyhedrons. They should have
    faces/vertices in the same order and of the same number.
    Args:
        outer_polyhedron:
        inner_polyhedron:
        prioritizer: priotization function to decide which panel takes precedence over the other.
            priority 1000 means that the face won't be cut no matter what priorities the other faces have
    Returns:
         Dictionary[face_index, panel], only for faces with some offset
    """
    vertex_id_to_face_indices: DefaultDict[int, List[int]] = defaultdict(list)
    for face_index in range(len(outer_polyhedron.faces)):
        for vertex in outer_polyhedron.faces[face_index].vertices:
            vertex_id_to_face_indices[id(vertex)].append(face_index)
    face_has_offset = [
        are_faces_different(
            outer_polyhedron.faces[index], inner_polyhedron.faces[index], 0.01
        )
        for index in range(len(inner_polyhedron.faces))
    ]
    panels = {}
    for face_index in range(len(inner_polyhedron.faces)):
        if not face_has_offset[face_index]:
            continue
        outer = outer_polyhedron.faces[face_index].vertices[:]
        inner = inner_polyhedron.faces[face_index].vertices[:]
        for vertex_index in range(len(outer)):
            adjacent_face_indices = vertex_id_to_face_indices[id(outer[vertex_index])]
            put_value_at_start(adjacent_face_indices, face_index)
            priorities = []
            if not face_has_offset[
                adjacent_face_indices[1]
            ]:  # make suure that all panel-less faces are at the end
                swap_list_elements(adjacent_face_indices, 1, 2)
            if not face_has_offset[adjacent_face_indices[1]]:
                # no real need to compare faces - only one of them will get a panel
                priorities = [1, 1, 1]
            elif not face_has_offset[adjacent_face_indices[2]]:
                # only two faces get panels, prioritize them and give something non-conflicting to the third one
                priorities = prioritizer(adjacent_face_indices[0:2])
                priorities.append(priorities[1])
            else:
                priorities = prioritizer(adjacent_face_indices)
            current_priority = priorities[0]
            if is_face_corner_concave(outer_polyhedron.faces[face_index], vertex_index):
                if (
                    priorities[1] <= current_priority
                    or priorities[2] <= current_priority
                ):
                    if priorities[1] != priorities[2]:
                        raise ValueError(
                            f"generate_panel_shapes: priorities on concave corner #{vertex_index} require to make a cut into face #{face_index}"
                        )
            # inner
            inner[vertex_index] = select_inner_vertex_position(
                outer_polyhedron,
                inner_polyhedron,
                adjacent_face_indices,
                priorities,
            )
            # outer
            outer[vertex_index] = select_outer_vertex_position(
                outer_polyhedron,
                inner_polyhedron,
                adjacent_face_indices,
                priorities,
            )
        panels[face_index] = make_polyhedron_between_faces(outer, inner)
    return panels

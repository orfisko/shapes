from collections import defaultdict
from typing import DefaultDict, List

from source.general import *
from source.model import Face, Polyhedron

import math


def make_plate(
    outer_face_contour: List[Vector3d], inner_face_contour: List[Vector3d]
) -> Polyhedron:
    if len(outer_face_contour) != len(inner_face_contour):
        raise ValueError(
            "make_plate: outer and inner contours have different number of vertices"
        )
    result = Polyhedron(faces=[])
    result.faces.append(Face(vectors=outer_face_contour))
    for edge_index in range(len(outer_face_contour)):
        next_index = (edge_index + 1) % len(outer_face_contour)
        result.faces.append(
            Face(
                vectors=[
                    outer_face_contour[next_index],
                    outer_face_contour[edge_index],
                    inner_face_contour[edge_index],
                    inner_face_contour[next_index],
                ]
            )
        )
    result.faces.append(Face(vectors=inner_face_contour[::-1]))
    return result


def make_vertex(position: Vector3d) -> Vector3d:
    return Vector3d(position.x, position.y, position.z)


def are_faces_different(face1: Face, face2: Face, tolerance: float) -> bool:
    distance = calculate_signed_distance_to_plane(face2.vectors[0], face1.plane)
    return math.fabs(distance) > tolerance


def swap_list_elements(list, index1, index2):
    if index1 != index2:
        list[index1], list[index2] = list[index2], list[index1]


def put_value_at_start(list, value):
    swap_list_elements(list, 0, list.index(value))


def find_common_edge_direction(face1: Face, face2: Face) -> Vector3d:
    for edge_index in range(len(face1.vectors)):
        edge_start = face1.vectors[edge_index]
        edge_finish = face1.vectors[(edge_index + 1) % len(face1.vectors)]
        if not (edge_start in face2.vectors):
            continue
        if not (edge_finish in face2.vectors):
            continue
        return edge_finish - edge_start
    raise ValueError("find_common_edge_direction: the given faces are not adjacent")


def is_angle_internal(face1: Face, face2: Face) -> bool:
    normal1 = face1.plane.normal
    normal2 = face2.plane.normal
    edge = find_common_edge_direction(face1, face2)
    return normal1.crossProduct(normal2).dotProduct(edge) > 0


def is_face_corner_concave(face: Face, corner_index: int) -> bool:
    normal = face.plane.normal
    previous_index = (corner_index - 1) % len(face.vectors)
    next_index = (corner_index + 1) % len(face.vectors)
    previous_vector = face.vectors[corner_index] - face.vectors[previous_index]
    next_vector = face.vectors[next_index] - face.vectors[corner_index]
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
        if priorities[c] * invertor > priorities[0] * invertor:
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
        if priorities[c] * invertor < priorities[0] * invertor:
            surface = inner_polyhedron
        planes.append(surface.faces[face_indices[c]].plane)
    return compute_three_planes_intersection(planes[0], planes[1], planes[2])


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
    Returns:
         Dictionary[face_index, panel], only for faces with some offset
    """
    vertex_id_to_face_indices: DefaultDict[int, List[int]] = defaultdict(list)
    for face_index in range(len(outer_polyhedron.faces)):
        for vertex in outer_polyhedron.faces[face_index].vectors:
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
        outer = outer_polyhedron.faces[face_index].vectors[:]
        inner = inner_polyhedron.faces[face_index].vectors[:]
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
        panels[face_index] = make_plate(outer, inner)
    return panels

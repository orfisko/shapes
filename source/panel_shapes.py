from collections import defaultdict
from typing import DefaultDict, List

from source.geometry import *
from source.model import Vertex, Face, Polyhedron

import math


def make_plate(
    outer_face_contour: List[Vertex], inner_face_contour: List[Vertex]
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


def make_vertex(position: Vector3d) -> Vertex:
    return Vertex(position.x, position.y, position.z)


def are_faces_different(face1: Face, face2: Face, tolerance: float) -> bool:
    plane1 = face1.plane
    distance = (face2.vertices[0].vector - plane1.origin).dotProduct(
        plane1.normal.normalized
    )
    return math.fabs(distance) > tolerance


def put_value_at_start(list, value):
    index = list.index(value)
    if index != 0:
        list[0], list[index] = list[index], list[0]
    return list


def find_common_edge_direction(face1: Face, face2: Face) -> Vector3d:
    for edge_index in range(len(face1.vertices)):
        edge_start = face1.vertices[edge_index]
        edge_finish = face1.vertices[(edge_index + 1) % len(face1.vertices)]
        if not (edge_start in face2.vertices):
            continue
        if not (edge_finish in face2.vertices):
            continue
        return edge_finish.vector - edge_start.vector
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
    previous_vector = (
        face.vertices[corner_index].vector - face.vertices[previous_index].vector
    )
    next_vector = face.vertices[next_index].vector - face.vertices[corner_index].vector
    return previous_vector.crossProduct(next_vector).dotProduct(normal) < 0


def generate_panel_shapes(
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
            planes = [inner_polyhedron.faces[face_index].plane]
            for c in range(1, 3):
                surface = inner_polyhedron
                invertor = 1
                if is_angle_internal(
                    outer_polyhedron.faces[face_index],
                    outer_polyhedron.faces[adjacent_face_indices[c]],
                ):
                    invertor = -1
                if priorities[c] * invertor > current_priority * invertor:
                    surface = outer_polyhedron
                planes.append(surface.faces[adjacent_face_indices[c]].plane)
            inner[vertex_index] = make_vertex(
                compute_three_planes_intersection(planes[0], planes[1], planes[2])
            )
            # outer
            planes = [outer_polyhedron.faces[face_index].plane]
            for c in range(1, 3):
                surface = outer_polyhedron
                invertor = 1
                if is_angle_internal(
                    outer_polyhedron.faces[face_index],
                    outer_polyhedron.faces[adjacent_face_indices[c]],
                ):
                    invertor = -1
                if priorities[c] * invertor < current_priority * invertor:
                    surface = inner_polyhedron
                planes.append(surface.faces[adjacent_face_indices[c]].plane)
            outer[vertex_index] = make_vertex(
                compute_three_planes_intersection(planes[0], planes[1], planes[2])
            )
        panels[face_index] = make_plate(outer, inner)
    return panels

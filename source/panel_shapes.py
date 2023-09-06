from _decimal import Decimal
from collections import defaultdict
from typing import Optional, DefaultDict, List

from source.model import Polyhedron, Vertex, Face
from source.geometry import *


def make_plate(
    outer_face_contour: [Vertex],
    inner_face_contour: [Vertex]
) -> Polyhedron:
    if len(outer_face_contour)!=len(inner_face_contour):
        raise ValueError("make_plate: outer and inner contours have different number of vertices")
    result=Polyhedron(faces=[])
    result.faces.append(Face(vertices=outer_face_contour))
    for edge_index in range(len(outer_face_contour)):
        next_index=(edge_index+1)%len(outer_face_contour)
        result.faces.append(Face(vertices=[
            outer_face_contour[next_index],
            outer_face_contour[edge_index],
            inner_face_contour[edge_index],
            inner_face_contour[next_index]]))
    result.faces.append(Face(vertices=inner_face_contour[::-1]))
    return result
def compute_face_plane(face: Face):
    return Plane3d(
        origin=face.vertices[0].vector(),
        normal=calculate_contour_normal([v.vector() for v in face.vertices]),
    )
def make_vertex(position: Vector3d)->Vertex:
    return Vertex(position.x,position.y,position.z)
def generate_panel_shapes(
    outer_polyhedron: Polyhedron,
    inner_polyhedron: Polyhedron,
) -> [Polyhedron]:
    """
    Generates panel shapes using inner and outer polyhedrons. They should have
    faces/vertices in the same order and of the same number.
    Returns a list of generated panels in the same order as faces in the
    polyhedrons.
    """
    vertex_id_to_face_indices:DefaultDict[int,List[int]]=defaultdict(list)
    for face_index in range(len(outer_polyhedron.faces)):
        for vertex in outer_polyhedron.faces[face_index].vertices:
            vertex_id_to_face_indices[id(vertex)].append(face_index)
    panels=[]
    for face_index in range(len(inner_polyhedron.faces)):
        outer=outer_polyhedron.faces[face_index].vertices[:]
        inner=inner_polyhedron.faces[face_index].vertices[:]
        for vertex_index in range(len(outer)):
            adjacent_face_indices=vertex_id_to_face_indices[id(outer[vertex_index])]
            adjacent_face_indices.sort()
            main_face_inner_vertex=make_vertex(compute_three_planes_intersection(
                compute_face_plane(inner_polyhedron.faces[adjacent_face_indices[0]]),
                compute_face_plane(outer_polyhedron.faces[adjacent_face_indices[1]]),
                compute_face_plane(outer_polyhedron.faces[adjacent_face_indices[2]])))
            secondary_face_inner_vertex=make_vertex(compute_three_planes_intersection(
                compute_face_plane(inner_polyhedron.faces[adjacent_face_indices[0]]),
                compute_face_plane(inner_polyhedron.faces[adjacent_face_indices[1]]),
                compute_face_plane(outer_polyhedron.faces[adjacent_face_indices[2]])))
            if face_index==adjacent_face_indices[0]:
                inner[vertex_index]=main_face_inner_vertex
            elif face_index==adjacent_face_indices[1]:
                outer[vertex_index]=main_face_inner_vertex
                inner[vertex_index]=secondary_face_inner_vertex
            else:
                outer[vertex_index]=secondary_face_inner_vertex
        panels.append(make_plate(outer,inner))
    return panels

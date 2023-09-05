from _decimal import Decimal
from collections import defaultdict
from typing import Optional, DefaultDict, List

from source.model import Polyhedron, Vertex, Face
from source.geometry import *


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
    panels=[]
    for face_index in range(len(inner_polyhedron.faces)):
        outer_face=outer_polyhedron.faces[face_index]
        inner_face=inner_polyhedron.faces[face_index]
        panel=Polyhedron(faces=[])
        panel.faces.append(outer_face)
        for edge_index in range(len(outer_face.vertices)):
            next_index=(edge_index+1)%len(outer_face.vertices)
            panel.faces.append(Face(vertices=[
                outer_face.vertices[next_index],
                outer_face.vertices[edge_index],
                inner_face.vertices[edge_index],
                inner_face.vertices[next_index]]))
        panel.faces.append(Face(vertices=inner_face.vertices[::-1]))
        panels.append(panel)
    return panels

from dk_geometry.covering import cover_faces
from dk_geometry.model import Face, Polyhedron, Vector3d
import pytest


def are_faces_equal(face1: Face, face2: Face) -> bool:
    tolerance = 0.01
    if len(face1.vertices)!=len(face2.vertices):
        return False
    vertex_count = len(face1.vertices)
    for shift in range(vertex_count):
        equal = True
        for index in range(vertex_count):
            vertex1 = face1.vertices[index]
            vertex2 = face2.vertices[(index+shift) % vertex_count]
            if (vertex1 - vertex2).length > tolerance:
                equal = False
        if equal:
            return True
    return False


def test_that_single_convex_face_is_not_changed():
    input = Face(
        vertices=[
            Vector3d(0, 0, 0),
            Vector3d(2, 0, 0),
            Vector3d(1, 1, 0)
        ]
    )
    assert are_faces_equal(cover_faces([input]), input)

def test_that_inner_corner_is_filled():
    input = Face(
        vertices=[
            Vector3d(0, 0, 0),
            Vector3d(2, 0, 0),
            Vector3d(2, 2, 0),
            Vector3d(1, 2, 0),
            Vector3d(1, 1, 0),
            Vector3d(0, 1, 0),
        ]
    )
    expected = Face(
        vertices=[
            Vector3d(0, 0, 0),
            Vector3d(2, 0, 0),
            Vector3d(2, 2, 0),
            Vector3d(0, 2, 0),
        ]
    )
    assert are_faces_equal(cover_faces([input]), expected)

def test_that_two_rectangles_are_covered_with_one_rectangle():
    input1 = Face(
        vertices=[
            Vector3d(0, 0, 0),
            Vector3d(1, 0, 0),
            Vector3d(1, 1, 0),
            Vector3d(0, 1, 0),
        ]
    )
    input2 = Face(
        vertices=[
            Vector3d(2, 2, 0),
            Vector3d(3, 2, 0),
            Vector3d(3, 3, 0),
            Vector3d(2, 3, 0),
        ]
    )
    expected = Face(
        vertices=[
            Vector3d(0, 0, 0),
            Vector3d(3, 0, 0),
            Vector3d(3, 3, 0),
            Vector3d(0, 3, 0),
        ]
    )
    assert are_faces_equal(cover_faces([input1, input2]), expected)

def test_that_a_sloped_edge_can_cut():
    input1 = Face(
        vertices=[
            Vector3d(0, 0, 0),
            Vector3d(1, 0, 0),
            Vector3d(1, 1, 0),
            Vector3d(0, 1, 0),
        ]
    )
    input2 = Face(
        vertices=[
            Vector3d(2, 2, 0),
            Vector3d(3, 2, 0),
            Vector3d(2, 3, 0),
        ]
    )
    expected = Face(
        vertices=[
            Vector3d(0, 0, 0),
            Vector3d(3, 0, 0),
            Vector3d(3, 2, 0),
            Vector3d(2, 3, 0),
            Vector3d(0, 3, 0),
        ]
    )
    assert are_faces_equal(cover_faces([input1, input2]), expected)

def test_that_a_sloped_edge_cannot_cut_through():
    input1 = Face(
        vertices=[
            Vector3d(0, 0, 0),
            Vector3d(3, 0, 0),
            Vector3d(3, 1, 0),
            Vector3d(0, 1, 0),
        ]
    )
    input2 = Face(
        vertices=[
            Vector3d(1, 1, 0),
            Vector3d(2, 1, 0),
            Vector3d(1, 2, 0),
        ]
    )
    expected = Face(
        vertices=[
            Vector3d(0, 0, 0),
            Vector3d(3, 0, 0),
            Vector3d(3, 2, 0),
            Vector3d(0, 2, 0),
        ]
    )
    assert are_faces_equal(cover_faces([input1, input2]), expected)

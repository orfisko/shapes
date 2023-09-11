from dk_geometry.general import calculate_signed_distance_to_plane, cut_face_by_plane
from dk_geometry.model import Face, Plane3d, Polyhedron, Vector3d
import math

def make_xy_square(width: float, height: float) -> Face:
    return Face(
        vertices=[
            Vector3d(0,0,0),
            Vector3d(width,0,0),
            Vector3d(width,height,0),
            Vector3d(0,height,0)
        ]
    )


def test_that_a_face_behind_the_plane_is_unchanged():
    face = make_xy_square(10, 10)
    plane = Plane3d(origin=Vector3d(20,0,0), normal=Vector3d(1,0,0))
    cut_face = cut_face_by_plane(face, plane, {}, {})
    assert face.vertices==cut_face.vertices


def test_that_a_face_in_front_of_the_plane_becomes_empty():
    face = make_xy_square(10, 10)
    plane = Plane3d(origin=Vector3d(-10,0,0), normal=Vector3d(1,0,0))
    cut_face = cut_face_by_plane(face, plane, {}, {})
    assert len(cut_face.vertices)==0


def test_that_vertices_behind_the_plane_are_the_same_objects():
    face = make_xy_square(10, 10)
    plane = Plane3d(origin=Vector3d(8,8,0), normal=Vector3d(1,1,0).normalized)
    cut_face = cut_face_by_plane(face, plane, {}, {})
    for original_vertex in face.vertices:
        if calculate_signed_distance_to_plane(original_vertex, plane)<=0:
            assert original_vertex in cut_face.vertices
        else:
            assert original_vertex not in cut_face.vertices


def test_that_the_cut_face_is_behind_the_plane_and_touches_it():
    face = make_xy_square(10, 10)
    plane = Plane3d(origin=Vector3d(8,8,0), normal=Vector3d(1,1,0).normalized)
    cut_face = cut_face_by_plane(face, plane, {}, {})
    parameters = [calculate_signed_distance_to_plane(v, plane) for v in cut_face.vertices]
    assert math.fabs(max(parameters))<0.001
    assert min(parameters)<1

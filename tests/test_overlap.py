from dk_geometry.general import create_cube
from dk_geometry.overlap import do_faces_overlap, FaceOverlap, get_overlapping_faces
from dk_geometry.model import Face, Polyhedron, Vector3d


def inverted_face(face: Face) -> Face:
    return Face(vertices=face.vertices[::-1])


def test_that_identical_faces_overlap():
    face = Face(
        vertices = [
            Vector3d(0,0,0),
            Vector3d(2,0,0),
            Vector3d(2,2,0),
            Vector3d(0,2,0)
        ]
    )
    assert do_faces_overlap(face, inverted_face(face), 0.01, 0.01)


def test_that_nested_faces_overlap():
    big_face = Face(
        vertices = [
            Vector3d(0,0,0),
            Vector3d(3,0,0),
            Vector3d(3,3,0),
            Vector3d(0,3,0)
        ]
    )
    small_face = Face(
        vertices = [
            Vector3d(1,1,0),
            Vector3d(2,1,0),
            Vector3d(2,2,0),
            Vector3d(1,2,0)
        ]
    )
    assert do_faces_overlap(big_face, inverted_face(small_face), 0.01, 0.01)


def test_that_touching_faces_do_not_overlap():
    face1 = Face(
        vertices = [
            Vector3d(0,0,0),
            Vector3d(1,0,0),
            Vector3d(1,1,0),
            Vector3d(0,1,0)
        ]
    )
    face2 = Face(
        vertices = [
            Vector3d(1,0,0),
            Vector3d(2,0,0),
            Vector3d(2,1,0),
            Vector3d(1,1,0)
        ]
    )
    assert not do_faces_overlap(face1, inverted_face(face2), 0.01, 0.01)


def test_that_partially_overlapping_faces_overlap():
    face1 = Face(
        vertices = [
            Vector3d(0,0,0),
            Vector3d(2,0,0),
            Vector3d(2,2,0),
            Vector3d(0,2,0)
        ]
    )
    face2 = Face(
        vertices = [
            Vector3d(1,1,0),
            Vector3d(2,1,0),
            Vector3d(2,2,0),
            Vector3d(1,2,0)
        ]
    )
    assert do_faces_overlap(face1, inverted_face(face2), 0.01, 0.01)


def test_that_parallel_but_translated_faces_do_not_overlap():
    face1 = Face(
        vertices = [
            Vector3d(0,0,0),
            Vector3d(1,0,0),
            Vector3d(1,1,0),
            Vector3d(0,1,0)
        ]
    )
    face2 = Face(
        vertices = [
            Vector3d(0,0,1),
            Vector3d(1,0,1),
            Vector3d(1,1,1),
            Vector3d(0,1,1)
        ]
    )
    assert not do_faces_overlap(face1, inverted_face(face2), 0.01, 0.01)


def test_that_separate_faces_in_the_same_plane_do_not_overlap():
    face1 = Face(
        vertices = [
            Vector3d(0,0,0),
            Vector3d(1,0,0),
            Vector3d(1,1,0),
            Vector3d(0,1,0)
        ]
    )
    face2 = Face(
        vertices = [
            Vector3d(2,2,0),
            Vector3d(3,2,0),
            Vector3d(3,3,0),
            Vector3d(2,3,0)
        ]
    )
    assert not do_faces_overlap(face1, inverted_face(face2), 0.01, 0.01)


def test_that_face_in_a_concave_angle_does_not_overlap():
    small_face = Face(
        vertices = [
            Vector3d(0,0,0),
            Vector3d(1,0,0),
            Vector3d(1,1,0),
            Vector3d(0,1,0)
        ]
    )
    face_with_cavity = Face(
        vertices = [
            Vector3d(2,0,0),
            Vector3d(3,0,0),
            Vector3d(3,3,0),
            Vector3d(0,3,0),
            Vector3d(0,2,0),
            Vector3d(2,2,0)
        ]
    )
    assert not do_faces_overlap(small_face, inverted_face(face_with_cavity), 0.01, 0.01)


def test_that_non_parallel_faces_do_not_overlap():
    face1 = Face(
        vertices = [
            Vector3d(0,0,1),
            Vector3d(2,0,1),
            Vector3d(2,2,1),
            Vector3d(0,2,1)
        ]
    )
    face2 = Face(
        vertices = [
            Vector3d(1,0,0),
            Vector3d(1,2,0),
            Vector3d(1,2,2),
            Vector3d(1,0,2)
        ]
    )
    assert not do_faces_overlap(face1, face2, 0.01, 0.01)


def test_that_faces_with_same_normals_do_not_overlap():
    face = Face(
        vertices = [
            Vector3d(0,0,0),
            Vector3d(2,0,0),
            Vector3d(2,2,0),
            Vector3d(0,2,0)
        ]
    )
    assert not do_faces_overlap(face, face, 0.01, 0.01)


def test_get_overlapping_faces():
    test_cube = create_cube(Vector3d(0,0,0), 1000)
    directly_on_top = create_cube(Vector3d(0,1000,0), 1000)
    too_far = create_cube(Vector3d(0,0,2000), 1000)
    under_partially_overlapping = create_cube(Vector3d(200,-1000,0), 1000)
    touching_by_edge = create_cube(Vector3d(1000,1000,0), 1000)
    overlaps = get_overlapping_faces(
        test_cube.faces,
        [
            directly_on_top,
            too_far,
            under_partially_overlapping,
            touching_by_edge
        ]
    )
    assert list(overlaps.keys())==[1,3]
    assert overlaps[1]==[FaceOverlap(poly_index=0, face_index=3)]
    assert overlaps[3]==[FaceOverlap(poly_index=2, face_index=1)]

import math
from source.model import *
from source.general import *


def make_simple_square_face() -> Face:
    return Face(
        vertices = [
            Vector3d(0, 0, 0),
            Vector3d(2, 0, 0),
            Vector3d(2, 2, 0),
            Vector3d(0, 2, 0),
        ]
    )


def test_that_vertices_are_either_on_face_or_another_plane():
    for offset in [-1, 1]:
        input_face = make_simple_square_face()
        plate = make_plate(input_face, offset)
        on_plane_count = 0
        off_plane_count = 0
        for face in plate.faces:
            for vertex in face.vertices:
                distance = calculate_signed_distance_to_plane(vertex, input_face.plane)
                if math.fabs(distance)<0.0001:
                    on_plane_count+=1
                elif math.fabs(distance-offset)<0.0001:
                    off_plane_count+=1
                else:
                    assert False, "a vertex is neither on the original plane nor on the shifted one"
        assert on_plane_count == len(face.vertices)*3, "unexpected number of vertices on the original plane"
        assert off_plane_count == len(face.vertices)*3, "unexpected number of vertices on the shifted plane"


def test_that_plates_are_not_inverted():
    for offset in [-1, 1]:
        plate = make_plate(make_simple_square_face(), offset)
        volume = calculate_polyhedron_signed_volume(plate)
        assert volume>0, f"plate volume is negative for offset {offset}"


def test_that_faces_are_not_skewed():
    input_face = make_simple_square_face()
    normalized_normal = input_face.plane.normal.normalized
    plate = make_plate(input_face, 1)
    for face in plate.faces:
        cos = face.plane.normal.normalized.dotProduct(normalized_normal)
        assert (
            math.fabs(cos)<0.0001 or math.fabs(cos)>0.9999
        ), f"a face is neither parallel nor orthogonal to the original one"

import math
from _decimal import Decimal

from source.general import (
    calculate_signed_distance_to_plane,
)


def test_offset_all_faces(polyhedron_cutout_sloped):
    poly = polyhedron_cutout_sloped()

    print(poly.faces)


def test_polyhedron_offset_exclude_front_back(polyhedron_cutout_sloped):
    poly = polyhedron_cutout_sloped()

    new_poly = poly.apply_offset(
        offset=Decimal(18),
        offset_map={6: Decimal(0), 5: Decimal(0)},
    )

    # Collect distinct values in a set
    distinct_front_z = {vertex.z for vertex in poly.faces[5].vectors}
    # In case the front face is not offset, the z coordinate should remain unchanged
    assert distinct_front_z == {Decimal(0)}, f"Expected 0, got {distinct_front_z}"

    # Collect distinct values in a set
    distinct_back_z = {vertex.z for vertex in poly.faces[6].vectors}
    # In case the front face is not offset, the z coordinate should remain unchanged
    assert distinct_back_z == {Decimal(-600)}, f"Expected 0, got {distinct_back_z}"


def test_that_the_offset_has_been_done(polyhedron_cutout_sloped):
    offset_distance = Decimal(10)
    input = polyhedron_cutout_sloped()
    output = input.apply_offset(offset=offset_distance)
    for face_index in range(len(input.faces)):
        input_face = input.faces[face_index]
        output_face = output.faces[face_index]
        input_plane = input_face.plane
        output_plane = output_face.plane
        assert (
            output_plane.normal - input_plane.normal
        ).length < 0.001, f"Face #{face_index} has a different normal after offset"
        for vertex in output.faces[face_index].vectors:
            distance_to_plane = calculate_signed_distance_to_plane(
                vertex, input_plane
            )
            assert (
                math.fabs(distance_to_plane - float(offset_distance)) < 0.1
            ), f"Vertex on face #{face_index} does not have the correct distance to the original plane"

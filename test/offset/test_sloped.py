from _decimal import Decimal

from offset import apply_offset


def test_offset_all_faces(polyhedron_cutout_sloped):
    poly = polyhedron_cutout_sloped()

    print(poly.faces)


def test_polyhedron_offset_exclude_front_back(polyhedron_cutout_sloped):
    poly = polyhedron_cutout_sloped()

    new_poly = apply_offset(
        poly,
        offset=Decimal(18),
        offset_map={5: Decimal(0), 4: Decimal(0)},
    )

    # Collect distinct values in a set
    distinct_front_z = {
        vertex.z for face in poly.faces if face.index == 4 for vertex in face.vertices
    }
    # In case the front face is not offset, the z coordinate should remain unchanged
    assert distinct_front_z == {Decimal(0)}, f"Expected 0, got {distinct_front_z}"

    # Collect distinct values in a set
    distinct_back_z = {
        vertex.z for face in poly.faces if face.index == 5 for vertex in face.vertices
    }
    # In case the front face is not offset, the z coordinate should remain unchanged
    assert distinct_back_z == {Decimal(600)}, f"Expected 0, got {distinct_back_z}"

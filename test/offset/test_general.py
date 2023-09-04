from _decimal import Decimal

from offset import apply_offset
from model import Face


def test_normals_set_after_processing(polyhedron_cutout_sloped):
    """When the offset is applied, all normals should be populated for later use"""
    poly = polyhedron_cutout_sloped()

    apply_offset(polyhedron=poly, offset=Decimal(10))

    for face in poly.faces:
        assert isinstance(face, Face)
        for vertex in face.vertices:
            assert vertex.normal is not None


def test_number_of_faces(polyhedron_cutout_sloped):
    poly = polyhedron_cutout_sloped()

    offset_poly = apply_offset(polyhedron=poly, offset=Decimal(10))

    assert len(offset_poly.faces) == len(
        poly.faces
    ), f"Expected {len(poly.faces)} faces, got {len(offset_poly.faces)}"

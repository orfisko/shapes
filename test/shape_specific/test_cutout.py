from _decimal import Decimal

from main import apply_offset
from model import FaceLocation


def test_offset_all_faces(polyhedron_cutout):
    poly = polyhedron_cutout()
    offset_poly = apply_offset(polyhedron=poly, offset=Decimal(18))

    left = Decimal(0 + 18)
    right = Decimal(1200 - 18)
    top = Decimal(2500 - 18)
    bottom = Decimal(0 + 18)
    back = Decimal(600 - 18)
    front = Decimal(0 + 18)
    cutout_z = Decimal(300 - 18)
    cutout_x = Decimal(500 - 18)

    check_poly = polyhedron_cutout(
        left=left,
        right=right,
        top=top,
        bottom=bottom,
        back=back,
        front=front,
        cutout_z=cutout_z,
        cutout_x=cutout_x,
    )

    # Note that dataclasses have a __eq__ method built in that checks all fields specified in the class
    # In pycharm it's very easy to compare these side by side
    assert offset_poly == check_poly


def test_polyhedron_offset_exclude_front_back(polyhedron_cutout):
    poly = polyhedron_cutout()

    new_poly = apply_offset(
        poly,
        offset=Decimal(18),
        offset_map={FaceLocation.BACK: Decimal(0), FaceLocation.FRONT: Decimal(0)},
    )

    # Collect distinct values for z in the front
    front_z = {
        vertex.z
        for poly in (poly, new_poly)
        for face in poly.faces
        if face.faceLocation == FaceLocation.FRONT
        for vertex in face.vertices
    }
    # In case the front face is not offset, the z coordinate should remain unchanged
    assert (
        len(front_z) == 1
    ), f"Distinct z coordinates for front are note the same, got these values {front_z}"

    # Collect distinct values in a set
    back_z = {
        vertex.z
        for poly in (poly, new_poly)
        for face in poly.faces
        if face.faceLocation == FaceLocation.FRONT
        for vertex in face.vertices
    }
    # In case the back face is not offset, the z coordinate should remain unchanged
    assert (
        len(back_z) == 1
    ), f"Distinct z coordinates for back are note the same, got these values {back_z}"

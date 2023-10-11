from _decimal import Decimal

from dk_geometry.model import SliceInterval
from dk_geometry.slice import apply_slice_interval

import pytest


@pytest.mark.skip(reason="not implemented")
def test_change_rotation(polyhedron_cutout):
    """This test is there to verify that if we send in a number of slices, the order of the vertices is being
    rotated depending on the face location"""
    poly = polyhedron_cutout()

    poly_slice = apply_slice_interval(
        polyhedron=poly, slice=SliceInterval(left_x=Decimal(10), right_x=Decimal(20))
    )

    poly_slice_check = polyhedron_cutout(
        top=Decimal(20),
        bottom=Decimal(10),
    )
    assert (
        poly_slice == poly_slice_check
    ), f"Expected {poly_slice_check}, got {poly_slice}"

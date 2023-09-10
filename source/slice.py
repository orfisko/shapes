from _decimal import Decimal
from typing import List, Set

from source.model import Polyhedron, SliceInterval, Slice, Vector3d


def apply_slice(polyhedron: Polyhedron, slice: Slice) -> List[Vector3d]:
    """
    Makes a cross sectional cut of the polyhedron
    Args:
        polyhedron: polyhedron to cut
        slice: slice to apply

    Returns:
        A list of vertices that define a plane generated at the slice location
    """


def apply_slice_interval(polyhedron: Polyhedron, slice: SliceInterval) -> Polyhedron:
    """
    Generates a new polyhedron with the slice applied to the vertices.
    Args:
        polyhedron: the polyhedron for which the slice needs to be applied
        slice: the slice that needs to be applied

    Returns:
        a new polyhedron with the slice applied.
    """
    return polyhedron


def apply_slice_intervals(
    polyhedron: Polyhedron, slices: List[SliceInterval]
) -> List[Polyhedron]:
    """
    Generate a list of polyhedrons with the slices applied. Will only result in optimization over a consecutive calling
    of apply_slice if the slice intervals are touching on at least one axis. This function will be called a lot whereby
    the slices are defined on a single axis and with overlapping start and end points.
    Args:
        polyhedron: polyhedron to be sliced
        slices: list of slices to apply

    Returns:
        List of sliced polyhedrons
    """
    # We can constrain this function to only work for slice intervals that vary on a single axis
    x_slices: Set[Decimal] = set()
    y_slices: Set[Decimal] = set()
    z_slices: Set[Decimal] = set()

    for slice in slices:
        x_slices.add(slice.x0)
        x_slices.add(slice.x1)
        y_slices.add(slice.y0)
        y_slices.add(slice.y1)
        z_slices.add(slice.z0)
        z_slices.add(slice.z1)

    # For each individual slice on the specified axis we could send that to the apply_slice function

    # Once we get the return, we might need to change the order of the vertices to make sure that the faces are still
    # rendered 'outwards' when reassembling them into a polyhedron

    return polyhedron

from _decimal import Decimal
from typing import List, Set

from dk_geometry.general import cut_polyhedron_by_plane
from dk_geometry.model import Plane3d, Polyhedron, SliceInterval, Slice, Vector3d
from copy import deepcopy


def apply_slice_interval(polyhedron: Polyhedron, slice: SliceInterval) -> Polyhedron:
    """
    Generates a new polyhedron with the slice applied to the vertices.
    Args:
        polyhedron: the polyhedron for which the slice needs to be applied
        slice: the slice that needs to be applied

    Returns:
        a new polyhedron with the slice applied.
    """
    result = polyhedron
    if slice.x0 is not None:
        result = cut_polyhedron_by_plane(
            result,
            Plane3d(origin=Vector3d(slice.x0,0,0), normal=Vector3d(-1,0,0))
        )
    if slice.x1 is not None:
        result = cut_polyhedron_by_plane(
            result,
            Plane3d(origin=Vector3d(slice.x1,0,0), normal=Vector3d(1,0,0))
        )
    if slice.y0 is not None:
        result = cut_polyhedron_by_plane(
            result,
            Plane3d(origin=Vector3d(0,slice.y0,0), normal=Vector3d(0,-1,0))
        )
    if slice.y1 is not None:
        result = cut_polyhedron_by_plane(
            result,
            Plane3d(origin=Vector3d(0,slice.y1,0), normal=Vector3d(0,1,0))
        )
    if slice.z0 is not None:
        result = cut_polyhedron_by_plane(
            result,
            Plane3d(origin=Vector3d(0,0,slice.z0), normal=Vector3d(0,0,-1))
        )
    if slice.z1 is not None:
        result = cut_polyhedron_by_plane(
            result,
            Plane3d(origin=Vector3d(0,0,slice.z1), normal=Vector3d(0,0,1))
        )
    return deepcopy(result)

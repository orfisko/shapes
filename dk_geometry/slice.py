from copy import deepcopy

from dk_geometry.general import cut_polyhedron_by_plane
from dk_geometry.model import Plane3d, Polyhedron, SliceInterval, Vector3d


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
    if slice.min_x is not None:
        result = cut_polyhedron_by_plane(
            result,
            Plane3d(origin=Vector3d(slice.min_x, 0, 0), normal=Vector3d(-1, 0, 0)),
        )
    if slice.max_x is not None:
        result = cut_polyhedron_by_plane(
            result,
            Plane3d(origin=Vector3d(slice.max_x, 0, 0), normal=Vector3d(1, 0, 0)),
        )
    if slice.min_y is not None:
        result = cut_polyhedron_by_plane(
            result,
            Plane3d(origin=Vector3d(0, slice.min_y, 0), normal=Vector3d(0, -1, 0)),
        )
    if slice.max_y is not None:
        result = cut_polyhedron_by_plane(
            result,
            Plane3d(origin=Vector3d(0, slice.max_y, 0), normal=Vector3d(0, 1, 0)),
        )
    if slice.min_z is not None:
        result = cut_polyhedron_by_plane(
            result,
            Plane3d(origin=Vector3d(0, 0, slice.min_z), normal=Vector3d(0, 0, -1)),
        )
    if slice.front_z is not None:
        result = cut_polyhedron_by_plane(
            result,
            Plane3d(origin=Vector3d(0, 0, slice.front_z), normal=Vector3d(0, 0, 1)),
        )
    return deepcopy(result)

from collections import namedtuple, defaultdict
from typing import Optional, Callable

from dk_geometry.model import Polyhedron

FaceOverlap = namedtuple("FaceOverlap", ["poly_index", "face_index"])


def get_overlapping_faces(
    polyhedron: Polyhedron, faces: Optional[list[int]], polyhedrons: list[Polyhedron]
) -> dict[int, list[FaceOverlap]]:
    """
    Function to find out which face of a polyhedrons touches one of the faces of a given polyhedron. Note that
    line touches should not be included.
    Args:
        polyhedron: polyhedron to check
        faces: optional parameter to specify which faces of the polyhedron to check
        polyhedrons: the list of polyhedrons to check against
    Returns:
        a dictionary containing per face of the given polyhedron as key the list of faceoverlaps
    """

    # index:The index of the polyhedron in the passed list of polyhedrons
    # faces: the list of faces where the other polyhedron is touching the given polyhedron
    result: defaultdict[int, list[FaceOverlap]] = defaultdict(list)

    return result


def prioritize_polyhedrons(
    polyhedrons: list[Polyhedron],
    idx,
    other_idx,
    facee_idx,
    other_face_idx,
    overlap: float,
) -> tuple[Polyhedron, Polyhedron]:
    poly = polyhedrons[idx]
    other_poly = polyhedrons[other_idx]
    # Figure out what to do and then apply offset
    poly = poly.apply_offset(...)
    other_poly = other_poly.apply_offset(...)
    return poly, other_poly


def resolve_overlapping_polyhedrons(
    polyhedrons: list[Polyhedron],
    resolve_function: Callable[
        [list[Polyhedron], int, int, int, int, float], tuple[Polyhedron, Polyhedron]
    ],
):
    """
    Function to resolve overlapping polyhedrons. The resolve_function is called for each overlapping polyhedron pair
    Args:
        polyhedrons: the list of polyhedrons to check
        resolve_function: the function to call for each overlapping polyhedron pair
    """

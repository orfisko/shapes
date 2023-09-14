from collections import namedtuple, defaultdict
from typing import Callable

from dk_geometry.model import Polyhedron, Face

FaceOverlap = namedtuple("FaceOverlap", ["poly_index", "face_index"])


def get_overlapping_faces(
    faces: list[Face], polyhedra: list[Polyhedron]
) -> dict[int, list[FaceOverlap]]:
    """
    Function to find out which face of a polyhedra touches one of the faces of a given polyhedron. Note that
    line touches should not be included.
    Args:
        faces: which faces to check against the sent in polyhedra
        polyhedra: the list of polyhedrons to check against
    Returns:
        a dictionary containing per face of the given polyhedron as key the list of faceoverlaps
    """

    # index:The index of the polyhedron in the passed list of polyhedrons
    # faces: the list of faces where the other polyhedron is touching the given polyhedron
    result: defaultdict[int, list[FaceOverlap]] = defaultdict(list)

    return result


def get_non_overlapping_faces(
    faces: list[Face], polyhedra: list[Polyhedron]
) -> list[int]:
    """Returns all faces that are not touching the faces of ather polyehedra"""
    overlapping_faces = get_overlapping_faces(faces=faces, polyhedra=polyhedra)
    return [
        face_index
        for face_index in range(len(faces))
        if face_index not in overlapping_faces
    ]


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

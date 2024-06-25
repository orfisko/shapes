# Copyright: 2024 BV De Kastenman
import math
from collections import defaultdict

from dk_geometry.general import calculate_signed_distance_to_plane, cut_face_by_plane
from dk_geometry.model import Face, Plane3d, Polyhedron, FaceOverlap


def same_plane(face1: Face, face2: Face, tolerance) -> bool:
    plane1 = face1.plane
    for v in face2.vertices:
        if math.fabs(calculate_signed_distance_to_plane(v, plane1)) > tolerance:
            return False
    plane2 = face2.plane
    for v in face1.vertices:
        if math.fabs(calculate_signed_distance_to_plane(v, plane2)) > tolerance:
            return False
    return True


def intersect_convex_faces(face1: Face, face2: Face) -> Face:
    face2_normal = face2.plane.normal
    for edge_index in range(len(face2.vertices)):
        edge = face2.get_edge(edge_index)
        plane = Plane3d(
            origin=edge[0],
            normal=(edge[1] - edge[0]).crossProduct(face2_normal).normalized,
        )
        face1 = cut_face_by_plane(face1, plane, {}, {})
    return face1


def split_face_into_convex_pieces(face: Face) -> list[Face]:
    inner_corner_indices = []
    face_normal = face.plane.normal
    for index in range(len(face.vertices)):
        previous_edge = face.get_edge((index - 1) % len(face.vertices))
        previous_vector = previous_edge[1] - previous_edge[0]
        next_edge = face.get_edge(index)
        next_vector = next_edge[1] - next_edge[0]
        if previous_vector.crossProduct(next_vector).dotProduct(face_normal) < 0:
            inner_corner_indices.append(index)
    if len(inner_corner_indices) == 0:
        return [face]
    if len(inner_corner_indices) > 1:
        raise ValueError("a face has more than one inner corner")
    central_index = inner_corner_indices[0]
    pieces = []
    for shift in range(1, len(face.vertices) - 1):
        pieces.append(
            Face(
                vertices=[
                    face.vertices[central_index],
                    face.vertices[(central_index + shift) % len(face.vertices)],
                    face.vertices[(central_index + shift + 1) % len(face.vertices)],
                ]
            )
        )
    return pieces


def do_faces_overlap(
    face1: Face,
    face2: Face,
    tolerance: float,
    min_area: float,
    opposite_facenormals: bool = True,
) -> tuple[bool, float]:
    if opposite_facenormals:
        if face1.plane.normal.dotProduct(face2.plane.normal) > 0:
            return False, 0
    if not same_plane(face1, face2, tolerance):
        return False, 0
    area = 0
    for convex1 in split_face_into_convex_pieces(face1):
        for convex2 in split_face_into_convex_pieces(face2):
            area += intersect_convex_faces(face1, face2).surfaceArea
    return area >= min_area, area


def get_overlapping_faces(
    faces: list[Face], polyhedra: list[Polyhedron], opposite_facenormals: bool = True
) -> dict[int, list[FaceOverlap]]:
    """
    Function to find out which face of a polyhedra touches one of the faces of a given polyhedron. Note that
    line are not included. Also faces need to have opposite normals to be touching.
    Limitation: all faces must have at most one inner corner
    Args:
        faces: which faces to check against the sent in polyhedra
        polyhedra: the list of polyhedrons to check against
        opposite_facenormals: if true, only faces with opposite normals are considered touching
    Returns:
        a dictionary containing per face of the given polyhedron as key the list of faceoverlaps
    """

    # index:The index of the polyhedron in the passed list of polyhedrons
    # faces: the list of faces where the other polyhedron is touching the given polyhedron
    result: defaultdict[int, list[FaceOverlap]] = defaultdict(list)
    for face_index, face in enumerate(faces):
        for polyhedron_index, polyhedron in enumerate(polyhedra):
            for adjacent_index, adjacent_face in enumerate(polyhedron.faces):
                overlap, area = do_faces_overlap(
                    face, adjacent_face, 1, 1, opposite_facenormals
                )
                if overlap:
                    result[face_index].append(
                        FaceOverlap(polyhedron_index, adjacent_index, area)
                    )

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

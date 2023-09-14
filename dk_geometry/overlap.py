from collections import namedtuple, defaultdict
from typing import Optional, Callable, Tuple

from dk_geometry.model import default_config, Face, Line3d, Plane3d, Polyhedron, Vector3d
from dk_geometry.general import calculate_signed_distance_to_plane
from pydantic import confloat, ConfigDict, model_validator
from pydantic.dataclasses import dataclass
import math


def do_faces_overlap(
    face1: Face,
    face2: Face,
    tolerance: float,
    min_depth: float
) -> bool:
    def same_plane(face1: Face, face2: Face, tolerance) -> bool:
        plane1 = face1.plane
        for v in face2.vertices:
            if math.fabs(calculate_signed_distance_to_plane(v, plane1))>tolerance:
                return False
        plane2 = face2.plane
        for v in face1.vertices:
            if math.fabs(calculate_signed_distance_to_plane(v, plane2))>tolerance:
                return False
        return True
    def select_orthogonal(vector: Vector3d) -> Vector3d:
        if math.fabs(vector.x)>math.fabs(vector.y):
            return vector.crossProduct(Vector3d(0,1,0))
        else:
            return vector.crossProduct(Vector3d(1,0,0))
    def make_polygon(
        face: Face,
        x: Vector3d,
        y: Vector3d,
    ) -> [Vector3d]:
        return [
            Vector3d(v.dotProduct(x), v.dotProduct(y), 0)
            for v in face.vertices
        ]
    def get_distance_to_segment(
        point: Vector3d,
        segment_start: Vector3d,
        segment_finish: Vector3d
    ) -> float:
        segment_vector = segment_finish - segment_start
        line_parameter = 0
        if segment_vector.length>0:
            line_parameter = (point - segment_start).dotProduct(segment_vector)/segment_vector.length**2
            if line_parameter<0:
                line_parameter = 0
            elif line_parameter>1:
                line_parameter = 1
        projection = segment_start + segment_vector*line_parameter
        return (point-projection).length
    def get_distance_to_polygon(
        point: Vector3d,
        polygon: [Vector3d]
    ) -> float:
        min_distance = None
        for e in range(len(polygon)):
            distance = get_distance_to_segment(
                point,
                polygon[e],
                polygon[(e+1) % len(polygon)]
            )
            if min_distance is None or distance<min_distance:
                min_distance = distance
        return distance
    def is_point_inside_polygon(point: Vector3d, polygon: [Vector3d]) -> bool:
        ray = Line3d(
            origin = point,
            direction = Vector3d(1,0,0)
        )
        cutting_plane = Plane3d(
            origin = point,
            normal = Vector3d(0,1,0)
        )
        vertex_distances_to_plane = {
            id(v): calculate_signed_distance_to_plane(v, cutting_plane)
            for v in polygon
        }
        inside = False
        for e in range(len(polygon)):
            edge_start = polygon[e]
            edge_finish = polygon[(e+1)%len(polygon)]
            distances = (
                vertex_distances_to_plane[id(edge_start)],
                vertex_distances_to_plane[id(edge_finish)]
            )
            if (distances[0]<0) == (distances[1]<0):
                continue #they are on the same side of the cut
            parameter = (0-distances[0]) / (distances[1]-distances[0])
            intersection_point = edge_start + (edge_finish-edge_start)*parameter
            if (intersection_point-ray.origin).dotProduct(ray.direction)>0:
                inside = not inside
        return inside
    def get_signed_distance_to_polygon(
        point: Vector3d,
        polygon: [Vector3d]
    ) -> float:
        distance = get_distance_to_polygon(point, polygon)
        if is_point_inside_polygon(point, polygon):
            distance = -distance
        return distance
    def do_polygons_overlap(
        polygon1: [Vector3d],
        polygon2: [Vector3d],
        min_radius: float
    ) -> bool:
        """
        Checks whether there is a point inside of both polygons which is
        at least at min_radius distance from both of them
        """
        @dataclass(**default_config)
        class Square:
            centre: Vector3d
            size: float
        x_values = [v.x for v in polygon1+polygon2]
        y_values = [v.y for v in polygon1+polygon2]
        areas = [
            Square(
                centre=Vector3d(
                    (min(x_values)+max(x_values))/2,
                    (min(y_values)+max(y_values))/2,
                    0
                ),
                size=max(
                    max(x_values)-min(x_values),
                    max(y_values)-min(y_values)
                )
            )
        ]
        while len(areas)!=0:
            smaller_areas = []
            for area in areas:
                distance = max(
                    get_signed_distance_to_polygon(area.centre, polygon1),
                    get_signed_distance_to_polygon(area.centre, polygon2)
                )
                if distance<-min_radius:
                    return True
                if area.size<tolerance:
                    continue
                min_possible_distance = distance - area.size/math.sqrt(2)
                if min_possible_distance>min_radius:
                    continue #it has no chances to have a point satisfying the condition
                for dx in (-1,1):
                    for dy in (-1,1):
                        smaller_areas.append(
                            Square(
                                centre = area.centre + Vector3d(dx,dy,0)*area.size/4,
                                size = area.size/2
                            )
                        )
            areas = smaller_areas
        return False

    if not same_plane(face1, face2, tolerance):
        return False
    normal = face1.plane.normal
    x = select_orthogonal(normal).normalized
    y = normal.crossProduct(x).normalized
    polygon1 = make_polygon(face1, x, y)
    polygon2 = make_polygon(face2, x, y)
    return do_polygons_overlap(polygon1, polygon2, min_depth/2)


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
    for face_index, face in enumerate(faces):
        for polyhedron_index, polyhedron in enumerate(polyhedra):
            for adjacent_index, adjacent_face in enumerate(polyhedron.faces):
                if do_faces_overlap(face, adjacent_face, 1, 1):
                    result[face_index].append(
                        FaceOverlap(polyhedron_index, adjacent_index)
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

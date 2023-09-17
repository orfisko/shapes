from collections import namedtuple, defaultdict
from typing import Optional, Callable, Tuple

from dk_geometry.model import default_config, Face, Line3d, Plane3d, Polyhedron, Vector3d
from dk_geometry.general import calculate_signed_distance_to_plane, cut_polyhedron_by_plane
from pydantic import confloat, ConfigDict, model_validator
from pydantic.dataclasses import dataclass
from enum import Enum
import math

@dataclass
class Edge:
    door_index: int
    edge_index: int
    def __eq__(self, other):
        return self.door_index==other.door_index and self.edge_index==other.edge_index
    def __hash__(self):
        return hash((self.door_index, self.edge_index))


@dataclass
class Range:
    min: float
    max: float
    def length(self) -> float:
        return self.max-self.min
    def intersect(self, other):
        return Range(
            max(self.min, other.min),
            min(self.max, other.max)
        )


@dataclass
class Overlap:
    min_edge: Edge
    max_edge: Edge
    range: Range


@dataclass
class Cut(Enum):
    none = 0
    half = 50
    full = 100
    def get_cut_distance(self, overlap_depth: float, gap_size: float) -> float:
        return (overlap_depth+gap_size)*self.value/100


@dataclass
class CutOnEdge:
    edge: Edge
    cut: Cut


def get_main_face(door: Polyhedron) -> Face:
    front_faces = [
        face
        for face in door.faces
        if face.plane.normal.normalized.z<-0.99
    ]
    if len(front_faces)==0:
        raise ValueError("a door has no front face")
    if len(front_faces)>1:
        raise ValueError("a door has multiple front faces")
    return front_faces[0]


def get_range(face: Face, direction: Vector3d) -> Range:
    min = None
    max = None
    for v in face.vertices:
        value = v.dotProduct(direction)
        if min is None or value<min:
            min = value
        if max is None or value>max:
            max = value
    return Range(min, max)


def get_extreme_edge_index(face: Face, direction: Vector3d) -> int:
    result = None
    max_parameter = None
    for e in range(len(face.vertices)):
        edge = face.get_edge(e)
        middle = (edge[0]+edge[1])/2
        parameter = middle.dotProduct(direction)
        if max_parameter is None or parameter>max_parameter:
            max_parameter = parameter
            result = e
    return result


def get_overlaps(
    door_faces: list[Face],
    cross_direction: Vector3d,
    min_overlap_length: float
) -> list[Overlap]:
    direction = cross_direction.crossProduct(Vector3d(0,0,1))
    ranges_along = [get_range(f, direction) for f in door_faces]
    ranges_across = [get_range(f, cross_direction) for f in door_faces]
    overlaps = []
    for index1, door1 in enumerate(door_faces):
        range_along1 = ranges_along[index1]
        range_across1 = ranges_across[index1]
        for index2, door2 in enumerate(door_faces):
            if index2<=index1:
                continue
            range_along2 = ranges_along[index2]
            range_across2 = ranges_across[index2]
            if range_along1.intersect(range_along2).length() < min_overlap_length:
                continue
            overlap_range = range_across1.intersect(range_across2)
            if overlap_range.length()<0:
                continue
            min_index = index1 if range_across1.min<range_across2.min else index2
            max_index = index1 + index2 - min_index
            overlaps.append(
                Overlap(
                    Edge(
                        min_index,
                        get_extreme_edge_index(door_faces[min_index],cross_direction)
                    ),
                    Edge(
                        max_index,
                        get_extreme_edge_index(door_faces[max_index],-cross_direction)
                    ),
                    overlap_range
                )
            )
    return overlaps


def does_range_group_cover_another_group(
    covering_ranges: list[Range],
    covered_ranges: list[Range]
) -> bool:
    class Event(Enum):
        start_covering_range = 1
        finish_covering_range = 2
        start_covered_range = 3
        finish_covered_range = 4
    tolerance = 0.01
    events = []
    for range in covering_ranges:
        events.append((range.min-tolerance, Event.start_covering_range))
        events.append((range.max+tolerance, Event.finish_covering_range))
    for range in covered_ranges:
        events.append((range.min, Event.start_covered_range))
        events.append((range.max, Event.finish_covered_range))
    events.sort(key=lambda e:e[0])
    covering_count = 0
    covered_count = 0
    for unused, event in events:
        if event==Event.start_covering_range:
            covering_count+=1
        elif event==Event.finish_covering_range:
            covering_count-=1
        elif event==Event.start_covered_range:
            covered_count+=1
        elif event==Event.finish_covered_range:
            covered_count-=1
        if covering_count==0 and covered_count>0:
            return False
    return True


def select_cuts(
    door_faces: list[Face],
    overlaps: list[Overlap],
    cross_direction: Vector3d,
    gap_size: float
) -> dict[Edge, float]:
    ranges = [
        get_range(f, cross_direction.crossProduct(Vector3d(0,0,1)))
        for f in door_faces
    ]
    min_edge_to_max_edges = defaultdict(list)
    max_edge_to_min_edges = defaultdict(list)
    for overlap in overlaps:
        min_edge_to_max_edges[overlap.min_edge].append(overlap.max_edge)
        max_edge_to_min_edges[overlap.max_edge].append(overlap.min_edge)
    cuts = {}
    for overlap in overlaps:
        if overlap.min_edge in cuts:
            continue
        min_edges = [overlap.min_edge]
        max_edges = []
        todo = [overlap.min_edge]
        while len(todo)>0:
            current = todo.pop()
            for max_edge in min_edge_to_max_edges[current]:
                if max_edge in max_edges:
                    continue
                max_edges.append(max_edge)
                for min_edge in max_edge_to_min_edges[max_edge]:
                    if min_edge in min_edges:
                        continue
                    min_edges.append(min_edge)
                    todo.append(min_edge)
        min_cut = Cut.half
        max_cut = Cut.half
        min_ranges = [ranges[edge.door_index] for edge in min_edges]
        max_ranges = [ranges[edge.door_index] for edge in max_edges]
        if not does_range_group_cover_another_group(min_ranges, max_ranges):
            min_cut = Cut.full
            max_cut = Cut.none
        if not does_range_group_cover_another_group(max_ranges, min_ranges):
            min_cut = Cut.none
            max_cut = Cut.full
        for edge in min_edges:
            cuts[edge] = min_cut.get_cut_distance(overlap.range.length(), gap_size)
        for edge in max_edges:
            cuts[edge] = max_cut.get_cut_distance(overlap.range.length(), gap_size)
    return cuts


def perform_cuts(
    doors: list[Polyhedron],
    faces: list[Face],
    cuts: dict[Edge, float],
    cross_direction: Vector3d,
    gap_size: float
) -> list[Polyhedron]:
    result = []
    for door_index, door in enumerate(doors):
        cut_door = door
        for edge, cut in cuts.items():
            if edge.door_index!=door_index:
                continue
            if cut<0.01:
                continue #cutting a polyhedron with its own face is unstable
            edge = faces[door_index].get_edge(edge.edge_index)
            edge_direction = (edge[1]-edge[0]).normalized
            plane_normal = edge_direction.crossProduct(Vector3d(0,0,-1))
            plane = Plane3d(
                origin = edge[0]-plane_normal*cut,
                normal = plane_normal
            )
            cut_door = cut_polyhedron_by_plane(cut_door, plane)
        result.append(cut_door)
    return result


def resolve_door_overlaps(
    door_shapes: list[Polyhedron],
    gap_size: float,
    min_overlap_length: float
) -> list[Polyhedron]:
    """
    The function cuts the given doors to remove overlaps between them ensuring that:
    1. straight edges of the doors remain straight (we only cut with planes)
    2. there are no overlaps in the resulting shapes
    3. when an overlap is resolved there should be a gap added between the doors
    4. all involved dividers should be covered when the doors are closed
    5. if possible, as many doors as possible should have as many striking panels
       as possible
    door_shapes is the shapes which cover the needed space and the adjacent dividers.
    expectations:
    1. the doors are plate-shaped - they have two relatively large opposite faces and
       the rest is the connecting ones, long and narrow
    2. all doors are in the same XY plane
    3. near the overlaps the edges of the doors are aligned along either X or Y
       (slopes are OK if they are not in the overlap areas)
    4. doors should be convex
    gap_size is the gap which should be created between the doors.
    min_overlap_length: overlaps shorter than this will be ignored.
    """
    for overlap_cross_direction in [Vector3d(1,0,0), Vector3d(0,1,0)]:
        faces = [get_main_face(door) for door in door_shapes]
        overlaps = get_overlaps(faces, overlap_cross_direction, min_overlap_length)
        cuts = select_cuts(faces, overlaps, overlap_cross_direction, gap_size)
        door_shapes = perform_cuts(
            door_shapes,
            faces,
            cuts,
            overlap_cross_direction,
            gap_size
        )
    return door_shapes

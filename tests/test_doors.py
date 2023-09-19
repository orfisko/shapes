from dk_geometry.general import make_plate
from dk_geometry.model import Face, Polyhedron, Vector3d
from dk_geometry.doors import resolve_door_overlaps
from dk_geometry.utils import export_to_obj
import math
import pytest

def make_door(
    left: float,
    right: float,
    top: float,
    bottom: float,
) -> Polyhedron:
    return make_plate(
        Face(
            vertices = [
                Vector3d(left, top, 0),
                Vector3d(right, top, 0),
                Vector3d(right, bottom, 0),
                Vector3d(left, bottom, 0)
            ]
        ),
        1
    )


def test_that_gap_is_created():
    middle = 100
    overlap = 10
    left_height = 100
    left_door = make_door(0, middle+overlap/2, 0, left_height)
    for required_gap in [0,2]:
        for right_height in [left_height, left_height+10]:
            resolved = resolve_door_overlaps(
                [
                    left_door,
                    make_door(middle-overlap/2, 200, 0, right_height)
                ],
                required_gap,
                20
            )
            actual_gap = resolved[1].min_x - resolved[0].max_x
            assert math.fabs(actual_gap-required_gap)<0.01


def test_that_taller_doors_get_overlap():
    middle = 100
    overlap = 10
    left_height = 100
    left_door = make_door(0, middle+overlap/2, 0, left_height)
    for right_height in [left_height-10, left_height, left_height+10]:
        expected_border = middle
        if right_height<left_height-0.001:
            expected_border = middle+overlap/2 #everything to the left door
        elif right_height>left_height+0.001:
            expected_border = middle-overlap/2 #everything to the right door
        right_door = make_door(middle-overlap/2, 200, 0, right_height)
        resolved = resolve_door_overlaps([left_door, right_door], 0, 20)
        actual_border = resolved[0].max_x
        assert math.fabs(actual_border-expected_border)<0.01


def test_that_vertical_overlaps_get_resolved():
    resolved = resolve_door_overlaps(
        [
            make_door(0, 100, 0, 105),
            make_door(0, 100, 95, 200)
        ],
        0,
        20
    )
    assert math.fabs(resolved[1].min_y - resolved[0].max_y)<0.01


def test_2by2_situation():
    doors = [
        make_door(0, 110, 0, 110),
        make_door(95, 200, 0, 110),
        make_door(0, 110, 95, 200),
        make_door(95, 200, 95, 200)
    ]
    resolved = resolve_door_overlaps(doors, 0, 20)
    assert resolved[0].max_x<resolved[1].min_x+0.01
    assert resolved[2].max_x<resolved[3].min_x+0.01
    assert resolved[0].max_y<resolved[2].min_y+0.01
    assert resolved[1].max_y<resolved[3].min_y+0.01

@pytest.mark.skip(reason="only for visual inspection")
def test_doors_visual_inspection():
    doors = [
        make_door(0, 100, 0, 100),
        make_door(0, 100, 90, 210),
        make_door(90, 200, 0, 200)
    ]
    for index, door in enumerate(doors):
        export_to_obj(door, "input."+str(index)+".obj")
    for index, door in enumerate(resolve_door_overlaps(doors,2,20)):
        export_to_obj(door, "output."+str(index)+".obj")

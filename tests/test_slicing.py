import math

from dk_geometry.general import create_cube
from dk_geometry.model import SliceInterval, Vector3d
from dk_geometry.slice import apply_slice_interval


def test_simple_slicing():
    size = 10
    cube = create_cube(Vector3d(0, 0, 0), size)
    slice_interval = SliceInterval(min_x=0, max_x=2, min_y=-1, max_z=20, min_z=-20)
    sliced = apply_slice_interval(cube, slice_interval)
    x = [v.x for f in sliced.faces for v in f.vertices]
    assert math.fabs(min(x) - slice_interval.min_x) < 0.001
    assert math.fabs(max(x) - slice_interval.max_x) < 0.001
    y = [v.y for f in sliced.faces for v in f.vertices]
    assert math.fabs(min(y) - slice_interval.min_y) < 0.001
    assert math.fabs(max(y) - size / 2) < 0.001
    z = [v.z for f in sliced.faces for v in f.vertices]
    assert math.fabs(min(z) - (-size / 2)) < 0.001
    assert math.fabs(max(z) - size / 2) < 0.001

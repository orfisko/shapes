from dk_geometry.general import create_cube
from dk_geometry.model import Face, Plane3d, Polyhedron, SliceInterval, Vector3d
from dk_geometry.slice import apply_slice_interval
import math

def test_simple_slicing():
    size = 10
    cube = create_cube(Vector3d(0,0,0), size)
    slice_interval = SliceInterval(x0=0, x1=2, y0=-1, z0=-20, z1=20)
    sliced = apply_slice_interval(cube, slice_interval)
    x=[v.x for f in sliced.faces for v in f.vertices]
    assert math.fabs(min(x)-slice_interval.x0)<0.001
    assert math.fabs(max(x)-slice_interval.x1)<0.001
    y=[v.y for f in sliced.faces for v in f.vertices]
    assert math.fabs(min(y)-slice_interval.y0)<0.001
    assert math.fabs(max(y)-size/2)<0.001
    z=[v.z for f in sliced.faces for v in f.vertices]
    assert math.fabs(min(z)-(-size/2))<0.001
    assert math.fabs(max(z)-size/2)<0.001

import math

from dk_geometry.general import create_cube
from dk_geometry.model import SliceInterval, Vector3d, Polyhedron, Face
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


def test_sharp_corner_polyhedron():
    polyhedron = Polyhedron(
        faces=[
            Face(
                vertices=[
                    Vector3d(x=491.0, y=1941.8, z=-580.0),
                    Vector3d(x=18.0, y=995.8, z=-580.0),
                    Vector3d(x=18.0, y=995.8, z=0.0),
                    Vector3d(x=491.0, y=1941.8, z=0.0),
                ]
            ),
            Face(
                vertices=[
                    Vector3d(x=491.0, y=536.0, z=-580.0),
                    Vector3d(x=18.0, y=536.0, z=-580.0),
                    Vector3d(x=18.0, y=995.8, z=-580.0),
                    Vector3d(x=491.0, y=1941.8, z=-580.0),
                ]
            ),
            Face(
                vertices=[
                    Vector3d(x=491.0, y=1941.8, z=0.0),
                    Vector3d(x=18.0, y=995.8, z=0.0),
                    Vector3d(x=18.0, y=536.0, z=0.0),
                    Vector3d(x=491.0, y=536.0, z=0.0),
                ]
            ),
            Face(
                vertices=[
                    Vector3d(x=491.0, y=536.0, z=0.0),
                    Vector3d(x=18.0, y=536.0, z=0.0),
                    Vector3d(x=18.0, y=536.0, z=-580.0),
                    Vector3d(x=491.0, y=536.0, z=-580.0),
                ]
            ),
            Face(
                vertices=[
                    Vector3d(x=18.0, y=995.8, z=-580.0),
                    Vector3d(x=18.0, y=536.0, z=-580.0),
                    Vector3d(x=18.0, y=536.0, z=0.0),
                    Vector3d(x=18.0, y=995.8, z=0.0),
                ]
            ),
            Face(
                vertices=[
                    Vector3d(x=491.0, y=1941.8, z=0.0),
                    Vector3d(x=491.0, y=536.0, z=0.0),
                    Vector3d(x=491.0, y=536.0, z=-580.0),
                    Vector3d(x=491.0, y=1941.8, z=-580.0),
                ]
            ),
        ]
    )

    sliced_poly = apply_slice_interval(
        polyhedron=polyhedron, slice=SliceInterval(min_y=1485.2, max_y=1941.8)
    )
    # assert len(new_poly.faces) == 5
    assert not len(
        (
            set(sliced_poly.indexedFaceNormals.values())
            - set(polyhedron.indexedFaceNormals.values())
        )
    ), "Facenormals in sliced polyhedron should also be in source polyhedron"

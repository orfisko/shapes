from dk_geometry.model import Face, Vector3d

from model import Polyhedron


def test_dimension_angled_panel():
    polyhedron = Polyhedron(
        faces=[
            Face(
                vertices=[
                    Vector3d(x=0.0, y=1820.0, z=-18.0),
                    Vector3d(x=0.0, y=1820.0, z=0.0),
                    Vector3d(x=1930.01122, y=0.0, z=0.0),
                    Vector3d(x=1930.01122, y=0.0, z=-18.0),
                ]
            ),
            Face(
                vertices=[
                    Vector3d(x=1930.01122, y=0.0, z=0.0),
                    Vector3d(x=0.0, y=1820.0, z=0.0),
                    Vector3d(x=0.0, y=1462.67598, z=0.0),
                    Vector3d(x=1551.02325, y=0.0, z=0.0),
                ]
            ),
            Face(
                vertices=[
                    Vector3d(x=1930.01122, y=0.0, z=-18.0),
                    Vector3d(x=1930.01122, y=0.0, z=0.0),
                    Vector3d(x=1551.02325, y=0.0, z=0.0),
                    Vector3d(x=1551.02325, y=0.0, z=-18.0),
                ]
            ),
            Face(
                vertices=[
                    Vector3d(x=0.0, y=1462.67598, z=-18.0),
                    Vector3d(x=0.0, y=1462.67598, z=0.0),
                    Vector3d(x=0.0, y=1820.0, z=0.0),
                    Vector3d(x=0.0, y=1820.0, z=-18.0),
                ]
            ),
            Face(
                vertices=[
                    Vector3d(x=1551.02325, y=0.0, z=-18.0),
                    Vector3d(x=1551.02325, y=0.0, z=0.0),
                    Vector3d(x=0.0, y=1462.67598, z=0.0),
                    Vector3d(x=0.0, y=1462.67598, z=-18.0),
                ]
            ),
            Face(
                vertices=[
                    Vector3d(x=1930.01122, y=0.0, z=-18.0),
                    Vector3d(x=1551.02325, y=0.0, z=-18.0),
                    Vector3d(x=0.0, y=1462.67598, z=-18.0),
                    Vector3d(x=0.0, y=1820.0, z=-18.0),
                ]
            ),
        ]
    )
    # face with index 1 and 5 should be 1930 long and 260 wide
    pass
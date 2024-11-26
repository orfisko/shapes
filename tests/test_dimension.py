import math

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
    assert round(polyhedron.faces[1].lw_dimensions.size1, 0) == 2653
    assert round(polyhedron.faces[1].lw_dimensions.size2, 0) == 260


def test_angled_backpanel():
    backpanel = [
        Face(
            vertices=[
                Vector3d(x=18.0, y=2482.0, z=-588.0),
                Vector3d(x=18.0, y=2482.0, z=-580.0),
                Vector3d(x=286.3, y=2482.0, z=-580.0),
                Vector3d(x=286.3, y=2482.0, z=-588.0),
            ]
        ),
        Face(
            vertices=[
                Vector3d(x=286.3, y=2482.0, z=-588.0),
                Vector3d(x=286.3, y=2482.0, z=-580.0),
                Vector3d(x=976.29983, y=18.0, z=-580.0),
                Vector3d(x=976.29983, y=18.0, z=-588.0),
            ]
        ),
        Face(
            vertices=[
                Vector3d(x=976.29983, y=18.0, z=-588.0),
                Vector3d(x=976.29983, y=18.0, z=-580.0),
                Vector3d(x=18.0, y=18.0, z=-580.0),
                Vector3d(x=18.0, y=18.0, z=-588.0),
            ]
        ),
        Face(
            vertices=[
                Vector3d(x=18.0, y=18.0, z=-588.0),
                Vector3d(x=18.0, y=18.0, z=-580.0),
                Vector3d(x=18.0, y=2482.0, z=-580.0),
                Vector3d(x=18.0, y=2482.0, z=-588.0),
            ]
        ),
        Face(
            vertices=[
                Vector3d(x=18.0, y=18.0, z=-580.0),
                Vector3d(x=976.29983, y=18.0, z=-580.0),
                Vector3d(x=286.3, y=2482.0, z=-580.0),
                Vector3d(x=18.0, y=2482.0, z=-580.0),
            ]
        ),
        Face(
            vertices=[
                Vector3d(x=286.3, y=2482.0, z=-588.0),
                Vector3d(x=976.29983, y=18.0, z=-588.0),
                Vector3d(x=18.0, y=18.0, z=-588.0),
                Vector3d(x=18.0, y=2482.0, z=-588.0),
            ]
        ),
    ]
    assert backpanel[4].lw_dimensions.size1 == 2464
    assert math.floor(backpanel[5].lw_dimensions.size2) == 958


def test_horizontal_face():
    face = Face(
        vertices=[
            Vector3d(x=0.0, y=2500.0, z=-600.0),
            Vector3d(x=0.0, y=2500.0, z=0.0),
            Vector3d(x=1000.0, y=2500.0, z=0.0),
            Vector3d(x=1000.0, y=2500.0, z=-600.0),
        ]
    )
    assert face.lw_dimensions.size1 == 1000
    assert face.lw_dimensions.size2 == 600

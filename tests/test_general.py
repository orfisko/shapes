from dk_geometry.enums import Orientation
from dk_geometry.model import Face, Vector3d


def test_orientation(polyhedron_cutout_sloped):
    poly = polyhedron_cutout_sloped()
    top_face = poly.faces[0]
    assert poly.faces[0].orientation == Orientation.T
    assert poly.faces[1].orientation == Orientation.R_T
    assert poly.faces[2].orientation == Orientation.R
    assert poly.faces[3].orientation == Orientation.B
    assert poly.faces[4].orientation == Orientation.L


def test_surface(polyhedron_cutout_sloped):
    poly = polyhedron_cutout_sloped()
    assert poly.faces[0].surfaceArea == 350 * 600

def test_face_lwdimensions():
    face = Face(
        vertices=[
            Vector3d(0,1,0),
            Vector3d(2,0,0),
            Vector3d(2,5,0),
            Vector3d(0,4,0)
        ]
    )
    dimensions = face.lw_dimensions
    assert dimensions.width == 2
    assert dimensions.length == 5

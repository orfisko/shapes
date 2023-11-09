from dk_geometry.enums import FaceNormal
from dk_geometry.model import Face, Vector3d


def test_facenormal(polyhedron_cutout_sloped):
    poly = polyhedron_cutout_sloped()
    top_face = poly.faces[0]
    assert poly.faces[0].faceNormal == FaceNormal.T
    assert poly.faces[1].faceNormal == FaceNormal.R_T
    assert poly.faces[2].faceNormal == FaceNormal.R
    assert poly.faces[3].faceNormal == FaceNormal.B
    assert poly.faces[4].faceNormal == FaceNormal.L
    assert poly.faces[5].faceNormal == FaceNormal.F
    assert poly.faces[6].faceNormal == FaceNormal.BK
    assert poly.faces[7].faceNormal == FaceNormal.R
    assert poly.faces[8].faceNormal == FaceNormal.B
    assert poly.faces[9].faceNormal == FaceNormal.BK


def test_surface(polyhedron_cutout_sloped):
    poly = polyhedron_cutout_sloped()
    assert poly.faces[0].surfaceArea == 350 * 600


def test_face_lwdimensions():
    face = Face(
        vertices=[
            Vector3d(0, 1, 0),
            Vector3d(2, 0, 0),
            Vector3d(2, 5, 0),
            Vector3d(0, 4, 0),
        ]
    )
    dimensions = face.lw_dimensions
    assert dimensions.width == 2
    assert dimensions.length == 5


def test_face_equality():
    face_1 = Face(
        vertices=[
            Vector3d(0, 1, 0),
            Vector3d(2, 0, 0),
            Vector3d(2, 5, 0),
            Vector3d(0, 4, 0),
        ]
    )
    face_2 = Face(
        vertices=[
            Vector3d(0, 4, 0),
            Vector3d(0, 1, 0),
            Vector3d(2, 0, 0),
            Vector3d(2, 5, 0),
        ]
    )
    assert face_1 == face_2

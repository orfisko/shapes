from dk_geometry.model import Face, Vector3d
import math


def create_complex_face():
    return Face(
        vertices=[
            Vector3d(0,0,0),
            Vector3d(1,0,0),
            Vector3d(1,1,0),
            Vector3d(2,1,0),
            Vector3d(2,2,0),
            Vector3d(1,2,0),
            Vector3d(1,3,0),
            Vector3d(0,3,0),
        ]
    )


def test_triangle():
    face = Face(
        vertices=[
            Vector3d(0, 0, 0),
            Vector3d(1, 0, 0),
            Vector3d(0, 1, 0),
        ]
    )
    triangles = face.triangles
    assert len(triangles)==1


def test_quad():
    face = Face(
        vertices=[
            Vector3d(0, 0, 0),
            Vector3d(1, 0, 0),
            Vector3d(1, 1, 0),
            Vector3d(0, 1, 0),
        ]
    )
    assert len(face.triangles)==2


def test_triangle_count():
    face = create_complex_face()
    assert len(face.triangles)==len(face.vertices)-2


def test_all_are_triangles():
    face = create_complex_face()
    triangles = face.triangles
    for triangle in triangles:
        assert len(triangle)==3


def test_same_vertices():
    face = create_complex_face()
    triangles = face.triangles
    for triangle in triangles:
        for tv in triangle:
            assert id(tv) in [id(fv) for fv in face.vertices]


def test_same_area():
    face = create_complex_face()
    triangles_area = 0
    for triangle in face.triangles:
        area = Face(vertices=triangle).surfaceArea
        triangles_area += area
    assert math.fabs(triangles_area - face.surfaceArea)<0.001

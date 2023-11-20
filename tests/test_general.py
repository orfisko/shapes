from dk_geometry.enums import EdgeSharpness, FaceNormal
from dk_geometry.general import find_neighbour_faces
from dk_geometry.model import Face, Polyhedron, Vector3d


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

def test_neighbour_faces():
    reference_face = Face(
        vertices=[
            Vector3d(0, 0, 0),
            Vector3d(1, 0, 0),
            Vector3d(1, 1, 0),
            Vector3d(0, 1, 0),
        ]
    )
    assert len(find_neighbour_faces(Polyhedron(faces=[reference_face]),0))==0
    neighbour_face = Face(
        vertices=[
            reference_face.vertices[1],
            reference_face.vertices[0],
            Vector3d(0, 0, 1),
            Vector3d(1, 0, 1),
        ]
    )
    two_face_polyhedron = Polyhedron(faces=[reference_face,neighbour_face])
    assert find_neighbour_faces(two_face_polyhedron, 0)==[1]
    disjoint_face = Face(
        vertices=[
            Vector3d(0,0,1),
            Vector3d(1,0,1),
            Vector3d(1,1,1),
            Vector3d(0,1,1),
        ]
    )
    three_face_polyhedron = Polyhedron(
        faces=[
            reference_face,
            neighbour_face,
            disjoint_face,
        ]
    )
    assert find_neighbour_faces(three_face_polyhedron, 0)==[1]

def test_edge_sharpness():
    reference_face = Face(
        vertices=[
            Vector3d(0, 0, 0),
            Vector3d(1, 0, 0),
            Vector3d(1, 1, 0),
            Vector3d(0, 1, 0),
        ]
    )
    orthogonal_face = Face(
        vertices=[
            reference_face.vertices[1],
            reference_face.vertices[0],
            Vector3d(0, 0, 1),
            Vector3d(1, 0, 1),
        ]
    )
    assert reference_face.get_edge_sharpness(orthogonal_face)==EdgeSharpness.Orthogonal
    sharp_face = Face(
        vertices=[
            reference_face.vertices[1],
            reference_face.vertices[0],
            Vector3d(0, 1, 1),
            Vector3d(1, 1, 1),
        ]
    )
    assert reference_face.get_edge_sharpness(sharp_face)==EdgeSharpness.Sharp
    obtuse_face = Face(
        vertices=[
            reference_face.vertices[1],
            reference_face.vertices[0],
            Vector3d(0, -1, 1),
            Vector3d(1, -1, 1),
        ]
    )
    assert reference_face.get_edge_sharpness(obtuse_face)==EdgeSharpness.Obtuse

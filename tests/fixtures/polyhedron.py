from _pytest.fixtures import fixture

from dk_geometry.model import Face, Polyhedron, Vector3d


def polyhedron_cutout_fixture(
    left=float(0),
    right=float(1200),
    top=float(2500),
    bottom=float(0),
    back=float(-600),
    front=float(0),
    cutout_z=float(-300),
    cutout_x=float(500),
) -> Polyhedron:
    # Front Face vertices
    A = Vector3d(x=left, y=top, z=front)
    B = Vector3d(x=left, y=bottom, z=front)
    C = Vector3d(x=right, y=bottom, z=front)
    D = Vector3d(x=right, y=top, z=front)

    # Back Face vertices
    E = Vector3d(x=left, y=top, z=back)
    F = Vector3d(x=left, y=bottom, z=back)
    G = Vector3d(x=cutout_x, y=bottom, z=back)
    H = Vector3d(x=cutout_x, y=top, z=back)

    # Front cutout
    I = Vector3d(x=cutout_x, y=top, z=cutout_z)
    J = Vector3d(x=cutout_x, y=bottom, z=cutout_z)
    K = Vector3d(x=right, y=bottom, z=cutout_z)
    L = Vector3d(x=right, y=top, z=cutout_z)

    check = set(
        eval(f"'{letter}'") for letter in map(chr, range(ord("A"), ord("L") + 1))
    )
    assert len(check) == 12

    # Faces definition - counterclockwise -> threejs only renders one side of the face
    # 8 faces
    TOP = Face(vertices=[H, E, A, D, L, I])
    assert {vertex.y for vertex in TOP.vertices} == {top}
    RIGHT = Face(vertices=[L, D, C, K])
    assert {vertex.x for vertex in RIGHT.vertices} == {right}
    BOTTOM = Face(vertices=[F, G, J, K, C, B])
    assert {vertex.y for vertex in BOTTOM.vertices} == {bottom}
    LEFT = Face(vertices=[A, E, F, B])
    assert {vertex.x for vertex in LEFT.vertices} == {left}
    FRONT = Face(vertices=[A, B, C, D])
    assert {vertex.z for vertex in FRONT.vertices} == {front}
    BACK = Face(vertices=[E, H, G, F])
    assert {vertex.z for vertex in BACK.vertices} == {back}

    RIGHT_CUTOUT = Face(vertices=[G, H, I, J])
    assert {vertex.x for vertex in RIGHT_CUTOUT.vertices} == {cutout_x}
    FRONT_CUTOUT = Face(vertices=[K, J, I, L])
    assert {vertex.z for vertex in FRONT_CUTOUT.vertices} == {cutout_z}

    return Polyhedron(
        faces=[
            TOP,
            RIGHT,
            BOTTOM,
            LEFT,
            FRONT,
            BACK,
            RIGHT_CUTOUT,
            FRONT_CUTOUT,
        ]
    )


def polyhedron_cutout_slope_fixture(
    left=float(0),
    right=float(1200),
    top=float(2500),
    bottom=float(0),
    back=float(-600),
    front=float(0),
    angle_x=float(350),  # Start point in X of the angle on right hand side
    angle_y=float(2000),  # Start point in Y of the angle on right hand side
    cutout_z=float(-300),
    cutout_x=float(200),
    cutout_y=float(400),
) -> Polyhedron:
    # Front Face vertices
    A = Vector3d(x=left, y=top, z=front)
    B = Vector3d(x=left, y=bottom, z=front)
    C = Vector3d(x=right, y=bottom, z=front)
    D = Vector3d(x=right, y=angle_y, z=front)
    E = Vector3d(x=angle_x, y=top, z=front)

    # Back Face vertices
    F = Vector3d(x=left, y=top, z=back)
    G = Vector3d(x=angle_x, y=top, z=back)
    H = Vector3d(x=right, y=angle_y, z=back)
    I = Vector3d(x=right, y=cutout_y, z=back)
    J = Vector3d(x=cutout_x, y=cutout_y, z=back)
    K = Vector3d(x=cutout_x, y=bottom, z=back)
    L = Vector3d(x=left, y=bottom, z=back)

    # Left Face - No additional vertices needed
    # Right Face - 1 additional vertex
    M = Vector3d(x=right, y=cutout_y, z=cutout_z)
    N = Vector3d(x=right, y=bottom, z=cutout_z)
    O = Vector3d(x=cutout_x, y=bottom, z=cutout_z)
    P = Vector3d(x=cutout_x, y=cutout_y, z=cutout_z)

    check = set(
        eval(f"'{letter}'") for letter in map(chr, range(ord("A"), ord("P") + 1))
    )
    assert len(check) == 16

    # Faces definition - counterclockwise -> threejs only renders one side of the face
    # 10 faces
    TOP = Face(vertices=[A, E, G, F])
    assert {vertex.y for vertex in TOP.vertices} == {top}
    RIGHT = Face(vertices=[N, M, I, H, D, C])
    assert {vertex.x for vertex in RIGHT.vertices} == {right}
    BOTTOM = Face(vertices=[L, K, O, N, C, B])
    assert {vertex.y for vertex in BOTTOM.vertices} == {bottom}
    LEFT = Face(vertices=[F, L, B, A])
    assert {vertex.x for vertex in LEFT.vertices} == {left}
    FRONT = Face(vertices=[A, B, C, D, E])
    assert {vertex.z for vertex in FRONT.vertices} == {front}
    BACK = Face(vertices=[F, G, H, I, J, K, L])
    assert {vertex.z for vertex in BACK.vertices} == {back}

    RIGHT_ANGLED = Face(vertices=[D, H, G, E])
    RIGHT_CUTOUT = Face(vertices=[P, O, K, J])
    TOP_CUTOUT = Face(vertices=[I, M, P, J])
    FRONT_CUTOUT = Face(vertices=[M, N, O, P])

    return Polyhedron(
        faces=[
            TOP,
            RIGHT_ANGLED,
            RIGHT,
            BOTTOM,
            LEFT,
            FRONT,
            BACK,
            RIGHT_CUTOUT,
            TOP_CUTOUT,
            FRONT_CUTOUT,
        ]
    )


@fixture
def polyhedron_cutout():
    # For an idea on the modelled shape: please refer to cutout_* files in the pictures folder
    return polyhedron_cutout_fixture


@fixture
def polyhedron_cutout_sloped():
    # For an idea on the modelled shape: please refer to cutout_sloped_* files in the pictures folder
    return polyhedron_cutout_slope_fixture

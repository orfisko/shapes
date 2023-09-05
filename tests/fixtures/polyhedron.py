from _decimal import Decimal

from _pytest.fixtures import fixture

from model import Vertex, Face, Polyhedron


def polyhedron_cutout_fixture(
    left=Decimal(0),
    right=Decimal(1200),
    top=Decimal(2500),
    bottom=Decimal(0),
    back=Decimal(-600),
    front=Decimal(0),
    cutout_z=Decimal(-300),
    cutout_x=Decimal(500),
) -> Polyhedron:
    # Front Face vertices
    A = Vertex(x=left, y=top, z=front)
    B = Vertex(x=left, y=bottom, z=front)
    C = Vertex(x=right, y=bottom, z=front)
    D = Vertex(x=right, y=top, z=front)

    # Back Face vertices
    E = Vertex(x=left, y=top, z=back)
    F = Vertex(x=left, y=bottom, z=back)
    G = Vertex(x=cutout_x, y=bottom, z=back)
    H = Vertex(x=cutout_x, y=top, z=back)

    # Front cutout
    I = Vertex(x=cutout_x, y=top, z=cutout_z)
    J = Vertex(x=cutout_x, y=bottom, z=cutout_z)
    K = Vertex(x=right, y=bottom, z=cutout_z)
    L = Vertex(x=right, y=top, z=cutout_z)

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
    left=Decimal(0),
    right=Decimal(1200),
    top=Decimal(2500),
    bottom=Decimal(0),
    back=Decimal(-600),
    front=Decimal(0),
    angle_x=Decimal(350),  # Start point in X of the angle on right hand side
    angle_y=Decimal(2000),  # Start point in Y of the angle on right hand side
    cutout_z=Decimal(-300),
    cutout_x=Decimal(200),
    cutout_y=Decimal(400),
) -> Polyhedron:
    # Front Face vertices
    A = Vertex(x=left, y=top, z=front)
    B = Vertex(x=left, y=bottom, z=front)
    C = Vertex(x=right, y=bottom, z=front)
    D = Vertex(x=right, y=angle_y, z=front)
    E = Vertex(x=angle_x, y=top, z=front)

    # Back Face vertices
    F = Vertex(x=left, y=top, z=back)
    G = Vertex(x=angle_x, y=top, z=back)
    H = Vertex(x=right, y=angle_y, z=back)
    I = Vertex(x=right, y=cutout_y, z=back)
    J = Vertex(x=cutout_x, y=cutout_y, z=back)
    K = Vertex(x=cutout_x, y=bottom, z=back)
    L = Vertex(x=left, y=bottom, z=back)

    # Left Face - No additional vertices needed
    # Right Face - 1 additional vertex
    M = Vertex(x=right, y=cutout_y, z=cutout_z)
    N = Vertex(x=right, y=bottom, z=cutout_z)
    O = Vertex(x=cutout_x, y=bottom, z=cutout_z)
    P = Vertex(x=cutout_x, y=cutout_y, z=cutout_z)

    check = set(
        eval(f"'{letter}'") for letter in map(chr, range(ord("A"), ord("P") + 1))
    )
    assert len(check) == 16

    # Faces definition - counterclockwise -> threejs only renders one side of the face
    # 10 faces
    TOP = Face(vertices=[F, G, E, A])
    assert {vertex.y for vertex in TOP.vertices} == {top}
    RIGHT = Face(vertices=[C, D, H, I, M, N])
    assert {vertex.x for vertex in RIGHT.vertices} == {right}
    BOTTOM = Face(vertices=[B, C, N, O, K, L])
    assert {vertex.y for vertex in BOTTOM.vertices} == {bottom}
    LEFT = Face(vertices=[A, B, L, F])
    assert {vertex.x for vertex in LEFT.vertices} == {left}
    FRONT = Face(vertices=[E, D, C, B, A])
    assert {vertex.z for vertex in FRONT.vertices} == {front}
    BACK = Face(vertices=[L, K, J, I, H, G, F])
    assert {vertex.z for vertex in BACK.vertices} == {back}

    RIGHT_ANGLED = Face(vertices=[E, G, H, D])
    RIGHT_CUTOUT = Face(vertices=[J, K, O, P])
    TOP_CUTOUT = Face(vertices=[J, P, M, I])
    FRONT_CUTOUT = Face(vertices=[P, O, N, M])

    return Polyhedron(
        faces=[
            TOP,
            RIGHT,
            BOTTOM,
            LEFT,
            FRONT,
            BACK,
            RIGHT_ANGLED,
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

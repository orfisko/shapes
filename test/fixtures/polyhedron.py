from _decimal import Decimal

from _pytest.fixtures import fixture

from model import Vertex, Face, Polyhedron


@fixture
def polyhedron_cutout():
    # For an idea on the modelled shape: please refer to cutout_* files in the pictures folder
    def _fixture(
        left=Decimal(0),
        right=Decimal(1200),
        top=Decimal(2500),
        bottom=Decimal(0),
        back=Decimal(600),
        front=Decimal(0),
        cutout_z=Decimal(300),
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
        TOP = Face(vertices=[H, E, A, D, L, I], index=0)
        assert {vertex.y for vertex in TOP.vertices} == {top}
        RIGHT = Face(vertices=[L, D, C, K], index=1)
        assert {vertex.x for vertex in RIGHT.vertices} == {right}
        BOTTOM = Face(vertices=[F, G, J, K, C, B], index=2)
        assert {vertex.y for vertex in BOTTOM.vertices} == {bottom}
        LEFT = Face(vertices=[A, E, F, B], index=3)
        assert {vertex.x for vertex in LEFT.vertices} == {left}
        FRONT = Face(vertices=[A, B, C, D], index=4)
        assert {vertex.z for vertex in FRONT.vertices} == {front}
        BACK = Face(vertices=[E, H, G, F], index=5)
        assert {vertex.z for vertex in BACK.vertices} == {back}

        RIGHT_CUTOUT = Face(vertices=[G, H, I, J], index=6)
        assert {vertex.x for vertex in RIGHT_CUTOUT.vertices} == {cutout_x}
        FRONT_CUTOUT = Face(vertices=[K, J, I, L], index=7)
        assert {vertex.z for vertex in FRONT_CUTOUT.vertices} == {cutout_z}

        return Polyhedron(
            faces=[
                FRONT,
                BACK,
                LEFT,
                RIGHT,
                TOP,
                BOTTOM,
                RIGHT_CUTOUT,
                FRONT_CUTOUT,
            ]
        )

    return _fixture


@fixture
def polyhedron_cutout_sloped():
    # For an idea on the modelled shape: please refer to cutout_sloped_* files in the pictures folder
    def _fixture(
        left=Decimal(0),
        right=Decimal(1200),
        top=Decimal(2500),
        bottom=Decimal(0),
        back=Decimal(600),
        front=Decimal(0),
        angle_x=Decimal(350),  # Start point in X of the angle on right hand side
        angle_y=Decimal(2000),  # Start point in Y of the angle on right hand side
        cutout_z=Decimal(300),
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
        O = Vertex(x=cutout_z, y=bottom, z=cutout_z)
        P = Vertex(x=cutout_z, y=cutout_y, z=cutout_z)

        check = set(
            eval(f"'{letter}'") for letter in map(chr, range(ord("A"), ord("P") + 1))
        )
        assert len(check) == 16

        # Faces definition - counterclockwise -> threejs only renders one side of the face
        # 10 faces
        TOP = Face(vertices=[F, G, E, A], index=0)
        assert {vertex.y for vertex in TOP.vertices} == {top}
        RIGHT = Face(vertices=[C, D, H, I, M, N], index=1)
        assert {vertex.x for vertex in RIGHT.vertices} == {right}
        BOTTOM = Face(vertices=[B, C, N, O, K, L], index=2)
        assert {vertex.y for vertex in BOTTOM.vertices} == {bottom}
        LEFT = Face(vertices=[A, B, L, F], index=3)
        assert {vertex.x for vertex in LEFT.vertices} == {left}
        FRONT = Face(vertices=[A, B, C, D, E], index=4)
        assert {vertex.z for vertex in FRONT.vertices} == {front}
        BACK = Face(vertices=[F, G, H, I, J, K, L], index=5)
        assert {vertex.z for vertex in BACK.vertices} == {back}

        RIGHT_ANGLED = Face(vertices=[E, G, H, D], index=6)
        RIGHT_CUTOUT = Face(vertices=[J, K, O, P], index=7)
        TOP_CUTOUT = Face(vertices=[J, P, M, I], index=8)
        FRONT_CUTOUT = Face(vertices=[P, O, N, M], index=9)

        return Polyhedron(
            faces=[
                FRONT,
                BACK,
                LEFT,
                RIGHT,
                TOP,
                BOTTOM,
                RIGHT_ANGLED,
                RIGHT_CUTOUT,
                TOP_CUTOUT,
                FRONT_CUTOUT,
            ]
        )

    return _fixture

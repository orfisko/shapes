import math
from _decimal import Decimal
from typing import Optional

import pytest

from dk_geometry.enums import FaceNormal
from dk_geometry.model import Vector3d
from dk_geometry.offset import generate_delta_polyhedra, generate_offset
from dk_geometry.utils import *
from dk_geometry.general import calculate_signed_distance_to_plane, create_cube


def prioritize(
    outer, face_indices, super_important_face_indices: Optional[list[int]] = None
) -> list[int]:
    """
    Prioritisation function which returns prioritisation for each passed face
    Args:
        outer: outer polyhedron
        face_indices: index values passed by the calling algo
        super_important_face_indices: indices of faces which should always be prioritised over others
    Returns:
        List of priorities where the order relates to the order of the passed face indices
    """
    # 0 - horizontal
    # 1 - side
    # 2 - front/back
    # 3 - sloped
    # 4 - super important
    if super_important_face_indices is None:
        super_important_face_indices = []
    types = []
    for face_index in face_indices:
        normal = outer.faces[face_index].plane.normal
        if face_index in super_important_face_indices:
            types.append(4)
        elif math.fabs(normal.y) > normal.length * 0.99:
            types.append(0)
        elif math.fabs(normal.x) > normal.length * 0.99:
            types.append(1)
        elif math.fabs(normal.z) > normal.length * 0.99:
            types.append(2)
        else:
            types.append(3)
    priorities = []
    for type in types:
        if type == 0:
            priorities.append(3)
        elif type == 1:
            priorities.append(2)
        elif type == 2:
            priorities.append(1)
        elif type == 4:
            priorities.append(4)  # otherwise we'll get a face cut
        else:  # sloped takes 2 or 3 whatever is present
            priorities.append(3 if 0 in types else 2)
    return priorities


@pytest.mark.skip(reason="only for visual inspection")
def test_panel_generation(polyhedron_cutout_sloped):
    outer = polyhedron_cutout_sloped()
    inner = generate_offset(poly=outer, offset=-10)

    def local_prioritize(face_indices):
        return prioritize(outer, face_indices, [7, 8, 9])

    panels = generate_delta_polyhedra(outer, inner, local_prioritize)
    export_to_obj(outer, "outer.obj")
    export_to_obj(inner, "inner.obj")
    for panel_index, panel in panels.items():
        export_to_obj(panel, "panel." + str(panel_index) + ".obj")


def test_panel_generation_offsetmap(polyhedron_cutout_sloped):
    outer = polyhedron_cutout_sloped()
    inner = generate_offset(poly=outer, offset_map={0: -50, 1: -20, 2: -25})

    def local_prioritize(face_indices):
        return prioritize(outer, face_indices, [7, 8, 9])

    panels = generate_delta_polyhedra(outer, inner, local_prioritize)

    assert len(panels) == 3


def test_cut_check_for_concave_corners(polyhedron_cutout_sloped):
    outer = polyhedron_cutout_sloped()
    inner = generate_offset(poly=outer, offset=-10)

    def local_prioritize(face_indices):
        return prioritize(outer, face_indices, [])

    exception = False
    try:
        panels = generate_delta_polyhedra(outer, inner, local_prioritize)
    except ValueError:
        exception = True
    assert (
        exception
    ), "face cut caused by priorities on a concave corner has not been detected"


def test_that_panels_are_between_inner_and_outer(polyhedron_cutout_sloped):
    outer = polyhedron_cutout_sloped()
    inner = generate_offset(poly=outer, offset=-10)

    def local_prioritize(face_indices):
        return prioritize(outer, face_indices, [7, 8, 9])

    panels = generate_delta_polyhedra(outer, inner, local_prioritize)
    for face_index, panel in panels.items():
        outer_plane = outer.faces[face_index].plane
        inner_plane = inner.faces[face_index].plane
        for panel_face in panel.faces:
            for vertex in panel_face.vertices:
                assert (
                    calculate_signed_distance_to_plane(vertex, outer_plane) <= 0.01
                ), f"panel #{face_index} is in front of the corresponding outer face"
                assert (
                    calculate_signed_distance_to_plane(vertex, inner_plane) >= -0.01
                ), f"panel #{face_index} is behind the corresponding inner face"


def test_that_prioritization_for_one_face_is_not_asked(polyhedron_cutout_sloped):
    outer = polyhedron_cutout_sloped()
    inner = generate_offset(poly=outer, offset_map={0: -50})

    def local_prioritize(face_indices):
        assert (
            False
        ), "meaningless prioritization has been requested when only one face needs a panel"
        return prioritize(outer, face_indices, [7, 8, 9])

    generate_delta_polyhedra(outer, inner, local_prioritize)


def test_that_prioritization_skips_faces_without_panels(polyhedron_cutout_sloped):
    outer = polyhedron_cutout_sloped()
    inner = generate_offset(poly=outer, offset_map={0: -50, 1: -50})

    def local_prioritize(face_indices):
        assert (
            len(face_indices) == 2
        ), "a face not needing a panel has been asked to prioritize"
        return prioritize(outer, face_indices, [7, 8, 9])

    generate_delta_polyhedra(outer, inner, local_prioritize)


def test_check_facenormals():
    outer = create_cube(centre=Vector3d(50, 50, 50), size=float(100))
    inner = generate_offset(poly=outer, offset_map={3: -20})

    min_z_outer = outer.get_faces_by_facenormal(FaceNormal.F)[0].min_z
    max_z_outer = outer.get_faces_by_facenormal(FaceNormal.F)[0].max_z

    def local_prioritize(face_indices):
        return prioritize(outer, face_indices)

    panels = generate_delta_polyhedra(outer, inner, local_prioritize)

    assert len(panels) == 1
    panel = list(panels.values())[0]
    min_z_panel = panel.get_faces_by_facenormal(FaceNormal.F)[0].min_z
    max_z_panel = panel.get_faces_by_facenormal(FaceNormal.F)[0].max_z
    assert min_z_panel == min_z_outer
    assert max_z_panel == max_z_outer


def test_get_index_by_facenormal():
    cube = create_cube(centre=Vector3d(50, 50, 50), size=float(100))
    idxs = cube.get_face_indices_by_facenormal(FaceNormal.B)
    assert len(idxs) == 1

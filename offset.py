from _decimal import Decimal
from typing import Optional

from model import Polyhedron


def apply_offset(
    polyhedron: Polyhedron,
    offset: Optional[Decimal] = None,
    offset_map: Optional[dict[int, Decimal]] = None,
) -> Polyhedron:
    """
    Generates a new polyhedron with the offset applied to the vertices. The offset is applied to all faces unless
    an offset_map is supplied. The offset_map is a dictionary with the face index as key and the offset as value.
    Args:
        polyhedron: the polyhedron for which the offset needs to be applied
        offset: global offset for all faces
        offset_map: offset to apply on the face with the specified index as key

    Returns:
        a new polyhedron with the offset applied
    """
    if not any((offset, offset_map)):
        raise ValueError("Either offset or offset_map needs to be supplied")
    if offset_map is None:
        offset_map = dict()
    if offset is None and len(offset_map) != len(polyhedron.faces):
        raise ValueError(
            "When offset is not supplied, the offset_map needs to contain an offset for each face"
        )
    # Fill the offset_map with the offset if it is not supplied.
    offset_map.update(
        {
            loc: offset
            for loc in range(0, len(polyhedron.faces))
            if loc not in offset_map.keys()
        }
    )

    # Calculate normalized normals for each vertex given the supplied faces and store it in the Vertex object for later use
    # In the model a Normal class is available to store these values

    # Depending on whether or not the face should be offset, correct the normal. For Vertex A, I would expect a normal
    # to appear here wherby the shift in Z is being put to 0 in case the front face does not need to be offset

    # Apply the normal on the vertex

    # Return the polyhedron with an equal number of faces and the vertices in the same order as when they were sent in

    return polyhedron

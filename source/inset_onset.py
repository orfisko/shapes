from enum import Enum
from typing import Dict


class ConnectionType(Enum):
    ONSET = 0
    INSET = 90
    MITRE = 45


def generate_offset_polyhedrons(polyhedron, offset, offset_map, connection_map):
    """I would order the faces as shown below
    faces = [
    0    TOP,
    1    RIGHT_ANGLED,
    2    RIGHT,
    3    BOTTOM,
    4    LEFT,
    5    FRONT,
    6    BACK,
    7    RIGHT_CUTOUT,
    8    TOP_CUTOUT,
    9    FRONT_CUTOUT,
    ]"""

    """The default connection of:
        - a top panel resting on the side panels 
        - side panel supported by the bottom panel
        - back panel in between side and top panels
    would look like this"""
    connection_map = {
        # Top -> angled
        (0, 1): ConnectionType.ONSET,
        # Top -> left
        (0, 4): ConnectionType.ONSET,
        (3, 2): ConnectionType.ONSET,
        (3, 4): ConnectionType.ONSET,
        (0, 6): ConnectionType.ONSET,
        (3, 6): ConnectionType.ONSET,
        (2, 6): ConnectionType.ONSET,
        (4, 6): ConnectionType.ONSET,
        (1, 6): ConnectionType.ONSET,
    }

    """In case the the angled panel needs to connect to the top panel by just connecting the original point and 
    corresponding offset points, we get, simply remove the corresponding pair"""
    connection_map = {
        # Top -> left
        (0, 4): ConnectionType.ONSET,
        (3, 2): ConnectionType.ONSET,
        (3, 4): ConnectionType.ONSET,
        (0, 6): ConnectionType.ONSET,
        (3, 6): ConnectionType.ONSET,
        (2, 6): ConnectionType.ONSET,
        (4, 6): ConnectionType.ONSET,
        (1, 6): ConnectionType.ONSET,
    }
    connection_map: Dict[tuple[int, int], ConnectionType] = {}

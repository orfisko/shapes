from __future__ import annotations

from enum import Enum


class Orientation(Enum):
    """Indicates which absolute normals are different from 0"""

    X = "X"  # Vertical - typically used for tops, bottoms and shelves
    Y = "Y"  # Horizontal - typically used for sides
    Z = "Z"  # Depth - typically used for front and backpanels
    XY = "XY"  # Sloped panels in XY
    YZ = "YZ"  # Sloped panels in YZ
    OTHER = "OTHER"  # Other orientation

    def __neg__(self):
        if self.name == "X":
            return Orientation.Y
        if self.name == "Y":
            return Orientation.X
        else:
            raise NotImplemented

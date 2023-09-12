from __future__ import annotations

from enum import Enum


class Orientation(str, Enum):
    """Indicates which absolute normals are different from 0"""

    L = "L"  # Left
    R = "R"  # Right
    T = "T"  # Top
    B = "B"  # Bottom
    F = "F"  # Front
    BK = "BK"  # Back
    L_BK = "L_BK"  # Left back
    R_BK = "R_BK"  # Right back
    T_BK = "T_BK"  # Top back
    L_T = "L_T"  # Left top
    R_T = "R_T"  # Right top
    OTHER = "OTHER"

    @classmethod
    def _missing_(cls, value):
        return cls.OTHER

    def __neg__(self):
        if self.name == "L":
            return Orientation.R
        if self.name == "R":
            return Orientation.L
        if self.name == "T":
            return Orientation.B
        if self.name == "B":
            return Orientation.T
        if self.name == "F":
            return Orientation.BK
        if self.name == "BK":
            return Orientation.F
        else:
            raise NotImplemented

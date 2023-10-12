from __future__ import annotations

from enum import Enum


class FaceNormal(Enum):
    """Indicates which absolute normals of the face are different from 0"""

    L = "L"  # Left
    R = "R"  # Right
    T = "T"  # Top
    B = "B"  # Bottom
    F = "F"  # Front
    BK = "BK"  # Back
    L_BK = "L_BK"  # Left back
    L_F = "L_F"  # Left front
    R_BK = "R_BK"  # Right back
    R_F = "R_F"  # Right front
    T_BK = "T_BK"  # Top back
    T_F = "T_F"  # Top front
    L_T = "L_T"  # Left top
    L_B = "L_B"  # Left bottom
    R_T = "R_T"  # Right top
    R_B = "R_B"  # Right bottom
    OTHER = "OTHER"

    def __iter__(self):
        return iter([FaceNormal(normal) for normal in self.name.split("_")])

    def __len__(self):
        return len(self.name.split("_"))

    @classmethod
    def _missing_(cls, value):
        return cls.OTHER

    @classmethod
    def from_stringlist(cls, str_list: list[str]) -> FaceNormal:
        if len(str_list) == 1:
            return FaceNormal(str_list[0])
        else:
            str_list.sort()
            face: FaceNormal
            for face in list(cls):
                face_str_list = face.name.split("_")
                if len(face_str_list) > 1:
                    face_str_list.sort()
                    face_str = "".join(face_str_list)
                    if face_str == "".join(str_list):
                        return face

    def __neg__(self) -> FaceNormal:
        """Should return the opposite facenormal. This should allow to identify the face parallel to the one
        with orientation self"""
        opposites = [
            "R",
            "L",
            "B",
            "T",
            "BK",
            "F",
            "L_F",
            "L_BK",
            "R_F",
            "R_BK",
            "T_F",
            "T_BK",
            "L_B",
            "L_T",
            "R_B",
            "R_T",
            "OTHER",
        ]

        return FaceNormal(opposites[list(FaceNormal).index(self)])

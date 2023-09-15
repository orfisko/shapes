from __future__ import annotations

from enum import Enum


class FaceNormal(str, Enum):
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
                face_str_list = face.split("_")
                if len(face_str_list) > 1:
                    face_str_list.sort()
                    face_str = "".join(face_str_list)
                    if face_str == "".join(str_list):
                        return face

    def normal_in_facenormal(self, *args: FaceNormal) -> bool:
        """
        Function to allow checking which of the main 6 normals are at present in the normal instance.
        Args:
            *args: normals to check against.
        Returns:
            True if any of the normals is present in the facenormal, False otherwise
        """
        pure_normals = [
            FaceNormal.L,
            FaceNormal.R,
            FaceNormal.T,
            FaceNormal.B,
            FaceNormal.F,
            FaceNormal.BK,
        ]
        for normal in args:
            assert normal in pure_normals, (
                "This function only allows to check if a facenormal is exposed to one of the "
                "6 major normal directions"
            )
        for iter_normal in self.name.split("_"):
            if FaceNormal(iter_normal) in args:
                return True
        return False

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

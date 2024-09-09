# Copyright: 2024 BV De Kastenman
from __future__ import annotations

from enum import Enum

from dk_common.model.enums import Language


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

    @classmethod
    def _missing_(cls, value):
        return cls.OTHER

    def __ge__(self, other):
        return self.value >= other.value

    def __le__(self, other):
        return self.value <= other.value

    @classmethod
    def from_stringlist(cls, str_list: list[str]) -> FaceNormal:
        if len(str_list) == 1:
            return FaceNormal(str_list[0])
        else:
            str_set = set(str_list)
            for idx, face in enumerate(list(cls)):
                iter_face_set: set[FaceNormal] = {
                    face_n.name for face_n in face.split()
                }
                if iter_face_set == str_set:
                    return list(cls)[idx]

    def split(self) -> list[FaceNormal]:
        return [FaceNormal(split_name) for split_name in self.name.split("_")]

    def __neg__(self) -> FaceNormal:
        """Should return the opposite facenormal. This should allow to identify the face parallel to the one
        with orientation self"""
        opposite_map = {
            "L": "R",
            "R": "L",
            "B": "T",
            "T": "B",
            "BK": "F",
            "F": "BK",
            "OTHER": "OTHER",
        }
        return FaceNormal(
            "_".join(
                [opposite_map[face_normal] for face_normal in self.name.split("_")]
            )
        )

    def in_language(self, language: Language = Language.DUTCH):
        nl_lang_dict = {
            "L": "LINKS",  # Left
            "R": "RECTHS",  # Right
            "T": "BOVEN",  # Top
            "B": "ONDER",  # Bottom
            "F": "VOORAAN",  # Front
            "BK": "ACHTERAAN",  # Back
            "OTHER": "",
        }
        if language == Language.DUTCH:
            return " ".join([nl_lang_dict[part] for part in self.split()])
        else:
            raise NotImplementedError(f"Language {language.name} not implemented")


class AngleType(Enum):
    SHARP = "SHARP"
    ORTHOGONAL = "ORTHOGONAL"
    OBTUSE = "OBTUSE"

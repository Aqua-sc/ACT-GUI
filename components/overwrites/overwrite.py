from dataclasses import dataclass
from enum import Enum
from typing import List

class OVERWRITE_TYPE(Enum):
    DROPDOWN_STR = 1
    RANGED_FP = 2

@dataclass
class OverwriteInfo:
    field: str
    type: OVERWRITE_TYPE
    range_min: float | None = None
    range_max: float | None = None
    values_str : List[str] | None = None
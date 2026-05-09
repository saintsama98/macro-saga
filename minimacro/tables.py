from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class MNTEntry:
    name: str
    num_pp: int = 0
    num_kp: int = 0
    mdt_ptr: int = 0
    kpdt_ptr: int = 0
    ala_ptr: int = 0


@dataclass
class MDTEntry:
    text: str


@dataclass
class KPDTabEntry:
    name: str
    default: str


@dataclass
class ALAEntry:
    formal: str
    actual: str


@dataclass
class Tables:
    mnt: List[MNTEntry] = field(default_factory=list)
    mdt: List[MDTEntry] = field(default_factory=list)
    kpdtab: List[KPDTabEntry] = field(default_factory=list)
    ala: List[ALAEntry] = field(default_factory=list)
    intermediate: List[str] = field(default_factory=list)

    def find_macro(self, name: str) -> Optional[MNTEntry]:
        target = name.upper()
        for m in self.mnt:
            if m.name.upper() == target:
                return m
        return None

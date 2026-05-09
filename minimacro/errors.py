from dataclasses import dataclass, field
from typing import List


@dataclass
class ErrorReporter:
    errors: List[str] = field(default_factory=list)

    def add(self, msg: str) -> None:
        self.errors.append(msg)

    def has_errors(self) -> bool:
        return bool(self.errors)

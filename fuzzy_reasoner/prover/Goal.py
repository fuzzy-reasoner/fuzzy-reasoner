from __future__ import annotations
from dataclasses import dataclass

from fuzzy_reasoner.types.Atom import Atom
from fuzzy_reasoner.types.Rule import Rule


@dataclass(frozen=True, eq=False)
class Goal:
    statement: Atom
    scope: Rule

    def __str__(self) -> str:
        return f"GOAL:{self.statement}"

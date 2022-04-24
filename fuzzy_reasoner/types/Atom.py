from __future__ import annotations
from dataclasses import dataclass

from .Variable import Variable
from .Constant import Constant
from .Predicate import Predicate


@dataclass(frozen=True, eq=False)
class Atom:
    predicate: Predicate
    terms: tuple[Constant | Variable, ...]

    def __str__(self) -> str:
        terms_str = ",".join([term.__str__() for term in self.terms])
        return f"{self.predicate}({terms_str})"

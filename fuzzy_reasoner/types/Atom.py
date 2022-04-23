from __future__ import annotations
from dataclasses import dataclass

from .Variable import Variable
from .Constant import Constant
from .Predicate import Predicate


@dataclass(frozen=True, eq=False)
class Atom:
    predicate: Predicate
    terms: tuple[Constant | Variable]

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .Rule import Rule
from .Atom import Atom


@dataclass(frozen=True, eq=False)
class ProofGraphUnificationNode:
    goal: Atom
    rule: Rule
    unification_similarity: float
    overall_similarity: float
    child: Optional[ProofGraphConjunctionNode] = None


@dataclass(frozen=True, eq=False)
class ProofGraphConjunctionNode:
    goals: tuple[Atom, ...]
    children: tuple[ProofGraphUnificationNode, ...]


@dataclass(frozen=True, eq=False)
class ProofGraph:
    goal: Atom
    head: ProofGraphUnificationNode

    @property
    def similarity_score(self) -> float:
        return self.head.overall_similarity

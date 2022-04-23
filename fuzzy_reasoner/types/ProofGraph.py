from __future__ import annotations
from dataclasses import dataclass

from .Rule import Rule
from .Atom import Atom


@dataclass(frozen=True, eq=False)
class ProofGraphNode:
    rule: Rule
    children: tuple[ProofGraphNode]


@dataclass(frozen=True, eq=False)
class ProofGraph:
    goal: Atom
    steps: ProofGraphNode

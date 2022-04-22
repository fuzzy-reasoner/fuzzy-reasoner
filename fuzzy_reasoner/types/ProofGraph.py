from dataclasses import dataclass
from typing import List

from .Rule import Rule
from .Atom import Atom


@dataclass
class ProofGraphNode:
    rule: Rule
    children: List["ProofGraphNode"]


@dataclass
class ProofGraph:
    goal: Atom
    steps: ProofGraphNode

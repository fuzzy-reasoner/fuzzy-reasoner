from dataclasses import dataclass

from fuzzy_reasoner.types.Atom import Atom


@dataclass
class ProofState:
    goal: Atom
    similarity: float = 1.0

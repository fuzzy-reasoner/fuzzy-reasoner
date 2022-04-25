from __future__ import annotations
from dataclasses import dataclass
from immutables import Map
from fuzzy_reasoner.prover.operations.substitution import SubstitutionsMap

from fuzzy_reasoner.types.Rule import Rule


@dataclass
class ProofState:
    similarity: float = 1.0
    substitutions: SubstitutionsMap = Map()
    # TODO: allow re-using rules, find another way to avoid cycles in the proof graph
    available_rules: frozenset[Rule] = frozenset()

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from immutables import Map

from fuzzy_reasoner.prover.operations.substitution import SubstitutionsMap, resolve_term
from fuzzy_reasoner.types.Constant import Constant
from fuzzy_reasoner.types.Rule import Rule
from fuzzy_reasoner.types.Atom import Atom
from fuzzy_reasoner.types.Variable import Variable


@dataclass(frozen=True, eq=False)
class ProofGraphNode:
    goal: Atom
    rule: Rule
    unification_similarity: float
    overall_similarity: float
    children: Optional[list[ProofGraphNode]] = None
    substitutions: SubstitutionsMap = Map()


@dataclass(frozen=True, eq=False)
class ProofGraph:
    head: ProofGraphNode

    @property
    def goal(self) -> Atom:
        return self.head.goal

    @property
    def similarity_score(self) -> float:
        return self.head.overall_similarity

    @property
    def variable_bindings(self) -> Map[Variable, Constant | Variable]:
        bindings: dict[Variable, Constant | Variable] = {}
        for term in self.goal.terms:
            if isinstance(term, Variable):
                bindings[term] = resolve_term(
                    term, self.head.rule, self.head.substitutions
                )
        return Map(bindings)

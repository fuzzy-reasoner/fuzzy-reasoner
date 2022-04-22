from typing import Sequence, Set, Union

from fuzzy_reasoner.types.Atom import Atom
from fuzzy_reasoner.types.ProofGraph import ProofGraph
from fuzzy_reasoner.types.Rule import Rule


class SLDProver:
    max_proof_depth: int
    min_similarity_threshold: float
    rules: Set[Rule]

    def __init__(
        self,
        rules: Sequence[Rule] = [],
        max_proof_depth: int = 10,
        min_similarity_threshold: float = 0.5,
    ) -> None:
        self.max_proof_depth = max_proof_depth
        self.min_similarity_threshold = min_similarity_threshold
        self.rules = set(rules)

    def prove(
        goal: Atom, dynamic_rules: Sequence[Rule] = []
    ) -> Union[ProofGraph, None]:
        pass

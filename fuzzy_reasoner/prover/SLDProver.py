from __future__ import annotations
from typing import Optional, Sequence, Set
from fuzzy_reasoner.prover.ProofState import ProofState
from fuzzy_reasoner.prover.operations.recurse import recurse
from fuzzy_reasoner.similarity import SimilarityFunc, cosine_similarity

from fuzzy_reasoner.types.Atom import Atom
from fuzzy_reasoner.types.ProofGraph import ProofGraph
from fuzzy_reasoner.types.Rule import Rule


class SLDProver:
    max_proof_depth: int
    min_similarity_threshold: float
    rules: frozenset[Rule]
    similarity_func: Optional[SimilarityFunc]

    def __init__(
        self,
        rules: Sequence[Rule] = [],
        max_proof_depth: int = 10,
        min_similarity_threshold: float = 0.5,
        similarity_func: Optional[SimilarityFunc] = cosine_similarity,
    ) -> None:
        self.max_proof_depth = max_proof_depth
        self.min_similarity_threshold = min_similarity_threshold
        self.rules = frozenset(rules)
        self.similarity_func = similarity_func

    def prove(
        self, goal: Atom, dynamic_rules: Optional[Sequence[Rule]] = None
    ) -> ProofGraph | None:
        result_graphs = self.prove_all(goal, dynamic_rules)
        return result_graphs[0] if len(result_graphs) > 0 else None

    def prove_all(
        self, goal: Atom, dynamic_rules: Optional[Sequence[Rule]] = None
    ) -> list[ProofGraph]:
        rules = self.rules.union(dynamic_rules) if dynamic_rules else self.rules
        successful_proof_states, successful_graph_nodes = recurse(
            goal,
            self.max_proof_depth,
            ProofState(),
            self.similarity_func,
            self.min_similarity_threshold,
        )
        if not successful_graph_nodes:
            return []
        graphs = [ProofGraph(goal, node) for node in successful_graph_nodes]
        return sorted(graphs, key=lambda graph: graph.similarity_score, reverse=True)

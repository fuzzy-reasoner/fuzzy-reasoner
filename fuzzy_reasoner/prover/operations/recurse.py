from __future__ import annotations
from typing import Optional

from fuzzy_reasoner.prover.Goal import Goal
from fuzzy_reasoner.prover.ProofState import ProofState
from fuzzy_reasoner.prover.operations.unify import unify
from fuzzy_reasoner.prover.ProofGraph import (
    ProofGraphNode,
)
from fuzzy_reasoner.similarity import SimilarityFunc


def recurse(
    goal: Goal,
    max_depth: int,
    proof_state: ProofState,
    similarity_func: Optional[SimilarityFunc],
    min_similarity_threshold: float,
) -> tuple[list[ProofState], list[ProofGraphNode]]:
    """
    Operation corresponding to OR from "end-to-end differentiable proving"
    This will try to unify every available rule against the current goal
    and will return the resulting ProofStates
    """
    next_proof_states: list[ProofState] = []
    graph_nodes: list[ProofGraphNode] = []
    for rule in proof_state.available_rules:
        unify_result = unify(
            rule,
            goal,
            proof_state.substitutions,
            similarity_func=similarity_func,
            min_similarity_threshold=min_similarity_threshold,
        )
        # if unification failed, just skip this rule
        if not unify_result:
            continue
        substitutions, similarity = unify_result
        overall_similarity = min(similarity, proof_state.similarity)
        next_proof_state = ProofState(
            similarity=overall_similarity,
            substitutions=substitutions,
            available_rules=proof_state.available_rules.difference([rule]),
        )
        # if there's more atoms in the body of the rule, we'll need to AND them to continue the proof
        if rule.body:
            subgoals = tuple(Goal(atom, scope=rule) for atom in rule.body)
            child_proof_states, child_graph_nodes_lists = join(
                subgoals,
                max_depth,
                next_proof_state,
                similarity_func,
                min_similarity_threshold,
            )
            if not child_proof_states:
                continue
            next_proof_states += child_proof_states
            for child_node_list, child_proof_state in zip(
                child_graph_nodes_lists, child_proof_states
            ):
                graph_nodes.append(
                    ProofGraphNode(
                        goal.statement,
                        rule,
                        unification_similarity=similarity,
                        overall_similarity=child_proof_state.similarity,
                        substitutions=child_proof_state.substitutions,
                        children=child_node_list,
                    )
                )
        else:
            next_proof_states.append(next_proof_state)
            graph_nodes.append(
                ProofGraphNode(
                    goal.statement,
                    rule,
                    unification_similarity=similarity,
                    overall_similarity=overall_similarity,
                    substitutions=substitutions,
                )
            )
    return next_proof_states, graph_nodes


def join(
    goals: tuple[Goal, ...],
    max_depth: int,
    proof_state: ProofState,
    similarity_func: Optional[SimilarityFunc],
    min_similarity_threshold: float,
) -> tuple[list[ProofState], list[list[ProofGraphNode]]]:
    """
    Operation corresponding to AND from "end-to-end differentiable proving"

    This will attempt to prove all the subgoals and return the resulting proofstates
    """

    if max_depth <= 0:
        return [], []

    proof_states: list[ProofState] = []
    conjunction_nodes: list[list[ProofGraphNode]] = []
    first_goal = goals[0]
    remaining_goals = goals[1:]
    recursed_proof_states, recursed_graph_nodes = recurse(
        first_goal,
        max_depth - 1,
        proof_state,
        similarity_func,
        min_similarity_threshold,
    )
    # if we can't prove the first step of AND, the whole thing fails
    if not recursed_proof_states:
        return [], []
    # no more goals to prove, so every successful proof of the main goal is sufficient
    if len(remaining_goals) == 0:
        conjunction_nodes = [recursed_graph_nodes]
        return recursed_proof_states, conjunction_nodes
    for recursed_proof_state, recursed_graph_node in zip(
        recursed_proof_states, recursed_graph_nodes
    ):
        joined_proof_states, joined_graph_nodes_lists = join(
            remaining_goals,
            max_depth,
            recursed_proof_state,
            similarity_func,
            min_similarity_threshold,
        )
        if not joined_proof_states:
            continue
        proof_states += joined_proof_states
        for joined_graph_nodes in joined_graph_nodes_lists:
            conjunction_nodes.append([recursed_graph_node, *joined_graph_nodes])

    return proof_states, conjunction_nodes

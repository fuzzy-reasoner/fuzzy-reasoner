from __future__ import annotations
from typing import Callable, Any, Optional
from immutables import Map
from numpy.typing import NDArray
from fuzzy_reasoner.prover.Goal import Goal

from fuzzy_reasoner.prover.ProofState import ProofState, SubstitutionsMap
from fuzzy_reasoner.similarity import SimilarityFunc
from fuzzy_reasoner.types.Constant import Constant
from fuzzy_reasoner.types.Predicate import Predicate
from fuzzy_reasoner.types.Rule import Rule
from fuzzy_reasoner.types.Variable import Variable


class VariableBindingError(Exception):
    pass


def calc_similarity(
    item1: Constant | Predicate,
    item2: Constant | Predicate,
    similarity_func: Optional[Callable[[NDArray[Any], NDArray[Any]], float]],
) -> float:
    if similarity_func is None or item1.vector is None or item2.vector is None:
        return 1.0 if item1.symbol == item2.symbol else 0.0
    return similarity_func(item1.vector, item2.vector)


def resolve_term(
    term: Variable | Constant, scope: Rule, substitutions: SubstitutionsMap
) -> Variable | Constant:
    """
    if this term is a variable that's already been bound to a constant in the substitutions map, swap it for its bound value
    else, just return the term
    """
    if isinstance(term, Constant):
        return term
    var_binding = get_var_binding(term, scope, substitutions)
    return var_binding if var_binding else term


def is_var_bound(
    variable: Variable, scope: Rule, substitutions: SubstitutionsMap
) -> bool:
    return bool(get_var_binding(variable, scope, substitutions))


def get_var_binding(
    variable: Variable, scope: Rule, substitutions: SubstitutionsMap
) -> Constant | None:
    """Return the currently bound constant for this variable if already bound, or None if not bound yet"""
    scope_bindings = substitutions.get(scope)
    if not scope_bindings:
        return None
    var_binding = scope_bindings.get(variable)
    # if this is bound to another variable, recursively look up that variable
    if isinstance(var_binding, tuple):
        return get_var_binding(var_binding[1], var_binding[0], substitutions)
    return var_binding


def set_var_binding(
    variable: Variable,
    scope: Rule,
    # tuple[rule, var] represents the path to look up that variable recursively in the substitutions mapping
    value: Constant | tuple[Rule, Variable],
    substitutions: SubstitutionsMap,
) -> SubstitutionsMap:
    scope_bindings = substitutions.get(scope)
    if not scope_bindings:
        return substitutions.set(scope, Map({variable: value}))
    var_binding = scope_bindings.get(variable)
    # if this is bound to another variable, recursively set that var instead
    if isinstance(var_binding, tuple):
        return set_var_binding(var_binding[1], var_binding[0], value, substitutions)
    if var_binding is not None:
        raise VariableBindingError(
            f"Tried to bind an already-bound variable {variable} in scope {scope}"
        )
    return substitutions.set(scope, scope_bindings.set(variable, value))


def unify(
    rule: Rule,
    goal: Goal,
    proof_state: ProofState,
    similarity_func: Optional[SimilarityFunc] = None,
    min_similarity_threshold: float = 0.5,
) -> tuple[SubstitutionsMap, float] | None:
    """
    Fuzzy-optional implementation of prolog's unify
    If no similarity_func is provided, of if either atom lacks a vector,
    then it will do an exact match on the symbols themselves

    Based on unification module from "End-to-End Differentiable Proving" by Rocktäschel et al.
    https://arxiv.org/abs/1705.11040

    Returns a tuple with new substitutions and new similariy if successful or None if the unification fails
    """
    head = rule.head
    substitutions = proof_state.substitutions
    if len(head.terms) != len(goal.statement.terms):
        return None

    similarity = calc_similarity(
        head.predicate, goal.statement.predicate, similarity_func
    )

    # abort early if the predicate similarity is too low
    if similarity < min_similarity_threshold:
        return None

    for head_term, goal_term in zip(head.terms, goal.statement.terms):
        head_term_resolution = resolve_term(head_term, rule, substitutions)
        goal_term_resolution = resolve_term(goal_term, goal.scope, substitutions)
        if isinstance(head_term_resolution, Variable):
            # fail unification if it requires rebinding an already bound variable
            if is_var_bound(head_term_resolution, rule, substitutions):
                return None
            target_value = (
                goal_term_resolution
                if isinstance(goal_term_resolution, Constant)
                else (goal_term_resolution, goal.scope)
            )
            substitutions = set_var_binding(
                head_term_resolution, rule, target_value, substitutions
            )
        elif isinstance(goal_term_resolution, Variable):
            # fail unification if it requires rebinding an already bound variable
            if is_var_bound(goal_term_resolution, goal.scope, substitutions):
                return None
            substitutions = set_var_binding(
                goal_term_resolution, goal.scope, head_term_resolution, substitutions
            )
        else:
            similarity = min(
                similarity,
                calc_similarity(
                    head_term_resolution, goal_term_resolution, similarity_func
                ),
            )
            # abort early if the predicate similarity is too low
            if similarity < min_similarity_threshold:
                return None

    return (substitutions, similarity)

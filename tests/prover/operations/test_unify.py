from immutables import Map
import numpy as np
import pytest
from fuzzy_reasoner.prover.Goal import Goal
from fuzzy_reasoner.prover.ProofState import ProofState, SubstitutionsMap

from fuzzy_reasoner.prover.operations.unify import (
    VariableBindingError,
    calc_similarity,
    get_var_binding,
    set_var_binding,
    unify,
)
from fuzzy_reasoner.similarity import cosine_similarity
from fuzzy_reasoner.types.Constant import Constant
from fuzzy_reasoner.types.Predicate import Predicate
from fuzzy_reasoner.types.Rule import Rule
from fuzzy_reasoner.types.Variable import Variable


# -- calc_similarity helper --


def test_calc_similarity_uses_the_provided_similarity_metric() -> None:
    assert calc_similarity(
        Constant("a", np.array([1, 0, 1])),
        Constant("b", np.array([0, 1, 1])),
        cosine_similarity,
    ) == pytest.approx(0.5)


def test_calc_similarity_compares_symbols_if_no_metric_is_provided() -> None:
    assert calc_similarity(
        Constant("a", np.array([1, 0, 1])),
        Constant("b", np.array([0, 1, 1])),
        None,
    ) == pytest.approx(0.0)
    assert calc_similarity(
        Constant("same", np.array([1, 0, 1])),
        Constant("same", np.array([0, 1, 1])),
        None,
    ) == pytest.approx(1.0)


def test_calc_similarity_compares_symbols_if_either_const_is_missing_a_vector() -> None:
    assert calc_similarity(
        Constant("a", np.array([1, 0, 1])),
        Constant("b"),
        cosine_similarity,
    ) == pytest.approx(0.0)
    assert calc_similarity(
        Constant("same"),
        Constant("same"),
        cosine_similarity,
    ) == pytest.approx(1.0)


# -- get_var_binding helper --


def test_get_var_binding_recursively_resolves_dependencies() -> None:
    predicate = Predicate("is")
    const1 = Constant("jared")
    const2 = Constant("mark")
    var1 = Variable("X")
    var2 = Variable("Y")
    rule1 = Rule(predicate(const1))
    rule2 = Rule(predicate(const2))
    subs: SubstitutionsMap = Map(
        {
            rule1: Map({var1: const1, var2: (rule2, var1)}),
            rule2: Map({var2: (rule1, var1)}),
        }
    )
    assert get_var_binding(var1, rule1, subs) == const1
    assert get_var_binding(var2, rule1, subs) is None
    assert get_var_binding(var2, rule2, subs) == const1


# -- set_var_binding helper --


def test_set_var_binding_can_set_var_to_another_var() -> None:
    predicate = Predicate("is")
    const1 = Constant("jared")
    var1 = Variable("X")
    var2 = Variable("Y")
    rule1 = Rule(predicate(const1))
    subs: SubstitutionsMap = Map()

    new_subs = set_var_binding(var1, rule1, (rule1, var2), subs)

    # should recursively find the first referenced var and set its subtitution
    assert new_subs[rule1][var1] == (rule1, var2)


def test_set_var_binding_recursively_resolves_dependencies() -> None:
    predicate = Predicate("is")
    const1 = Constant("jared")
    const2 = Constant("mark")
    var1 = Variable("X")
    var2 = Variable("Y")
    rule1 = Rule(predicate(const1))
    rule2 = Rule(predicate(const2))
    subs: SubstitutionsMap = Map(
        {
            rule1: Map({var1: const1, var2: (rule2, var1)}),
            rule2: Map({var2: (rule1, var1)}),
        }
    )

    new_subs = set_var_binding(var1, rule2, const2, subs)

    # should recursively find the first referenced var and set its subtitution
    assert new_subs[rule2][var1] == const2
    assert get_var_binding(var1, rule2, new_subs) == const2


def test_set_var_binding_raises_exception_when_binding_already_bound_var() -> None:
    predicate = Predicate("is")
    const1 = Constant("jared")
    var1 = Variable("X")
    var2 = Variable("Y")
    rule1 = Rule(predicate(const1))
    subs: SubstitutionsMap = Map({rule1: Map({var1: const1})})

    with pytest.raises(VariableBindingError):
        set_var_binding(var1, rule1, (rule1, var2), subs)


# -- unify --


def test_unify_returns_new_substitution_map_and_similarity_on_success() -> None:
    is_dog = Predicate("is_dog")
    X = Variable("X")
    fluffy = Constant("fluffy")

    rule1 = Rule(is_dog(X))
    rule2 = Rule(is_dog(fluffy))

    goal = Goal(rule1.head, rule1)

    result = unify(
        rule2,
        goal,
        ProofState(similarity=0.9),
        similarity_func=cosine_similarity,
        min_similarity_threshold=0.5,
    )
    assert result is not None
    assert result[0] == Map({rule1: Map({X: fluffy})})
    assert result[1] == 0.9


def test_unify_fails_if_similarity_is_below_threshold() -> None:
    is_person = Predicate("is_person", np.array([1, 0, 1]))
    is_dog = Predicate("is_dog", np.array([0, 1, 1]))
    X = Variable("X")
    fluffy = Constant("fluffy")

    rule1 = Rule(is_person(X))
    rule2 = Rule(is_dog(fluffy))

    goal = Goal(rule1.head, rule1)

    assert (
        unify(
            rule2,
            goal,
            ProofState(similarity=1.0),
            similarity_func=cosine_similarity,
            min_similarity_threshold=0.9,
        )
        is None
    )


def test_unify_fails_if_the_terms_are_different_lengths() -> None:
    is_doggo = Predicate("is_doggo", np.array([1, 0, 1]))
    is_dog = Predicate("is_dog", np.array([0, 1, 1]))
    X = Variable("X")
    fluffy = Constant("fluffy")
    face = Constant("face")

    rule1 = Rule(is_doggo(X))
    rule2 = Rule(is_dog(fluffy, face))

    goal = Goal(rule1.head, rule1)

    assert (
        unify(
            rule2,
            goal,
            ProofState(similarity=1.0),
            similarity_func=cosine_similarity,
            min_similarity_threshold=0.1,
        )
        is None
    )


def test_unify_uses_the_min_similarity_of_all_unified_items() -> None:
    is_doggo = Predicate("is_doggo", np.array([1, 0, 1, 1]))
    is_dog = Predicate("is_dog", np.array([0, 1, 1, 1]))
    fluffy = Constant("fluffy", np.array([1, 0, 1]))
    furball = Constant("furball", np.array([0, 1, 1]))

    rule1 = Rule(is_doggo(furball))
    rule2 = Rule(is_dog(fluffy))

    goal = Goal(rule1.head, rule1)

    result = unify(
        rule2,
        goal,
        ProofState(similarity=0.9),
        similarity_func=cosine_similarity,
        min_similarity_threshold=0.1,
    )
    assert result is not None
    assert result[0] == Map()
    assert result[1] == pytest.approx(0.5)

# -- get_var_binding helper --


from immutables import Map
import pytest  # type: ignore
from fuzzy_reasoner.prover.operations.substitution import (
    SubstitutionsMap,
    VariableBindingError,
    get_var_binding,
    set_var_binding,
)
from fuzzy_reasoner.types.Constant import Constant
from fuzzy_reasoner.types.Predicate import Predicate
from fuzzy_reasoner.types.Rule import Rule
from fuzzy_reasoner.types.Variable import Variable


def test_get_var_binding_recursively_resolves_dependencies() -> None:
    predicate = Predicate("is")
    const1 = Constant("jared")
    const2 = Constant("mark")
    var1 = Variable("X")
    var2 = Variable("Y")
    rule1 = Rule(predicate(const1))
    rule2 = Rule(predicate(const2))
    subs: SubstitutionsMap = Map(
        {  # type: ignore
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
        {  # type: ignore
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

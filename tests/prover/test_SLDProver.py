from fuzzy_reasoner.prover.SLDProver import SLDProver
from fuzzy_reasoner.types.Constant import Constant
from fuzzy_reasoner.types.Rule import Rule
from fuzzy_reasoner.types.Variable import Variable
from fuzzy_reasoner.types.Predicate import Predicate


def test_basic_proof_without_fuzzy_unification() -> None:
    X = Variable("X")
    Y = Variable("Y")
    Z = Variable("Z")
    grandpa_of = Predicate("grandpa_of")
    grandma_of = Predicate("grandma_of")
    parent_of = Predicate("parent_of")
    father_of = Predicate("father_of")
    mother_of = Predicate("mother_of")
    bart = Constant("bart")
    homer = Constant("homer")
    marge = Constant("marge")
    mona = Constant("mona")
    abe = Constant("abe")

    grandpa_of_def = Rule(grandpa_of(X, Y), (father_of(X, Z), parent_of(Z, Y)))
    grandma_of_def = Rule(grandma_of(X, Y), (mother_of(X, Z), parent_of(Z, Y)))

    rules = [
        # base facts
        Rule(parent_of(homer, bart)),
        Rule(parent_of(marge, bart)),
        Rule(father_of(abe, homer)),
        Rule(mother_of(mona, homer)),
        # theorems
        grandpa_of_def,
        grandma_of_def,
    ]

    prover = SLDProver(rules=rules)
    goal = grandpa_of(abe, bart)

    result = prover.prove(goal)
    assert result is not None
    assert result.similarity_score == 1.0
    assert result.goal == goal

    # should first unify against grandpa_of(X,Y) :- father_of(X,Z), parent_of(Z,Y)
    assert result.head.rule == grandpa_of_def

    # should then join the 2 subgoals
    assert result.head.children is not None
    assert len(result.head.children) == 2

    assert grandpa_of_def.body is not None  # for mypy

    # should then unify father_of(X,Z) with father_of(abe, homer)
    assert result.head.children[0].goal == grandpa_of_def.body[0]
    assert result.head.children[0].children is None

    # should then unify parent_of(Z,Y) with parent_of(homer, bart)
    assert result.head.children[1].goal == grandpa_of_def.body[1]
    assert result.head.children[1].children is None

    # should not be able to prove things that are false
    assert prover.prove(grandpa_of(mona, bart)) is None
    assert prover.prove(grandpa_of(bart, abe)) is None


def test_can_solve_for_variable_values() -> None:
    X = Variable("X")
    Y = Variable("Y")
    Z = Variable("Z")
    grandpa_of = Predicate("grandpa_of")
    grandma_of = Predicate("grandma_of")
    parent_of = Predicate("parent_of")
    father_of = Predicate("father_of")
    mother_of = Predicate("mother_of")
    bart = Constant("bart")
    homer = Constant("homer")
    marge = Constant("marge")
    mona = Constant("mona")
    abe = Constant("abe")

    grandpa_of_def = Rule(grandpa_of(X, Y), (father_of(X, Z), parent_of(Z, Y)))
    grandma_of_def = Rule(grandma_of(X, Y), (mother_of(X, Z), parent_of(Z, Y)))

    rules = [
        # base facts
        Rule(parent_of(homer, bart)),
        Rule(parent_of(marge, bart)),
        Rule(father_of(abe, homer)),
        Rule(mother_of(mona, homer)),
        # theorems
        grandpa_of_def,
        grandma_of_def,
    ]

    prover = SLDProver(rules=rules)
    single_var_goal = grandpa_of(X, bart)

    result = prover.prove(single_var_goal)
    assert result is not None
    assert len(result.variable_bindings) == 1
    assert result.variable_bindings[X] == abe

    # should be able to solve for multiple variables together
    multi_var_goal = grandpa_of(X, Y)

    result = prover.prove(multi_var_goal)
    assert result is not None
    assert len(result.variable_bindings) == 2
    assert result.variable_bindings[X] == abe
    assert result.variable_bindings[Y] == bart

    # should not be able to find proofs of things that are false
    assert prover.prove(grandpa_of(X, homer)) is None
    assert prover.prove(grandpa_of(bart, X)) is None


def test_prove_all_can_find_multiple_solutions_with() -> None:
    X = Variable("X")
    Y = Variable("Y")
    Z = Variable("Z")
    grandpa_of = Predicate("grandpa_of")
    parent_of = Predicate("parent_of")
    father_of = Predicate("father_of")
    bart = Constant("bart")
    homer = Constant("homer")
    marge = Constant("marge")
    clancy = Constant("clancy")
    abe = Constant("abe")

    grandpa_of_def = Rule(grandpa_of(X, Y), (father_of(X, Z), parent_of(Z, Y)))

    rules = [
        # base facts
        Rule(parent_of(homer, bart)),
        Rule(parent_of(marge, bart)),
        Rule(father_of(abe, homer)),
        Rule(father_of(clancy, marge)),
        # theorems
        grandpa_of_def,
    ]

    prover = SLDProver(rules=rules)

    goal = grandpa_of(X, bart)

    results = prover.prove_all(goal)
    assert len(results) == 2
    var_bindings_for_x = {result.variable_bindings[X] for result in results}
    assert abe in var_bindings_for_x
    assert clancy in var_bindings_for_x

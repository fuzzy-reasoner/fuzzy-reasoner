from fuzzy_reasoner.prover.SLDProver import SLDProver
from fuzzy_reasoner.types.Atom import Atom
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
    is_male = Predicate("is_male")
    is_female = Predicate("is_female")
    bart = Constant("bart")
    homer = Constant("homer")
    marge = Constant("marge")
    mona = Constant("mona")
    abe = Constant("abe")

    rules = {
        # base facts
        Rule(parent_of([homer, bart])),
        Rule(parent_of([marge, bart])),
        Rule(parent_of([abe, homer])),
        Rule(parent_of([mona, homer])),
        Rule(is_male([homer])),
        Rule(is_male([abe])),
        Rule(is_male([bart])),
        Rule(is_female([marge])),
        Rule(is_female([mona])),
        # theorems
        Rule(father_of([X, Y]), [parent_of([X, Y]), is_male([X])]),
        Rule(mother_of([X, Y]), [parent_of([X, Y]), is_male([X])]),
        Rule(grandpa_of([X, Y]), [father_of([X, Z]), parent_of([Z, X])]),
        Rule(grandma_of([X, Y]), [mother_of([X, Z]), parent_of([Z, X])]),
    }

    prover = SLDProver(rules=rules)

    result = prover.prove(grandpa_of([abe, bart]))
    assert result is not None

    # should not be able to prove things that are false
    assert prover.prove(grandpa_of([mona, bart])) is None
    assert prover.prove(grandpa_of([bart, abe])) is None

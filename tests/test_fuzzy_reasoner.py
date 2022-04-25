from fuzzy_reasoner import (
    SLDProver,
    Atom,
    Constant,
    Predicate,
    Rule,
    Variable,
    cosine_similarity,
    symbol_compare,
)


def test_imports() -> None:
    assert SLDProver is not None
    assert Atom is not None
    assert Constant is not None
    assert Predicate is not None
    assert Rule is not None
    assert Variable is not None
    assert cosine_similarity is not None
    assert symbol_compare is not None

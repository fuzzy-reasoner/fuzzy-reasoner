from __future__ import annotations
from typing import Callable, Union
import numpy as np
from numpy.linalg import norm

from fuzzy_reasoner.types.Constant import Constant
from fuzzy_reasoner.types.Predicate import Predicate


SimilarityFunc = Callable[
    [Union[Constant, Predicate], Union[Constant, Predicate]], float
]


def symbol_compare(item1: Constant | Predicate, item2: Constant | Predicate) -> float:
    """
    directly compares the symbol strings of the two items, doesn't do any fuzzy matching
    """
    return 1.0 if item1.symbol == item2.symbol else 0.0


def cosine_similarity(
    item1: Constant | Predicate, item2: Constant | Predicate
) -> float:
    """
    use cosine similarity to calculate a similarity score between the items.
    falls back to symbol comparison if either item is missing a vector
    """
    if item1.vector is None or item2.vector is None:
        return symbol_compare(item1, item2)
    return np.dot(item1.vector, item2.vector) / (
        norm(item1.vector) * norm(item2.vector)
    )

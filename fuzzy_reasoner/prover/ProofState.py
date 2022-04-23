from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Union
from immutables import Map

from fuzzy_reasoner.types.Constant import Constant
from fuzzy_reasoner.types.Rule import Rule
from fuzzy_reasoner.types.Variable import Variable

# using from __future__ import annotations with | doesn't work here
# I think because this is declaring a type as a variable
SubstitutionsMap = Map[Rule, Map[Variable, Union[Constant, Tuple[Rule, Variable]]]]


@dataclass(frozen=True, eq=False)
class ProofState:
    similarity: float = 1.0
    substitutions: SubstitutionsMap = Map()

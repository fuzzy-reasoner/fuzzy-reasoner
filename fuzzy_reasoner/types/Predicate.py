from dataclasses import dataclass
from typing import List, Optional, Union
import numpy as np
from numpy.typing import NDArray

from .Atom import Atom
from .Constant import Constant
from .Variable import Variable


@dataclass
class Predicate:
    symbol: str
    vector: Optional[NDArray[np.float32]]

    # shorthand for creating an Atom out of this predicate and terms
    def __call__(self, terms: List[Union[Constant, Variable]]) -> Atom:
        return Atom(self, terms)

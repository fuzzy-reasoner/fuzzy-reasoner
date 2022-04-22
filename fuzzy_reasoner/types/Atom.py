from dataclasses import dataclass
from typing import List, Union

from .Variable import Variable
from .Constant import Constant
from .Predicate import Predicate


@dataclass
class Atom:
    predicate: Predicate
    terms: List[Union[Constant, Variable]]

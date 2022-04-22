from dataclasses import dataclass
from typing import List

from .Atom import Atom


@dataclass
class Rule:
    Head: Atom
    Body: List[Atom]

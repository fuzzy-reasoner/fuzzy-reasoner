__version__ = "0.1.1"

from .prover.SLDProver import SLDProver

from .types.Atom import Atom
from .types.Constant import Constant
from .types.Predicate import Predicate
from .types.Rule import Rule
from .types.Variable import Variable

from .similarity import cosine_similarity, symbol_compare

__all__ = (
    "SLDProver",
    "Atom",
    "Constant",
    "Predicate",
    "Rule",
    "Variable",
    "cosine_similarity",
    "symbol_compare",
)

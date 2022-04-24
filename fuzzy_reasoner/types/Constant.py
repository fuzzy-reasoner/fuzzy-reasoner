from dataclasses import dataclass
from typing import Optional, Any
from numpy.typing import NDArray


@dataclass(frozen=True, eq=False)
class Constant:
    symbol: str
    vector: Optional[NDArray[Any]] = None

    def __str__(self) -> str:
        return f"CONST:{self.symbol}"

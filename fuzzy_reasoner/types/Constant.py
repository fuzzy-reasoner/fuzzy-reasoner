from dataclasses import dataclass
from typing import Optional
import numpy as np
from numpy.typing import NDArray


@dataclass
class Constant:
    symbol: str
    vector: Optional[NDArray[np.float32]]

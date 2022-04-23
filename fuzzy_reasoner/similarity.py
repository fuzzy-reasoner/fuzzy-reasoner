from typing import Any
import numpy as np
from numpy.typing import NDArray
from numpy.linalg import norm


def cosine_similarity(vec1: NDArray[Any], vec2: NDArray[Any]) -> np.float32:
    return np.dot(vec1, vec2) / (norm(vec1) * norm(vec2))

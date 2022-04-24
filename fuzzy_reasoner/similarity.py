from typing import Any, Callable
import numpy as np
from numpy.typing import NDArray
from numpy.linalg import norm


SimilarityFunc = Callable[[NDArray[Any], NDArray[Any]], float]


def cosine_similarity(vec1: NDArray[Any], vec2: NDArray[Any]) -> float:
    return np.dot(vec1, vec2) / (norm(vec1) * norm(vec2))

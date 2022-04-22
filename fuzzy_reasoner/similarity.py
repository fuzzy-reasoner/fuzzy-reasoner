import numpy as np
from numpy.typing import NDArray
from numpy.linalg import norm


def cosine_similarity(
    vec1: NDArray[np.float32], vec2: NDArray[np.float32]
) -> np.float32:
    return np.dot(vec1, vec2) / (norm(vec1) * norm(vec2))

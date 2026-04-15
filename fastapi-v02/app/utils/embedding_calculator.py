import numpy as np


def calculate_retrained_embedding(
    u0: np.ndarray, posts: np.ndarray, alphas: np.ndarray
) -> np.ndarray:
    """Oblicz finalny embedding użytkownika z listy postów i wag alpha."""
    
    alphas = alphas.astype(np.float32)
    posts = posts.astype(np.float32)

    N = len(alphas)
    suffix = np.ones(N, dtype=np.float32)

    for i in range(N - 2, -1, -1):
        suffix[i] = suffix[i + 1] * (1.0 - alphas[i + 1])

    w_posts = alphas * suffix
    w0 = np.prod(1.0 - alphas)

    return w0 * u0 + (w_posts[:, None] * posts).sum(axis=0)

import numpy as np


def generate_random_basis(n_points: int = 1024,
                          n_dims: int = 3,
                          radius: float = 0.5,
                          seed: int = 0):
    rng = np.random.default_rng(seed)
    x = rng.normal(size=(n_points, n_dims))
    x_norms = np.sqrt(np.sum(np.square(x), axis=1)).reshape((-1, 1))
    x_unit = x / x_norms

    r = rng.uniform(size=(n_points, 1))
    u = np.power(r, 1.0 / n_dims)
    x = radius * x_unit * u

    return x

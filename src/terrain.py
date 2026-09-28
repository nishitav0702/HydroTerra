"""
terrain.py
HydroTerra - Terrain generation
Owner: Pranaya

Produces a procedural heightfield terrain as a 2D NumPy array.
Values are normalized to the range [0, 1] where:
    low number  -> low elevation
    high number -> high elevation (mountain)
"""

import numpy as np

try:
    from noise import pnoise2
    _HAS_NOISE = True
except ImportError:
    _HAS_NOISE = False


def generate_random_terrain(size=128, seed=None):
    """
    Quick-and-dirty terrain for Day 1 sanity checks.
    Not used in the final simulation, but useful to confirm
    the array shapes / plotting pipeline work before Perlin noise.
    """
    rng = np.random.default_rng(seed)
    terrain = rng.random((size, size))
    return terrain


def generate_terrain(size=128, scale=30.0, octaves=4, persistence=0.5, lacunarity=2.0, seed=0):
    """
    Procedural terrain using Perlin noise (Day 1 -> real deliverable).

    Falls back to smoothed random noise if the `noise` package
    isn't installed, so the rest of the pipeline never breaks.
    """
    terrain = np.zeros((size, size))

    if _HAS_NOISE:
        for y in range(size):
            for x in range(size):
                terrain[y, x] = pnoise2(
                    (x + seed * 1000) / scale,
                    (y + seed * 1000) / scale,
                    octaves=octaves,
                    persistence=persistence,
                    lacunarity=lacunarity,
                )
    else:
        # Fallback: random noise smoothed with a simple box blur,
        # so it still looks terrain-like without the `noise` package.
        rng = np.random.default_rng(seed)
        raw = rng.random((size, size))
        terrain = raw.copy()
        for _ in range(6):
            terrain = (
                terrain
                + np.roll(terrain, 1, axis=0)
                + np.roll(terrain, -1, axis=0)
                + np.roll(terrain, 1, axis=1)
                + np.roll(terrain, -1, axis=1)
            ) / 5.0

    # Normalize to [0, 1]
    terrain -= terrain.min()
    terrain /= (terrain.max() + 1e-8)

    return terrain


if __name__ == "__main__":
    t = generate_terrain()
    print("Terrain shape:", t.shape)
    print("Min:", t.min(), "Max:", t.max())

"""
============================================================
HydroTerra
Nishita's Terrain Generation Module
============================================================

Purpose:
    Generate procedural terrain represented as a 2D heightmap.

The heightmap is the foundation of the HydroTerra project.

Each cell:

    terrain[y, x]

stores the normalized elevation of that location.

The output of this module will later be used by:

    - hydraulic erosion
    - water simulation
    - flood vulnerability
    - 3D rendering

Author:
    Nishita

File:
    n_terrain.py
============================================================
"""

import numpy as np
from noise import pnoise2


# ------------------------------------------------------------
# DEFAULT SETTINGS
# ------------------------------------------------------------

DEFAULT_SIZE = 128
DEFAULT_SCALE = 50.0
DEFAULT_OCTAVES = 5


# ------------------------------------------------------------
# TERRAIN GENERATOR
# ------------------------------------------------------------

def generate_terrain(
    size=DEFAULT_SIZE,
    scale=DEFAULT_SCALE,
    octaves=DEFAULT_OCTAVES
):
    """
    Generate a procedural terrain using Perlin noise.

    Parameters
    ----------
    size : int
        Width and height of the terrain grid.

    scale : float
        Controls the size of terrain features.
        Larger values generally create broader terrain features.

    octaves : int
        Number of layers of noise used to create the terrain.
        More octaves create more detail.

    Returns
    -------
    numpy.ndarray
        A size x size floating-point heightmap.
        Values are normalized between 0 and 1.
    """

    # Create an empty terrain array.
    terrain = np.zeros(
        (size, size),
        dtype=np.float32
    )

    # Generate Perlin noise for every terrain cell.
    for y in range(size):
        for x in range(size):

            # Convert grid coordinates to noise coordinates.
            nx = x / scale
            ny = y / scale

            # Generate multi-octave Perlin noise.
            value = pnoise2(
                nx,
                ny,
                octaves=octaves,
                persistence=0.5,
                lacunarity=2.0,
                repeatx=size,
                repeaty=size,
                base=42
            )

            terrain[y, x] = value

    # --------------------------------------------------------
    # NORMALIZE TERRAIN
    # --------------------------------------------------------
    #
    # Convert the generated values into the range [0, 1].
    #
    # This gives us a convenient representation where:
    #
    # 0.0 = lowest terrain
    # 1.0 = highest terrain
    # --------------------------------------------------------

    minimum = terrain.min()
    maximum = terrain.max()

    if maximum != minimum:

        terrain = (
            terrain - minimum
        ) / (
            maximum - minimum
        )

    return terrain


# ------------------------------------------------------------
# TESTING
# ------------------------------------------------------------

if __name__ == "__main__":

    # Generate a test terrain when this file is executed
    # directly.

    terrain = generate_terrain()

    print("HydroTerra terrain generated.")
    print("Shape:", terrain.shape)
    print("Minimum:", terrain.min())
    print("Maximum:", terrain.max())
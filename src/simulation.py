"""
simulation.py
HydroTerra - Rain, water flow, erosion, sediment, evaporation
Owner: Pranaya

Maintains terrain height, water height, and sediment on a 2D grid.
Pipeline per step: rain -> flow -> erosion -> deposition -> evaporation
"""

import numpy as np
from google.colab import drive
drive.mount('/content/drive')

import os
import sys

PROJECT_PATH = "/content/drive/MyDrive/HydroTerra"
SRC_PATH = f"{PROJECT_PATH}/src"

# Check that the folder really exists
print("Project exists:", os.path.exists(PROJECT_PATH))
print("src exists:", os.path.exists(SRC_PATH))

# Show all files inside src
print("\nFiles inside src:")
print(os.listdir(SRC_PATH))

# Add src to Python's import path
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

print("\nsrc added to Python path:", SRC_PATH)

def add_rain(water, rainfall_intensity=0.001):
    """Rainfall adds water uniformly to every grid cell."""
    water = water + rainfall_intensity
    return water


def flow_water(terrain, water, flow_rate=0.25):
    """
    Simplified downhill water redistribution.

    For each cell, find its lowest neighbour (terrain + water height)
    and move a fraction of the water height-difference toward it.

    NOTE: this is a simplified discrete height-field approximation,
    not the full four-neighbour virtual-pipe model from the literature.
    That's a fair MVP simplification to state explicitly in the viva.
    """
    total = terrain + water
    new_water = water.copy()

    h, w = terrain.shape
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            neighbours = [(y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)]
            current_height = total[y, x]

            lowest = min(neighbours, key=lambda p: total[p[0], p[1]])
            ly, lx = lowest

            difference = current_height - total[ly, lx]
            if difference > 0:
                amount = min(water[y, x], difference * flow_rate)
                new_water[y, x] -= amount
                new_water[ly, lx] += amount

    return np.maximum(new_water, 0)


def erode_terrain(terrain, water, strength=0.0005):
    """
    Erosion proportional to local slope and water present.
    Steeper + wetter cells lose more terrain height, which becomes sediment.
    """
    gy, gx = np.gradient(terrain)
    slope = np.sqrt(gx ** 2 + gy ** 2)

    erosion = water * slope * strength
    erosion = np.minimum(erosion, terrain)  # can't erode below 0

    terrain = terrain - erosion
    sediment = erosion

    return terrain, sediment


def deposit_sediment(terrain, water, sediment, threshold=0.01):
    """
    Where water is slow/shallow, suspended sediment settles back
    onto the terrain.
    """
    slow_water = water < threshold
    deposition = sediment * slow_water * 0.3

    terrain = terrain + deposition
    sediment = sediment - deposition

    return terrain, sediment


def evaporate(water, rate=0.01):
    """Removes a fraction of water each step so it doesn't accumulate forever."""
    water = water * (1 - rate)
    return np.maximum(water, 0)


def simulation_step(
    terrain,
    water,
    sediment,
    rainfall=0.001,
    flow_rate=0.25,
    erosion_strength=0.0005,
    evaporation_rate=0.01,
):
    """
    One full iteration of the HydroTerra simulation:
    rain -> flow -> erosion -> deposition -> evaporation

    This is the function your teammate's Pygame main.py will call
    every frame.
    """
    water = add_rain(water, rainfall)
    water = flow_water(terrain, water, flow_rate)

    terrain, new_sediment = erode_terrain(terrain, water, erosion_strength)
    sediment = sediment + new_sediment

    terrain, sediment = deposit_sediment(terrain, water, sediment)
    water = evaporate(water, evaporation_rate)

    return terrain, water, sediment


if __name__ == "__main__":
    from terrain import generate_terrain

    terrain = generate_terrain()
    water = np.zeros_like(terrain)
    sediment = np.zeros_like(terrain)

    for i in range(50):
        terrain, water, sediment = simulation_step(terrain, water, sediment)

    print("After 50 steps:")
    print("Terrain range:", terrain.min(), terrain.max())
    print("Water range:", water.min(), water.max())
    print("Sediment range:", sediment.min(), sediment.max())

"""
HydroTerra - Nishita's Main Application

Loads:
    - terrain heightmap
    - water simulation output

Then sends both to TerrainRenderer.
"""

import sys
import pygame
import moderngl
import numpy as np

from src.n_renderer import TerrainRenderer
from src.n_camera import Camera


# ============================================================
# INITIALIZE PYGAME
# ============================================================

pygame.init()

# Window dimensions.
WIDTH = 1000
HEIGHT = 700

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT),
    pygame.OPENGL | pygame.DOUBLEBUF
)

pygame.display.set_caption(
    "HydroTerra"
)

print("Pygame window created successfully.")


# ============================================================
# CREATE MODERNGL CONTEXT
# ============================================================

context = moderngl.create_context()

print("ModernGL context created successfully.")

print(
    "OpenGL version:",
    context.info["GL_VERSION"]
)

print(
    "OpenGL renderer:",
    context.info["GL_RENDERER"]
)


# ============================================================
# ENABLE DEPTH TESTING
# ============================================================

# Depth testing makes closer terrain appear in front
# of terrain farther away.
context.enable(moderngl.DEPTH_TEST)


# ============================================================
# LOAD TERRAIN
# ============================================================

heightmap = np.load(
    "data/heightmap.npy"
)

print("Heightmap loaded.")

print(
    "Shape:",
    heightmap.shape
)


# ============================================================
# LOAD WATER SIMULATION OUTPUT
# ============================================================

watermap = np.load(
    "data/water.npy"
)

print("Water map loaded.")

print(
    "Water shape:",
    watermap.shape
)

print(
    "Water range:",
    float(watermap.min()),
    "to",
    float(watermap.max())
)


# ============================================================
# CREATE CAMERA
# ============================================================

camera = Camera()

print("Camera created.")


# ============================================================
# CREATE TERRAIN RENDERER
# ============================================================

renderer = TerrainRenderer(
    context,
    heightmap,
    watermap
)


# ============================================================
# MAIN LOOP
# ============================================================

clock = pygame.time.Clock()

running = True

while running:

    # --------------------------------------------------------
    # HANDLE EVENTS
    # --------------------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        # Mouse wheel controls zoom.
        elif event.type == pygame.MOUSEWHEEL:

            camera.zoom(
                event.y * 0.8
            )

    # --------------------------------------------------------
    # MOUSE CAMERA CONTROL
    # --------------------------------------------------------

    mouse_buttons = pygame.mouse.get_pressed()

    if mouse_buttons[0]:

        # Get mouse movement since the previous frame.
        dx, dy = pygame.mouse.get_rel()

        # Convert mouse movement into camera rotation.
        camera.orbit(
            dx * 0.5,
            -dy * 0.5
        )

    else:

        # Clear accumulated mouse movement so the camera
        # doesn't jump when you click again.
        pygame.mouse.get_rel()

    # --------------------------------------------------------
    # CLEAR SCREEN
    # --------------------------------------------------------

    context.clear(
        0.05,
        0.05,
        0.08,
        1.0
    )

    # --------------------------------------------------------
    # RENDER TERRAIN + WATER
    # --------------------------------------------------------

    renderer.render(
        camera,
        WIDTH / HEIGHT
    )

    # --------------------------------------------------------
    # DISPLAY FRAME
    # --------------------------------------------------------

    pygame.display.flip()

    # Limit rendering to 60 FPS.
    clock.tick(60)


# ============================================================
# CLEANUP
# ============================================================

pygame.quit()

print(
    "HydroTerra application closed."
)

sys.exit()
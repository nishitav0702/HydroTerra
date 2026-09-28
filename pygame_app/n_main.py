"""
HydroTerra - Nishita's Main Application

STEP 2
Interactive visualization interface.

Controls:

    W = Water ON/OFF
    R = Risk ON/OFF
    S = Settlements ON/OFF
    T = Terrain ON/OFF
    H = Hide/Show interface
    ESC = Quit

Mouse:

    Mouse wheel = Zoom
    Left mouse drag = Orbit
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

WIDTH = 1000
HEIGHT = 700

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT),
    pygame.OPENGL | pygame.DOUBLEBUF
)

pygame.display.set_caption(
    "HydroTerra - Terrain Erosion & Flood Vulnerability"
)

print(
    "Pygame window created successfully."
)


# ============================================================
# MODERNGL
# ============================================================

context = moderngl.create_context()

print(
    "ModernGL context created successfully."
)

print(
    "OpenGL version:",
    context.info["GL_VERSION"]
)

print(
    "OpenGL renderer:",
    context.info["GL_RENDERER"]
)


# ============================================================
# DEPTH TESTING
# ============================================================

context.enable(
    moderngl.DEPTH_TEST
)


# ============================================================
# LOAD TERRAIN
# ============================================================

heightmap = np.load(
    "data/heightmap.npy"
)

print(
    "Heightmap loaded."
)

print(
    "Shape:",
    heightmap.shape
)


# ============================================================
# LOAD WATER
# ============================================================

watermap = np.load(
    "data/water.npy"
)

print(
    "Water map loaded."
)

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
# LOAD RISK
# ============================================================

riskmap = np.load(
    "data/risk.npy"
)

print(
    "Risk map loaded."
)

print(
    "Risk shape:",
    riskmap.shape
)

print(
    "Risk range:",
    float(riskmap.min()),
    "to",
    float(riskmap.max())
)


# ============================================================
# LOAD SETTLEMENT
# ============================================================

settlementmap = np.load(
    "data/settlement.npy"
)

print(
    "Settlement map loaded."
)

print(
    "Settlement shape:",
    settlementmap.shape
)

settlement_count = int(
    np.sum(settlementmap)
)

print(
    "Settlement cells:",
    settlement_count
)


# ============================================================
# STATISTICS
# ============================================================

max_water = float(
    watermap.max()
)

mean_risk = float(
    riskmap.mean()
)

max_risk = float(
    riskmap.max()
)


# ============================================================
# CAMERA
# ============================================================

camera = Camera()

print(
    "Camera created."
)


# ============================================================
# RENDERER
# ============================================================

renderer = TerrainRenderer(
    context,
    heightmap,
    watermap,
    riskmap,
    settlementmap
)


# ============================================================
# UI SETUP
# ============================================================

font = pygame.font.SysFont(
    "Arial",
    20
)

small_font = pygame.font.SysFont(
    "Arial",
    16
)

title_font = pygame.font.SysFont(
    "Arial",
    28,
    bold=True
)

show_ui = True


# ============================================================
# UI DRAWING
# ============================================================

def draw_text(
    text,
    x,
    y,
    font_object,
    surface
):

    text_surface = font_object.render(
        text,
        True,
        (255, 255, 255)
    )

    surface.blit(
        text_surface,
        (x, y)
    )


def draw_ui():

    # --------------------------------------------------------
    # UI PANEL
    # --------------------------------------------------------

    panel = pygame.Surface(
        (290, 440),
        pygame.SRCALPHA
    )

    panel.fill(
        (10, 15, 25, 220)
    )

    screen.blit(
        panel,
        (20, 20)
    )

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    draw_text(
        "HYDROTERRA",
        40,
        40,
        title_font,
        screen
    )

    draw_text(
        "Terrain & Flood Simulator",
        40,
        76,
        small_font,
        screen
    )

    # --------------------------------------------------------
    # SIMULATION DATA
    # --------------------------------------------------------

    draw_text(
        "SIMULATION",
        40,
        115,
        font,
        screen
    )

    draw_text(
        f"Terrain: {heightmap.shape[0]} x {heightmap.shape[1]}",
        40,
        145,
        small_font,
        screen
    )

    draw_text(
        f"Max water: {max_water:.3f}",
        40,
        170,
        small_font,
        screen
    )

    draw_text(
        f"Mean risk: {mean_risk:.3f}",
        40,
        195,
        small_font,
        screen
    )

    draw_text(
        f"Max risk: {max_risk:.3f}",
        40,
        220,
        small_font,
        screen
    )

    draw_text(
        f"Settlement cells: {settlement_count}",
        40,
        245,
        small_font,
        screen
    )

    # --------------------------------------------------------
    # LAYER STATUS
    # --------------------------------------------------------

    draw_text(
        "LAYERS",
        40,
        285,
        font,
        screen
    )

    terrain_status = (
        "ON" if renderer.show_terrain else "OFF"
    )

    water_status = (
        "ON" if renderer.show_water else "OFF"
    )

    risk_status = (
        "ON" if renderer.show_risk else "OFF"
    )

    settlement_status = (
        "ON" if renderer.show_settlements else "OFF"
    )

    draw_text(
        f"[T] Terrain       {terrain_status}",
        40,
        315,
        small_font,
        screen
    )

    draw_text(
        f"[W] Water         {water_status}",
        40,
        340,
        small_font,
        screen
    )

    draw_text(
        f"[R] Risk          {risk_status}",
        40,
        365,
        small_font,
        screen
    )

    draw_text(
        f"[S] Settlements   {settlement_status}",
        40,
        390,
        small_font,
        screen
    )

    # --------------------------------------------------------
    # CONTROLS
    # --------------------------------------------------------

    draw_text(
        "[H] Hide interface",
        40,
        425,
        small_font,
        screen
    )


# ============================================================
# MAIN LOOP
# ============================================================

clock = pygame.time.Clock()

running = True

while running:

    # --------------------------------------------------------
    # EVENTS
    # --------------------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        # ----------------------------------------------------
        # KEYBOARD
        # ----------------------------------------------------

        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:

                running = False

            elif event.key == pygame.K_w:

                renderer.show_water = (
                    not renderer.show_water
                )

            elif event.key == pygame.K_r:

                renderer.show_risk = (
                    not renderer.show_risk
                )

            elif event.key == pygame.K_s:

                renderer.show_settlements = (
                    not renderer.show_settlements
                )

            elif event.key == pygame.K_t:

                renderer.show_terrain = (
                    not renderer.show_terrain
                )

            elif event.key == pygame.K_h:

                show_ui = not show_ui

        # ----------------------------------------------------
        # ZOOM
        # ----------------------------------------------------

        elif event.type == pygame.MOUSEWHEEL:

            camera.zoom(
                event.y * 0.8
            )

    # --------------------------------------------------------
    # MOUSE ORBIT
    # --------------------------------------------------------

    mouse_buttons = pygame.mouse.get_pressed()

    if mouse_buttons[0]:

        dx, dy = pygame.mouse.get_rel()

        camera.orbit(
            dx * 0.5,
            -dy * 0.5
        )

    else:

        pygame.mouse.get_rel()

    # --------------------------------------------------------
    # CLEAR
    # --------------------------------------------------------

    context.clear(
        0.05,
        0.05,
        0.08,
        1.0
    )

    # --------------------------------------------------------
    # RENDER
    # --------------------------------------------------------

    renderer.render(
        camera,
        WIDTH / HEIGHT
    )

    # --------------------------------------------------------
    # UI
    # --------------------------------------------------------

    if show_ui:

        draw_ui()

    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------

    pygame.display.flip()

    clock.tick(60)


# ============================================================
# CLEANUP
# ============================================================

pygame.quit()

print(
    "HydroTerra application closed."
)

sys.exit()
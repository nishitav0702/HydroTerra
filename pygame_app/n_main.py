"""
HydroTerra - Nishita's Main Application

FINAL INTEGRATION

HydroTerra visualizes:
    - Terrain elevation
    - Water accumulation
    - Flood vulnerability
    - Settlement locations

Controls:

    T = Terrain ON/OFF
    W = Water ON/OFF
    R = Risk ON/OFF
    S = Settlements ON/OFF
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
    "HydroTerra | Terrain Erosion & Flood Vulnerability"
)


# ============================================================
# MODERNGL
# ============================================================

context = moderngl.create_context()

context.enable(
    moderngl.DEPTH_TEST
)


# ============================================================
# LOAD SIMULATION DATA
# ============================================================

try:

    heightmap = np.load(
        "data/heightmap.npy"
    )

    watermap = np.load(
        "data/water.npy"
    )

    riskmap = np.load(
        "data/risk.npy"
    )

    settlementmap = np.load(
        "data/settlement.npy"
    )

except FileNotFoundError as error:

    print()
    print("=" * 60)
    print("HYDROTERRA DATA ERROR")
    print("=" * 60)
    print("A required simulation output is missing.")
    print("Make sure the data folder contains:")
    print("  heightmap.npy")
    print("  water.npy")
    print("  risk.npy")
    print("  settlement.npy")
    print()
    print("Missing file:")
    print(error)
    print("=" * 60)

    pygame.quit()
    sys.exit()


# ============================================================
# DATA VALIDATION
# ============================================================

expected_shape = heightmap.shape

if watermap.shape != expected_shape:
    raise ValueError(
        "water.npy does not match heightmap.npy."
    )

if riskmap.shape != expected_shape:
    raise ValueError(
        "risk.npy does not match heightmap.npy."
    )

if settlementmap.shape != expected_shape:
    raise ValueError(
        "settlement.npy does not match heightmap.npy."
    )


# ============================================================
# SIMULATION STATISTICS
# ============================================================

max_water = float(
    watermap.max()
)

mean_water = float(
    watermap.mean()
)

max_risk = float(
    riskmap.max()
)

mean_risk = float(
    riskmap.mean()
)

settlement_count = int(
    np.sum(settlementmap >= 0.5)
)

visible_water_cells = int(
    np.sum(watermap >= 0.03)
)

visible_risk_cells = int(
    np.sum(riskmap >= 0.08)
)


# ============================================================
# CAMERA
# ============================================================

camera = Camera()


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
# FONTS
# ============================================================

title_font = pygame.font.SysFont(
    "Arial",
    28,
    bold=True
)

section_font = pygame.font.SysFont(
    "Arial",
    19,
    bold=True
)

body_font = pygame.font.SysFont(
    "Arial",
    16
)

small_font = pygame.font.SysFont(
    "Arial",
    14
)


# ============================================================
# UI STATE
# ============================================================

show_ui = True


# ============================================================
# TEXT HELPER
# ============================================================

def draw_text(
    text,
    x,
    y,
    font_object,
    surface,
    alpha=255
):

    text_surface = font_object.render(
        text,
        True,
        (255, 255, 255)
    )

    if alpha != 255:
        text_surface.set_alpha(alpha)

    surface.blit(
        text_surface,
        (x, y)
    )


# ============================================================
# STATUS INDICATOR
# ============================================================

def draw_status(
    label,
    enabled,
    x,
    y
):

    status_colour = (
        (80, 220, 120)
        if enabled
        else
        (150, 150, 150)
    )

    status_text = (
        "ON"
        if enabled
        else
        "OFF"
    )

    label_surface = body_font.render(
        label,
        True,
        (235, 235, 235)
    )

    screen.blit(
        label_surface,
        (x, y)
    )

    pygame.draw.rect(
        screen,
        status_colour,
        (x + 145, y + 4, 9, 9)
    )

    status_surface = small_font.render(
        status_text,
        True,
        status_colour
    )

    screen.blit(
        status_surface,
        (x + 164, y - 1)
    )


# ============================================================
# RISK LEGEND
# ============================================================

def draw_risk_legend(
    x,
    y
):

    draw_text(
        "RISK SCALE",
        x,
        y,
        section_font,
        screen
    )

    legend_width = 210
    legend_height = 12

    segments = 30

    for i in range(segments):

        t = i / (segments - 1)

        if t < 0.5:

            local_t = t / 0.5

            r = 255
            g = int(
                215 - 135 * local_t
            )
            b = int(
                5 - 3 * local_t
            )

        else:

            local_t = (
                t - 0.5
            ) / 0.5

            r = int(
                255 - 25 * local_t
            )
            g = int(
                80 - 70 * local_t
            )
            b = int(
                2 + 20 * local_t
            )

        segment_width = (
            legend_width / segments
        )

        pygame.draw.rect(
            screen,
            (r, g, b),
            (
                int(
                    x + i * segment_width
                ),
                y + 30,
                int(segment_width + 1),
                legend_height
            )
        )

    draw_text(
        "Low",
        x,
        y + 48,
        small_font,
        screen
    )

    draw_text(
        "Medium",
        x + 88,
        y + 48,
        small_font,
        screen
    )

    draw_text(
        "High",
        x + 185,
        y + 48,
        small_font,
        screen
    )


# ============================================================
# MAIN UI
# ============================================================

def draw_ui():

    # --------------------------------------------------------
    # LEFT PANEL
    # --------------------------------------------------------

    panel = pygame.Surface(
        (330, 575),
        pygame.SRCALPHA
    )

    panel.fill(
        (8, 12, 22, 225)
    )

    screen.blit(
        panel,
        (18, 18)
    )

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    draw_text(
        "HYDROTERRA",
        38,
        36,
        title_font,
        screen
    )

    draw_text(
        "Terrain Erosion & Flood Vulnerability",
        40,
        72,
        small_font,
        screen
    )

    # --------------------------------------------------------
    # DIVIDER
    # --------------------------------------------------------

    pygame.draw.line(
        screen,
        (100, 110, 125),
        (38, 101),
        (320, 101),
        1
    )

    # --------------------------------------------------------
    # SIMULATION SECTION
    # --------------------------------------------------------

    draw_text(
        "SIMULATION OUTPUT",
        38,
        118,
        section_font,
        screen
    )

    draw_text(
        f"Terrain grid      {heightmap.shape[0]} x "
        f"{heightmap.shape[1]}",
        40,
        150,
        body_font,
        screen
    )

    draw_text(
        f"Maximum water    {max_water:.3f}",
        40,
        176,
        body_font,
        screen
    )

    draw_text(
        f"Mean water       {mean_water:.3f}",
        40,
        201,
        body_font,
        screen
    )

    draw_text(
        f"Maximum risk     {max_risk:.3f}",
        40,
        226,
        body_font,
        screen
    )

    draw_text(
        f"Mean risk        {mean_risk:.3f}",
        40,
        251,
        body_font,
        screen
    )

    draw_text(
        f"Settlements      {settlement_count}",
        40,
        276,
        body_font,
        screen
    )

    # --------------------------------------------------------
    # LAYER SECTION
    # --------------------------------------------------------

    draw_text(
        "VISUALIZATION LAYERS",
        38,
        315,
        section_font,
        screen
    )

    draw_status(
        "[T] Terrain",
        renderer.show_terrain,
        40,
        348
    )

    draw_status(
        "[W] Water",
        renderer.show_water,
        40,
        374
    )

    draw_status(
        "[R] Flood risk",
        renderer.show_risk,
        40,
        400
    )

    draw_status(
        "[S] Settlements",
        renderer.show_settlements,
        40,
        426
    )

    # --------------------------------------------------------
    # RISK LEGEND
    # --------------------------------------------------------

    draw_risk_legend(
        40,
        462
    )

    # --------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------

    footer = pygame.Surface(
        (330, 55),
        pygame.SRCALPHA
    )

    footer.fill(
        (20, 25, 38, 220)
    )

    screen.blit(
        footer,
        (18, 638)
    )

    draw_text(
        "Drag = Orbit     Wheel = Zoom     H = Hide UI",
        32,
        656,
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

        elif event.type == pygame.KEYDOWN:

            # ------------------------------------------------
            # EXIT
            # ------------------------------------------------

            if event.key == pygame.K_ESCAPE:

                running = False

            # ------------------------------------------------
            # LAYER CONTROLS
            # ------------------------------------------------

            elif event.key == pygame.K_t:

                renderer.show_terrain = (
                    not renderer.show_terrain
                )

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

            # ------------------------------------------------
            # UI
            # ------------------------------------------------

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
    # ORBIT
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
        0.035,
        0.045,
        0.065,
        1.0
    )

    # --------------------------------------------------------
    # 3D RENDER
    # --------------------------------------------------------

    renderer.render(
        camera,
        WIDTH / HEIGHT
    )

    # --------------------------------------------------------
    # 2D UI
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

sys.exit()
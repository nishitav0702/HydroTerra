"""
HydroTerra - Nishita's Terrain Renderer

FINAL INTEGRATION
Interactive 3D visualization:
    - Procedural terrain
    - Water accumulation
    - Flood-risk heatmap
    - Settlement locations
"""

import ctypes

import numpy as np
import moderngl
import glm


# ============================================================
# MATRIX HELPER
# ============================================================

def mat4_bytes(matrix):
    return ctypes.string_at(
        glm.value_ptr(matrix),
        64
    )


# ============================================================
# TERRAIN SHADERS
# ============================================================

TERRAIN_VERTEX_SHADER = """
#version 330

in vec3 in_position;
in vec3 in_normal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out float terrain_height;
out vec3 surface_normal;

void main()
{
    terrain_height = in_position.y / 2.0;
    surface_normal = in_normal;

    gl_Position =
        projection *
        view *
        model *
        vec4(in_position, 1.0);
}
"""


TERRAIN_FRAGMENT_SHADER = """
#version 330

in float terrain_height;
in vec3 surface_normal;

out vec4 fragColor;

void main()
{
    float h = clamp(terrain_height, 0.0, 1.0);

    vec3 low_colour =
        vec3(0.08, 0.30, 0.10);

    vec3 middle_colour =
        vec3(0.25, 0.60, 0.18);

    vec3 high_colour =
        vec3(0.55, 0.38, 0.15);

    vec3 peak_colour =
        vec3(0.85, 0.85, 0.75);

    vec3 terrain_colour;

    if (h < 0.35)
    {
        terrain_colour = mix(
            low_colour,
            middle_colour,
            h / 0.35
        );
    }
    else if (h < 0.70)
    {
        terrain_colour = mix(
            middle_colour,
            high_colour,
            (h - 0.35) / 0.35
        );
    }
    else
    {
        terrain_colour = mix(
            high_colour,
            peak_colour,
            (h - 0.70) / 0.30
        );
    }

    vec3 light_direction =
        normalize(vec3(-0.5, 1.0, 0.4));

    float light_amount =
        dot(
            normalize(surface_normal),
            light_direction
        );

    light_amount = max(light_amount, 0.25);

    terrain_colour *= light_amount;

    fragColor =
        vec4(terrain_colour, 1.0);
}
"""


# ============================================================
# WATER SHADERS
# ============================================================

WATER_VERTEX_SHADER = """
#version 330

in vec3 in_position;
in float in_water;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out float water_amount;

void main()
{
    water_amount = in_water;

    vec3 water_position = in_position;

    water_position.y += 0.025;

    gl_Position =
        projection *
        view *
        model *
        vec4(water_position, 1.0);
}
"""


WATER_FRAGMENT_SHADER = """
#version 330

in float water_amount;

out vec4 fragColor;

void main()
{
    float intensity = clamp(
        water_amount / 0.314632157,
        0.0,
        1.0
    );

    if (intensity < 0.03)
    {
        discard;
    }

    vec3 shallow_water =
        vec3(0.10, 0.55, 0.85);

    vec3 deep_water =
        vec3(0.02, 0.15, 0.65);

    vec3 water_colour =
        mix(
            shallow_water,
            deep_water,
            intensity
        );

    float alpha =
        0.35 + intensity * 0.45;

    fragColor =
        vec4(water_colour, alpha);
}
"""


# ============================================================
# RISK SHADERS
# ============================================================

RISK_VERTEX_SHADER = """
#version 330

in vec3 in_position;
in float in_risk;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out float risk_value;

void main()
{
    risk_value = in_risk;

    vec3 risk_position = in_position;

    risk_position.y += 0.045;

    gl_Position =
        projection *
        view *
        model *
        vec4(risk_position, 1.0);
}
"""


RISK_FRAGMENT_SHADER = """
#version 330

in float risk_value;

out vec4 fragColor;

void main()
{
    if (risk_value < 0.08)
    {
        discard;
    }

    float r = clamp(
        risk_value / 0.839,
        0.0,
        1.0
    );

    vec3 low_risk =
        vec3(1.0, 0.85, 0.05);

    vec3 medium_risk =
        vec3(1.0, 0.40, 0.02);

    vec3 high_risk =
        vec3(0.90, 0.03, 0.02);

    vec3 risk_colour;

    if (r < 0.5)
    {
        risk_colour = mix(
            low_risk,
            medium_risk,
            r / 0.5
        );
    }
    else
    {
        risk_colour = mix(
            medium_risk,
            high_risk,
            (r - 0.5) / 0.5
        );
    }

    float alpha =
        0.20 + r * 0.35;

    fragColor =
        vec4(risk_colour, alpha);
}
"""


# ============================================================
# SETTLEMENT SHADERS
# ============================================================

SETTLEMENT_VERTEX_SHADER = """
#version 330

in vec3 in_position;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    vec3 settlement_position =
        in_position;

    settlement_position.y += 0.075;

    gl_Position =
        projection *
        view *
        model *
        vec4(
            settlement_position,
            1.0
        );
}
"""


SETTLEMENT_FRAGMENT_SHADER = """
#version 330

out vec4 fragColor;

void main()
{
    fragColor =
        vec4(
            1.0,
            1.0,
            1.0,
            0.90
        );
}
"""


# ============================================================
# TERRAIN RENDERER
# ============================================================

class TerrainRenderer:

    def __init__(
        self,
        context,
        heightmap,
        watermap,
        riskmap,
        settlementmap
    ):

        self.context = context

        self.heightmap = np.asarray(
            heightmap,
            dtype=np.float32
        )

        self.watermap = np.asarray(
            watermap,
            dtype=np.float32
        )

        self.riskmap = np.asarray(
            riskmap,
            dtype=np.float32
        )

        self.settlementmap = np.asarray(
            settlementmap,
            dtype=np.float32
        )

        # ----------------------------------------------------
        # LAYER VISIBILITY
        # ----------------------------------------------------

        self.show_terrain = True
        self.show_water = True
        self.show_risk = True
        self.show_settlements = True

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if self.heightmap.ndim != 2:
            raise ValueError(
                "Heightmap must be 2D."
            )

        if self.watermap.shape != self.heightmap.shape:
            raise ValueError(
                "Water map must match heightmap shape."
            )

        if self.riskmap.shape != self.heightmap.shape:
            raise ValueError(
                "Risk map must match heightmap shape."
            )

        if self.settlementmap.shape != self.heightmap.shape:
            raise ValueError(
                "Settlement map must match heightmap shape."
            )

        # ----------------------------------------------------
        # TERRAIN NORMALIZATION
        # ----------------------------------------------------

        minimum = float(
            np.min(self.heightmap)
        )

        maximum = float(
            np.max(self.heightmap)
        )

        height_range = maximum - minimum

        if height_range == 0:
            height_range = 1.0

        self.normalized_heightmap = (
            self.heightmap - minimum
        ) / height_range

        # ----------------------------------------------------
        # SHADERS
        # ----------------------------------------------------

        self.terrain_program = self.context.program(
            vertex_shader=TERRAIN_VERTEX_SHADER,
            fragment_shader=TERRAIN_FRAGMENT_SHADER
        )

        self.water_program = self.context.program(
            vertex_shader=WATER_VERTEX_SHADER,
            fragment_shader=WATER_FRAGMENT_SHADER
        )

        self.risk_program = self.context.program(
            vertex_shader=RISK_VERTEX_SHADER,
            fragment_shader=RISK_FRAGMENT_SHADER
        )

        self.settlement_program = self.context.program(
            vertex_shader=SETTLEMENT_VERTEX_SHADER,
            fragment_shader=SETTLEMENT_FRAGMENT_SHADER
        )

        # ----------------------------------------------------
        # CREATE MESHES
        # ----------------------------------------------------

        terrain_vertices, indices = (
            self.create_terrain_mesh()
        )

        water_vertices = (
            self.create_water_mesh()
        )

        risk_vertices = (
            self.create_risk_mesh()
        )

        settlement_vertices = (
            self.create_settlement_mesh()
        )

        # ----------------------------------------------------
        # TERRAIN BUFFERS
        # ----------------------------------------------------

        self.terrain_vertex_buffer = (
            self.context.buffer(
                terrain_vertices.tobytes()
            )
        )

        self.index_buffer = (
            self.context.buffer(
                indices.tobytes()
            )
        )

        self.terrain_vertex_array = (
            self.context.vertex_array(
                self.terrain_program,
                [
                    (
                        self.terrain_vertex_buffer,
                        "3f 3f",
                        "in_position",
                        "in_normal"
                    )
                ],
                self.index_buffer
            )
        )

        # ----------------------------------------------------
        # WATER BUFFERS
        # ----------------------------------------------------

        self.water_vertex_buffer = (
            self.context.buffer(
                water_vertices.tobytes()
            )
        )

        self.water_vertex_array = (
            self.context.vertex_array(
                self.water_program,
                [
                    (
                        self.water_vertex_buffer,
                        "3f 1f",
                        "in_position",
                        "in_water"
                    )
                ],
                self.index_buffer
            )
        )

        # ----------------------------------------------------
        # RISK BUFFERS
        # ----------------------------------------------------

        self.risk_vertex_buffer = (
            self.context.buffer(
                risk_vertices.tobytes()
            )
        )

        self.risk_vertex_array = (
            self.context.vertex_array(
                self.risk_program,
                [
                    (
                        self.risk_vertex_buffer,
                        "3f 1f",
                        "in_position",
                        "in_risk"
                    )
                ],
                self.index_buffer
            )
        )

        # ----------------------------------------------------
        # SETTLEMENT BUFFERS
        # ----------------------------------------------------

        self.settlement_vertex_buffer = (
            self.context.buffer(
                settlement_vertices.tobytes()
            )
        )

        self.settlement_vertex_array = (
            self.context.vertex_array(
                self.settlement_program,
                [
                    (
                        self.settlement_vertex_buffer,
                        "3f",
                        "in_position"
                    )
                ]
            )
        )

    # ========================================================
    # TERRAIN MESH
    # ========================================================

    def create_terrain_mesh(self):

        height, width = (
            self.normalized_heightmap.shape
        )

        terrain_size = 8.0
        vertical_scale = 2.0

        x_step = terrain_size / (width - 1)
        z_step = terrain_size / (height - 1)

        vertices = []

        for z in range(height):

            for x in range(width):

                world_x = (
                    x * x_step
                    - terrain_size / 2.0
                )

                world_z = (
                    z * z_step
                    - terrain_size / 2.0
                )

                elevation = float(
                    self.normalized_heightmap[z, x]
                )

                world_y = (
                    elevation * vertical_scale
                )

                left_x = max(x - 1, 0)
                right_x = min(x + 1, width - 1)

                up_z = max(z - 1, 0)
                down_z = min(z + 1, height - 1)

                left_height = (
                    self.normalized_heightmap[z, left_x]
                )

                right_height = (
                    self.normalized_heightmap[z, right_x]
                )

                up_height = (
                    self.normalized_heightmap[up_z, x]
                )

                down_height = (
                    self.normalized_heightmap[down_z, x]
                )

                slope_x = right_height - left_height
                slope_z = down_height - up_height

                normal = np.array(
                    [
                        -slope_x,
                        1.0,
                        -slope_z
                    ],
                    dtype=np.float32
                )

                normal /= (
                    np.linalg.norm(normal) + 1e-8
                )

                vertices.extend([
                    world_x,
                    world_y,
                    world_z,
                    normal[0],
                    normal[1],
                    normal[2]
                ])

        return (
            np.asarray(vertices, dtype=np.float32),
            self.create_indices(width, height)
        )

    # ========================================================
    # WATER MESH
    # ========================================================

    def create_water_mesh(self):

        height, width = (
            self.normalized_heightmap.shape
        )

        terrain_size = 8.0
        vertical_scale = 2.0

        x_step = terrain_size / (width - 1)
        z_step = terrain_size / (height - 1)

        vertices = []

        for z in range(height):

            for x in range(width):

                world_x = (
                    x * x_step
                    - terrain_size / 2.0
                )

                world_z = (
                    z * z_step
                    - terrain_size / 2.0
                )

                elevation = float(
                    self.normalized_heightmap[z, x]
                )

                world_y = (
                    elevation * vertical_scale
                )

                water_amount = float(
                    self.watermap[z, x]
                )

                vertices.extend([
                    world_x,
                    world_y,
                    world_z,
                    water_amount
                ])

        return np.asarray(
            vertices,
            dtype=np.float32
        )

    # ========================================================
    # RISK MESH
    # ========================================================

    def create_risk_mesh(self):

        height, width = (
            self.normalized_heightmap.shape
        )

        terrain_size = 8.0
        vertical_scale = 2.0

        x_step = terrain_size / (width - 1)
        z_step = terrain_size / (height - 1)

        vertices = []

        for z in range(height):

            for x in range(width):

                world_x = (
                    x * x_step
                    - terrain_size / 2.0
                )

                world_z = (
                    z * z_step
                    - terrain_size / 2.0
                )

                elevation = float(
                    self.normalized_heightmap[z, x]
                )

                world_y = (
                    elevation * vertical_scale
                )

                risk_value = float(
                    self.riskmap[z, x]
                )

                vertices.extend([
                    world_x,
                    world_y,
                    world_z,
                    risk_value
                ])

        return np.asarray(
            vertices,
            dtype=np.float32
        )

    # ========================================================
    # SETTLEMENT MESH
    # ========================================================

    def create_settlement_mesh(self):

        height, width = (
            self.normalized_heightmap.shape
        )

        terrain_size = 8.0
        vertical_scale = 2.0

        x_step = terrain_size / (width - 1)
        z_step = terrain_size / (height - 1)

        vertices = []

        for z in range(height):

            for x in range(width):

                if self.settlementmap[z, x] < 0.5:
                    continue

                world_x = (
                    x * x_step
                    - terrain_size / 2.0
                )

                world_z = (
                    z * z_step
                    - terrain_size / 2.0
                )

                elevation = float(
                    self.normalized_heightmap[z, x]
                )

                world_y = (
                    elevation * vertical_scale
                )

                vertices.extend([
                    world_x,
                    world_y,
                    world_z
                ])

        return np.asarray(
            vertices,
            dtype=np.float32
        )

    # ========================================================
    # INDICES
    # ========================================================

    def create_indices(self, width, height):

        indices = []

        for z in range(height - 1):

            for x in range(width - 1):

                top_left = z * width + x
                top_right = top_left + 1
                bottom_left = (
                    (z + 1) * width + x
                )
                bottom_right = bottom_left + 1

                indices.extend([
                    top_left,
                    bottom_left,
                    top_right
                ])

                indices.extend([
                    top_right,
                    bottom_left,
                    bottom_right
                ])

        return np.asarray(
            indices,
            dtype=np.uint32
        )

    # ========================================================
    # RENDER
    # ========================================================

    def render(self, camera, aspect_ratio):

        model = glm.mat4(1.0)

        view = camera.get_view_matrix()

        projection = glm.perspective(
            glm.radians(45.0),
            aspect_ratio,
            0.1,
            100.0
        )

        # ----------------------------------------------------
        # TERRAIN
        # ----------------------------------------------------

        if self.show_terrain:

            self.set_matrices(
                self.terrain_program,
                model,
                view,
                projection
            )

            self.terrain_vertex_array.render(
                mode=moderngl.TRIANGLES
            )

        # ----------------------------------------------------
        # TRANSPARENT OVERLAYS
        # ----------------------------------------------------

        self.context.enable(
            moderngl.BLEND
        )

        self.context.blend_func = (
            moderngl.SRC_ALPHA,
            moderngl.ONE_MINUS_SRC_ALPHA
        )

        # ----------------------------------------------------
        # WATER
        # ----------------------------------------------------

        if self.show_water:

            self.set_matrices(
                self.water_program,
                model,
                view,
                projection
            )

            self.water_vertex_array.render(
                mode=moderngl.TRIANGLES
            )

        # ----------------------------------------------------
        # RISK
        # ----------------------------------------------------

        if self.show_risk:

            self.set_matrices(
                self.risk_program,
                model,
                view,
                projection
            )

            self.risk_vertex_array.render(
                mode=moderngl.TRIANGLES
            )

        # ----------------------------------------------------
        # SETTLEMENTS
        # ----------------------------------------------------

        if self.show_settlements:

            self.set_matrices(
                self.settlement_program,
                model,
                view,
                projection
            )

            self.context.point_size = 5.0

            self.settlement_vertex_array.render(
                mode=moderngl.POINTS
            )

        self.context.disable(
            moderngl.BLEND
        )

    # ========================================================
    # MATRIX SETUP
    # ========================================================

    def set_matrices(
        self,
        program,
        model,
        view,
        projection
    ):

        program["model"].write(
            mat4_bytes(model)
        )

        program["view"].write(
            mat4_bytes(view)
        )

        program["projection"].write(
            mat4_bytes(projection)
        )
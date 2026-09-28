"""
n_camera.py

HydroTerra camera controls.

The camera orbits around the centre of the terrain
and allows the user to zoom in and out.
"""

import glm


class Camera:

    def __init__(self):

        # ----------------------------------------------------
        # CAMERA TARGET
        # ----------------------------------------------------

        # The camera looks at the centre of the terrain.
        self.target = glm.vec3(
            0.0,
            0.5,
            0.0
        )

        # ----------------------------------------------------
        # CAMERA DISTANCE
        # ----------------------------------------------------

        # Our terrain is approximately 8 units wide,
        # so 12 units gives us a comfortable starting view.
        self.distance = 12.0

        # ----------------------------------------------------
        # CAMERA ROTATION
        # ----------------------------------------------------

        self.yaw = 45.0

        self.pitch = 35.0

    # ========================================================
    # CAMERA POSITION
    # ========================================================

    def get_position(self):

        yaw = glm.radians(
            self.yaw
        )

        pitch = glm.radians(
            self.pitch
        )

        # Convert spherical coordinates
        # into a 3D position.

        x = (
            self.distance
            * glm.cos(pitch)
            * glm.sin(yaw)
        )

        y = (
            self.distance
            * glm.sin(pitch)
        )

        z = (
            self.distance
            * glm.cos(pitch)
            * glm.cos(yaw)
        )

        return (
            self.target
            + glm.vec3(x, y, z)
        )

    # ========================================================
    # VIEW MATRIX
    # ========================================================

    def get_view_matrix(self):

        position = self.get_position()

        return glm.lookAt(
            position,
            self.target,
            glm.vec3(
                0.0,
                1.0,
                0.0
            )
        )

    # ========================================================
    # ZOOM
    # ========================================================

    def zoom(self, amount):

        self.distance -= amount

        # Don't get too close.
        self.distance = max(
            3.0,
            self.distance
        )

        # Don't go too far away.
        self.distance = min(
            30.0,
            self.distance
        )

    # ========================================================
    # ORBIT
    # ========================================================

    def orbit(self, dx, dy):

        self.yaw += dx

        self.pitch += dy

        # Prevent the camera from flipping.
        self.pitch = max(
            -80.0,
            min(80.0, self.pitch)
        )
from numba import njit
import numpy as np
import glm
import math

# Resolution
WIN_RES = glm.vec2(1600, 900) # Window resolution

# Chunk
CHUNK_SIZE = 32
H_CHUNK_SIZE = CHUNK_SIZE // 2
CHUNK_AREA = CHUNK_SIZE * CHUNK_SIZE
CHUNK_VOL = CHUNK_AREA * CHUNK_SIZE

# Camera
ASPECT_RATIO = WIN_RES.x / WIN_RES.y
FOV_DEG = 50 # Field of view degrees
V_FOV = glm.radians(FOV_DEG) # Vertical field of view
H_FOV = 2 * math.atan(math.tan(V_FOV * 0.5) * ASPECT_RATIO) # Horizontal field of view
NEAR = 0.1 # Near clipping plane
FAR = 2000.0 # Far clipping plane
PITCH_MAX = glm.radians(89) # Maximum allowed pitch

# Player
PLAYER_SPEED = 0.005
PLAYER_ROT_SPEED = 0.003 # Rotation speed
PLAYER_POS = glm.vec3(H_CHUNK_SIZE, CHUNK_SIZE, 1.5 * CHUNK_SIZE) # Position
MOUSE_SENSITIVITY = 0.002

# Colors
BG_COLOR = glm.vec3(0, 0.6, 0.6) # Background color
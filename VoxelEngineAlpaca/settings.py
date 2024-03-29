from numba import njit
import numpy as np
import glm
import math

# Resolution
WIN_RES = glm.vec2(1600, 900)  # Window resolution

# Ray casts
MAX_RAY_DIST = 6  # Maximum distance of the ray cast measured in voxels

# World generation
SEED = 16

# Tree settings
TREE_PROBABILITY = 0.02
TREE_WIDTH, TREE_HEIGHT = 4, 8
TREE_H_WIDTH, TREE_H_HEIGHT = TREE_WIDTH // 2, TREE_HEIGHT // 2

# Textures
AIR = 0
SAND = 1
GRASS = 2
DIRT = 3
STONE = 4
SNOW = 5
LEAVES = 6
OAK_LOG = 7

# Terrain levels
SNOW_LEVEL = 54
STONE_LEVEL = 49
DIRT_LEVEL = 40
GRASS_LEVEL = 8
SAND_LEVEL = 7

# Chunk
CHUNK_SIZE = 48
H_CHUNK_SIZE = CHUNK_SIZE // 2  # Height
CHUNK_AREA = CHUNK_SIZE * CHUNK_SIZE
CHUNK_VOL = CHUNK_AREA * CHUNK_SIZE  # Volume
CHUNK_SPHERE_RADIUS = H_CHUNK_SIZE * math.sqrt(3)  # Radius of sphere around the chunk for frustum culling0

# World
WORLD_W, WORLD_H = 20, 2  # Width and Height
WORLD_D = WORLD_W  # Depth
WORLD_AREA = WORLD_W * WORLD_D
WORLD_VOL = WORLD_AREA * WORLD_H  # Volume

# Water
WATER_LINE = 5.6
WATER_AREA = 5 * CHUNK_SIZE * WORLD_W

# Clouds
CLOUD_SCALE = 25
CLOUD_HEIGHT = WORLD_H * CHUNK_SIZE * 2

# World Center
CENTER_XZ = WORLD_W * H_CHUNK_SIZE
CENTER_Y = WORLD_H * H_CHUNK_SIZE

# Camera
ASPECT_RATIO = WIN_RES.x / WIN_RES.y
FOV_DEG = 50  # Field of view degrees
V_FOV = glm.radians(FOV_DEG)  # Vertical field of view
H_FOV = 2 * math.atan(math.tan(V_FOV * 0.5) * ASPECT_RATIO)  # Horizontal field of view
NEAR = 0.1  # Near clipping plane
FAR = 2000.0  # Far clipping plane
PITCH_MAX = glm.radians(89)  # Maximum allowed pitch

# Player
PLAYER_SPEED = 0.05
PLAYER_ROT_SPEED = 0.003  # Rotation speed
PLAYER_POS = glm.vec3(CENTER_XZ, WORLD_H * CHUNK_SIZE, CENTER_XZ)  # Position
MOUSE_SENSITIVITY = 0.002

# Colors
SKY_COLOR = glm.vec3(0.463, 0.706, 0.996)  # Sky color

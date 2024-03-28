from noise import noise2, noise3
from random import random
from settings import *


# This will use 2D noise for the creation of heightmaps and 3D noise for the creation of caves
# Uses fractional Brownian motion to generate octaves
@njit
def get_height(x, z):
    # Island mask
    island = 1 / (pow(0.0025 * math.hypot(x - CENTER_XZ, z - CENTER_XZ), 20) + 0.0001)
    island = min(island, 1)

    # Amplitude
    a1 = CENTER_Y
    a2, a4, a8 = a1 * 0.5, a1 * 0.25, a1 * 0.125  # Fractional Brownian motion

    # Frequency
    f1 = 0.005
    f2, f4, f8 = f1 * 2, f1 * 4, f1 * 8  # Fractional Brownian motion

    # Erosion effect
    if noise2(0.1 * x, 0.1 * z) < 0:
        a1 /= 1.03

    height = 0
    height += noise2(x * f1, z * f1) * a1 + a1
    height += noise2(x * f2, z * f2) * a2 - a2
    height += noise2(x * f4, z * f4) * a4 + a4
    height += noise2(x * f8, z * f8) * a8 - a8

    height = max(height, 1)
    height *= island  # Turn the world into more of an island

    return int(height)


@njit
def get_index(x, y, z):
    return x + CHUNK_SIZE * z + CHUNK_AREA * y


@njit
def set_voxel_id(voxels, x, y, z, wx, wy, wz, world_height):
    voxel_id = 0

    if wy < world_height - 1:
        # Create cave systems
        if (noise3(wx * 0.09, wy * 0.09, wz * 0.09) > 0 and
                noise2(wx * 0.1, wz * 0.1) * 3 + 3 < wy < world_height - 10):
            voxel_id = AIR
        else:
            voxel_id = STONE
    else:
        rng = int(7 * random())
        ry = wy - rng
        if SNOW_LEVEL <= ry < world_height:
            voxel_id = SNOW
        elif STONE_LEVEL <= ry < SNOW_LEVEL:
            voxel_id = STONE
        elif DIRT_LEVEL <= ry < STONE_LEVEL:
            voxel_id = DIRT
        elif GRASS_LEVEL <= ry < DIRT_LEVEL:
            voxel_id = GRASS
        else:
            voxel_id = SAND

    # Setting the voxel ID
    voxels[get_index(x, y, z)] = voxel_id

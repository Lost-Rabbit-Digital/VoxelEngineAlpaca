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

    # Tree placement
    if wy < DIRT_LEVEL:
        place_tree(voxels, x, y, z, voxel_id)


@njit
def place_tree(voxels, x, y, z, voxel_id):
    rnd = random()
    if voxel_id != GRASS or rnd > TREE_PROBABILITY:
        return None
    if y + TREE_HEIGHT >= CHUNK_SIZE:
        return None
    if x - TREE_H_WIDTH < 0 or x + TREE_H_WIDTH >= CHUNK_SIZE:
        return None
    if z - TREE_H_WIDTH < 0 or z + TREE_H_WIDTH >= CHUNK_SIZE:
        return None

    # Place a voxel of dirt under the tree
    voxels[get_index(x, y, z)] = DIRT

    # Base leaves
    m = 0
    for n, iy in enumerate(range(TREE_H_HEIGHT, TREE_HEIGHT - 1)):
        k = iy % 2
        rng = int(random() * 2)
        for ix in range(-TREE_H_WIDTH + m, TREE_H_WIDTH - m * rng):
            for iz in range(-TREE_H_WIDTH + m * rng, TREE_H_WIDTH - m):
                if (ix + iz) % 4:
                    voxels[get_index(x + ix + k, y + iy, z + iz + k)] = LEAVES
        m += 1 if n > 0 else 3 if n > 1 else 0

    # Top leaves
    voxels[get_index(x, y + TREE_HEIGHT - 2, z)] = LEAVES

    # Tree trunk
    for iy in range(1, TREE_HEIGHT - 2):
        voxels[get_index(x, y + iy, z)] = OAK_LOG

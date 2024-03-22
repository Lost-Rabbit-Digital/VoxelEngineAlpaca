from settings import *

def get_chunk_index(world_voxel_pos):
    wx, wy, wz = world_voxel_pos
    cx = wx // CHUNK_SIZE
    cy = wy // CHUNK_SIZE
    cz = wz // CHUNK_SIZE
    # Check if the coordinates of the chunk are beyond the boundaries of the world
    if not (0 <= cx < WORLD_W and 0 <= cy < WORLD_H and 0 <= cz < WORLD_D): 
        return -1

    index = cx + WORLD_W * cz + WORLD_AREA * cy
    return index

# Used to check the surroundings of the voxel for empty space.
def is_void(local_voxel_pos, world_voxel_pos, world_voxels):
    chunk_index = get_chunk_index(world_voxel_pos)
    if chunk_index == -1:
        return False
    chunk_voxels = world_voxels[chunk_index]

    x, y, z = local_voxel_pos
    voxel_index = x % CHUNK_SIZE + z % CHUNK_SIZE * CHUNK_SIZE + y % CHUNK_SIZE * CHUNK_AREA

    if chunk_voxels[voxel_index]:
        return False
    return True

# Adds vertex attributes to the vertex data array.
def add_data(vertex_data, index, *vertices):
    for vertex in vertices:
        for attr in vertex:
            vertex_data[index] = attr
            index += 1
    return index


# Builds the mesh for the chunk of voxels.
def build_chunk_mesh(chunk_voxels, format_size, chunk_pos, world_voxels):
    # ARRAY_SIZE = CHUNK_VOL * NUM_VOXEL_VERTICES * VERTEX_ATTRS
    # I use unsigned eight bit integers, so each vertex attribute will take one byte in GPU memory.
    # Each vertex will have five attributes:
    # 1. X
    # 2. y
    # 3. z
    # 4. voxel_id
    # 5. face_id
    vertex_data = np.empty(CHUNK_VOL * 18 * format_size, dtype='uint8')
    index = 0

    # Iterate over the chunk.
    for x in range(CHUNK_SIZE):
        for y in range(CHUNK_SIZE):
            for z in range(CHUNK_SIZE):
                voxel_id = chunk_voxels[x + CHUNK_SIZE * z + CHUNK_AREA * y]
                # Ignore voxels that represent empty space.
                if not voxel_id:
                    continue

                # Voxel world position
                cx, cy, cz = chunk_pos
                wx = x + cx * CHUNK_SIZE
                wy = y + cy * CHUNK_SIZE
                wz = z + cz * CHUNK_SIZE

                # Each face check will have the following format: x, y, z, voxel_id, face_id.
                # Top face of voxel.
                if is_void((x, y + 1, z), (wx, wy + 1, wz), world_voxels):
                    # If there is a void then form the attributes for the current face of the voxel.
                    vertex0 = (x    , y + 1, z    , voxel_id, 0)
                    vertex1 = (x + 1, y + 1, z    , voxel_id, 0)
                    vertex2 = (x + 1, y + 1, z + 1, voxel_id, 0)
                    vertex3 = (x    , y + 1, z + 1, voxel_id, 0)

                    # Using the add_data method this will form two triangles from the formed vertex data.
                    index = add_data(vertex_data, index, vertex0, vertex3, vertex2, vertex0, vertex2, vertex1)

                # Bottom face of the voxel.
                if is_void((x, y - 1, z), (wx, wy - 1, wz), world_voxels):
                    vertex0 = (x    , y, z    , voxel_id, 1)
                    vertex1 = (x + 1, y, z    , voxel_id, 1)
                    vertex2 = (x + 1, y, z + 1, voxel_id, 1)
                    vertex3 = (x    , y, z + 1, voxel_id, 1)

                    index = add_data(vertex_data, index, vertex0, vertex2, vertex3, vertex0, vertex1, vertex2)

                # Right face of the voxel.
                if is_void((x + 1, y, z), (wx + 1, wy, wz), world_voxels):
                    vertex0 = (x + 1, y    , z    , voxel_id, 2)
                    vertex1 = (x + 1, y + 1, z    , voxel_id, 2)
                    vertex2 = (x + 1, y + 1, z + 1, voxel_id, 2)
                    vertex3 = (x + 1, y    , z + 1, voxel_id, 2)

                    index = add_data(vertex_data, index, vertex0, vertex1, vertex2, vertex0, vertex2, vertex3)

                # Left face of the voxel.
                if is_void((x - 1, y, z), (wx - 1, wy, wz), world_voxels):
                    vertex0 = (x, y    , z    , voxel_id, 3)
                    vertex1 = (x, y + 1, z    , voxel_id, 3)
                    vertex2 = (x, y + 1, z + 1, voxel_id, 3)
                    vertex3 = (x, y    , z + 1, voxel_id, 3)

                    index = add_data(vertex_data, index, vertex0, vertex2, vertex1, vertex0, vertex3, vertex2)

                # Back face of the voxel.
                if is_void((x, y, z - 1), (wx, wy, wz - 1), world_voxels):
                    vertex0 = (x    , y    , z, voxel_id, 4)
                    vertex1 = (x    , y + 1, z, voxel_id, 4)
                    vertex2 = (x + 1, y + 1, z, voxel_id, 4)
                    vertex3 = (x + 1, y    , z, voxel_id, 4)

                    index = add_data(vertex_data, index, vertex0, vertex1, vertex2, vertex0, vertex2, vertex3)

                # Front face of the voxel.
                if is_void((x, y, z + 1), (wx, wy, wz + 1), world_voxels):
                    vertex0 = (x    , y    , z + 1, voxel_id, 5)
                    vertex1 = (x    , y + 1, z + 1, voxel_id, 5)
                    vertex2 = (x + 1, y + 1, z + 1, voxel_id, 5)
                    vertex3 = (x + 1, y    , z + 1, voxel_id, 5)

                    index = add_data(vertex_data, index, vertex0, vertex2, vertex1, vertex0, vertex3, vertex2)

    return vertex_data[:index + 1]

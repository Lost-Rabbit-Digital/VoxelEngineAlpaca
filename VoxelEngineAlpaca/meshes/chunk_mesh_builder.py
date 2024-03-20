from settings import *

# Used to check the surroundings of the voxel for empty space.
def is_empty(voxel_pos, chunk_voxels):
    x, y, z = voxel_pos

    # Check if the coordinates go beyond the boundaries of the chunk.
    if 0 <= x < CHUNK_SIZE and 0 <= y < CHUNK_SIZE and 0 <= z < CHUNK_SIZE:
        # Make sure the voxel is not empty space.
        if chunk_voxels[x + CHUNK_SIZE * z + CHUNK_AREA * y]:
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
def build_chunk_mesh(chunk_voxels):
    # ARRAY_SIZE = CHUNK_VOL * NUM_VOXEL_VERTICES * VERTEX_ATTRS
    # I use unsigned eight bit integers, so each vertex attribute will take one byte in GPU memory.
    # Each vertex will have five attributes:
    # 1. X
    # 2. y
    # 3. z
    # 4. voxel_id
    # 5. face_id
    vertex_data = np.empty(CHUNK_VOL * 18 * 5, dtype='uint8')
    index = 0

    # Iterate over the chunk.
    for x in range(CHUNK_SIZE):
        for y in range(CHUNK_SIZE):
            for z in range(CHUNK_SIZE):
                voxel_id = chunk_voxels[x + CHUNK_SIZE * z + CHUNK_AREA * y]
                # Ignore voxels that represent empty space.
                if not voxel_id:
                    continue

                # Each face check will have the following format: x, y, z, voxel_id, face_id.
                # Top face of voxel.
                if is_empty((x, y + 1, z), chunk_voxels):
                    # If there is a void then form the attributes for the current face of the voxel.
                    vertex0 = (x, y + 1, z, voxel_id, 0)
                    vertex1 = (x + 1, y + 1, z, voxel_id, 0)
                    vertex2 = (x + 1, y + 1, z + 1, voxel_id, 0)
                    vertex3 = (x, y + 1, z + 1, voxel_id, 0)

                    # Using the add_data method this will form two triangles from the formed vertex data.
                    index = add_data(vertex_data, index, vertex0, vertex3, vertex2, vertex0, vertex2, vertex1)

                # Bottom face of the voxel.
                if is_empty((x, y - 1, z), chunk_voxels):
                    vertex0 = (x, y, z, voxel_id, 1)
                    vertex1 = (x + 1, y, z, voxel_id, 1)
                    vertex2 = (x + 1, y, z + 1, voxel_id, 1)
                    vertex3 = (x, y, z + 1, voxel_id, 1)

                    index = add_data(vertex_data, index, vertex0, vertex2, vertex3, vertex0, vertex1, vertex2)

                # Left face of the voxel.
                if is_empty((x - 1, y, z), chunk_voxels):
                    vertex0 = (x, y, z, voxel_id, 3)
                    vertex1 = (x, y + 1, z, voxel_id, 3)
                    vertex2 = (x, y + 1, z + 1, voxel_id, 3)
                    vertex3 = (x, y, z + 1, voxel_id, 3)

                    index = add_data(vertex_data, index, vertex0, vertex2, vertex1, vertex0, vertex3, vertex2)

                # Right face of the voxel.
                if is_empty((x + 1, y, z), chunk_voxels):
                    vertex0 = (x + 1, y, z, voxel_id, 2)
                    vertex1 = (x + 1, y + 1, z, voxel_id, 2)
                    vertex2 = (x + 1, y + 1, z + 1, voxel_id, 2)
                    vertex3 = (x + 1, y, z + 1, voxel_id, 2)

                    index = add_data(vertex_data, index, vertex0, vertex1, vertex2, vertex0, vertex2, vertex3)

                # Back face of the voxel.
                if is_empty((x, y, z - 1), chunk_voxels):
                    vertex0 = (x, y, z, voxel_id, 4)
                    vertex1 = (x, y + 1, z, voxel_id, 4)
                    vertex2 = (x + 1, y + 1, z, voxel_id, 4)
                    vertex3 = (x + 1, y, z, voxel_id, 4)

                    index = add_data(vertex_data, index, vertex0, vertex1, vertex2, vertex0, vertex2, vertex3)

                # Front face of the voxel.
                if is_empty((x, y, z + 1), chunk_voxels):
                    vertex0 = (x, y, z + 1, voxel_id, 4)
                    vertex1 = (x, y + 1, z + 1, voxel_id, 4)
                    vertex2 = (x + 1, y + 1, z + 1, voxel_id, 4)
                    vertex3 = (x + 1, y, z + 1, voxel_id, 4)

                    index = add_data(vertex_data, index, vertex0, vertex2, vertex1, vertex0, vertex3, vertex2)

    return vertex_data[:index + 1]
from settings import *
from numba import uint8


@njit
def get_ao(local_pos, world_pos, world_voxels, plane):
    x, y, z = local_pos
    wx, wy, wz = world_pos

    # Top and bottom faces, which belong to the 'Y' plane
    if plane == 'Y':
        # Check all eight voxels that could surround the face, A-H
        a = is_void((x, y, z - 1), (wx, wy, wz - 1), world_voxels)
        b = is_void((x - 1, y, z - 1), (wx - 1, wy, wz - 1), world_voxels)
        c = is_void((x - 1, y, z), (wx - 1, wy, wz), world_voxels)
        d = is_void((x - 1, y, z + 1), (wx - 1, wy, wz + 1), world_voxels)
        e = is_void((x, y, z + 1), (wx, wy, wz + 1), world_voxels)
        f = is_void((x + 1, y, z + 1), (wx + 1, wy, wz + 1), world_voxels)
        g = is_void((x + 1, y, z), (wx + 1, wy, wz), world_voxels)
        h = is_void((x + 1, y, z - 1), (wx + 1, wy, wz - 1), world_voxels)

    # Front and back faces, which belong to the 'X' plane
    elif plane == 'X':
        a = is_void((x, y, z - 1), (wx, wy, wz - 1), world_voxels)
        b = is_void((x, y - 1, z - 1), (wx, wy - 1, wz - 1), world_voxels)
        c = is_void((x, y - 1, z), (wx, wy - 1, wz), world_voxels)
        d = is_void((x, y - 1, z + 1), (wx, wy - 1, wz + 1), world_voxels)
        e = is_void((x, y, z + 1), (wx, wy, wz + 1), world_voxels)
        f = is_void((x, y + 1, z + 1), (wx, wy + 1, wz + 1), world_voxels)
        g = is_void((x, y + 1, z), (wx, wy + 1, wz), world_voxels)
        h = is_void((x, y + 1, z - 1), (wx, wy + 1, wz - 1), world_voxels)

        # Left and right faces, which belong to the 'Z' plane
    else:
        a = is_void((x - 1, y, z), (wx - 1, wy, wz), world_voxels)
        b = is_void((x - 1, y - 1, z), (wx - 1, wy - 1, wz), world_voxels)
        c = is_void((x, y - 1, z), (wx, wy - 1, wz), world_voxels)
        d = is_void((x + 1, y - 1, z), (wx + 1, wy - 1, wz), world_voxels)
        e = is_void((x + 1, y, z), (wx + 1, wy, wz), world_voxels)
        f = is_void((x + 1, y + 1, z), (wx + 1, wy + 1, wz), world_voxels)
        g = is_void((x, y + 1, z), (wx, wy + 1, wz), world_voxels)
        h = is_void((x - 1, y + 1, z), (wx - 1, wy + 1, wz), world_voxels)

    ao = (a + b + c), (g + h + a), (e + f + g), (c + d + e)
    return ao


@njit
def pack_data(x, y, z, voxel_id, face_id, ao_id, flip_id):
    # x: 6 bits, y: 6 bits, z: 6 bits, voxel_id: 8 bits, face_id: 3 bits, ao_id: 2 bits, flip_id: 1 bit
    a, b, c, d, e, f, g = x, y, z, voxel_id, face_id, ao_id, flip_id

    b_bit, c_bit, d_bit, e_bit, f_bit, g_bit = 6, 6, 8, 3, 2, 1
    fg_bit = f_bit + g_bit
    efg_bit = e_bit + fg_bit
    defg_bit = d_bit + efg_bit
    cdefg_bit = c_bit + defg_bit
    bcdefg_bit = b_bit + cdefg_bit

    packed_data = (
        a << bcdefg_bit |
        b << cdefg_bit |
        c << defg_bit |
        d << efg_bit |
        e << fg_bit |
        f << g_bit | g
    )
    return packed_data


@njit
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
@njit
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
@njit
def add_data(vertex_data, index, *vertices):
    for vertex in vertices:
        vertex_data[index] = vertex
        index += 1
    return index


# Builds the mesh for the chunk of voxels.
@njit
def build_chunk_mesh(chunk_voxels, format_size, chunk_pos, world_voxels):
    # ARRAY_SIZE = CHUNK_VOL * NUM_VOXEL_VERTICES * VERTEX_ATTRS
    # I use unsigned eight bit integers, so each vertex attribute will take one byte in GPU memory.
    # Each vertex will have seven attributes:
    # 1. X
    # 2. y
    # 3. z
    # 4. voxel_id
    # 5. face_id
    # 6. ao_id
    # 7. flip_id
    vertex_data = np.empty(CHUNK_VOL * 18 * format_size, dtype='uint32')
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
                    # Get the ambient occlusion values for our mesh plane.
                    ao = get_ao((x, y + 1, z), (wx, wy + 1, wz), world_voxels, plane='Y')
                    flip_id = ao[1] + ao[3] > ao[0] + ao[2]

                    # If there is a void then form the attributes for the current face of the voxel.
                    vertex0 = pack_data(x, y + 1, z, voxel_id, 0, ao[0], flip_id)
                    vertex1 = pack_data(x + 1, y + 1, z, voxel_id, 0, ao[1], flip_id)
                    vertex2 = pack_data(x + 1, y + 1, z + 1, voxel_id, 0, ao[2], flip_id)
                    vertex3 = pack_data(x, y + 1, z + 1, voxel_id, 0, ao[3], flip_id)

                    # Fixes anisotropy in ambient occlusion
                    # When the condition is met the order of triangle vertices is flipped to maintain AO
                    if flip_id:
                        # Using the add_data method this will form two triangles from the formed vertex data.
                        index = add_data(vertex_data, index, vertex1, vertex0, vertex3, vertex1, vertex3, vertex2)
                    else:
                        index = add_data(vertex_data, index, vertex0, vertex3, vertex2, vertex0, vertex2, vertex1)

                # Bottom face of the voxel.
                if is_void((x, y - 1, z), (wx, wy - 1, wz), world_voxels):
                    ao = get_ao((x, y - 1, z), (wx, wy - 1, wz), world_voxels, plane='Y')
                    flip_id = ao[1] + ao[3] > ao[0] + ao[2]

                    vertex0 = pack_data(x, y, z, voxel_id, 1, ao[0], flip_id)
                    vertex1 = pack_data(x + 1, y, z, voxel_id, 1, ao[1], flip_id)
                    vertex2 = pack_data(x + 1, y, z + 1, voxel_id, 1, ao[2], flip_id)
                    vertex3 = pack_data(x, y, z + 1, voxel_id, 1, ao[3], flip_id)

                    if flip_id:
                        index = add_data(vertex_data, index, vertex1, vertex3, vertex0, vertex1, vertex2, vertex3)
                    else:
                        index = add_data(vertex_data, index, vertex0, vertex2, vertex3, vertex0, vertex1, vertex2)

                # Right face of the voxel.
                if is_void((x + 1, y, z), (wx + 1, wy, wz), world_voxels):
                    ao = get_ao((x + 1, y, z), (wx + 1, wy, wz), world_voxels, plane='X')
                    flip_id = ao[1] + ao[3] > ao[0] + ao[2]

                    vertex0 = pack_data(x + 1, y, z, voxel_id, 2, ao[0], flip_id)
                    vertex1 = pack_data(x + 1, y + 1, z, voxel_id, 2, ao[1], flip_id)
                    vertex2 = pack_data(x + 1, y + 1, z + 1, voxel_id, 2, ao[2], flip_id)
                    vertex3 = pack_data(x + 1, y, z + 1, voxel_id, 2, ao[3], flip_id)

                    if flip_id:
                        index = add_data(vertex_data, index, vertex3, vertex0, vertex1, vertex3, vertex1, vertex2)
                    else:
                        index = add_data(vertex_data, index, vertex0, vertex1, vertex2, vertex0, vertex2, vertex3)

                # Left face of the voxel.
                if is_void((x - 1, y, z), (wx - 1, wy, wz), world_voxels):
                    ao = get_ao((x - 1, y, z), (wx - 1, wy, wz), world_voxels, plane='X')
                    flip_id = ao[1] + ao[3] > ao[0] + ao[2]

                    vertex0 = pack_data(x, y, z, voxel_id, 3, ao[0], flip_id)
                    vertex1 = pack_data(x, y + 1, z, voxel_id, 3, ao[1], flip_id)
                    vertex2 = pack_data(x, y + 1, z + 1, voxel_id, 3, ao[2], flip_id)
                    vertex3 = pack_data(x, y, z + 1, voxel_id, 3, ao[3], flip_id)

                    if flip_id:
                        index = add_data(vertex_data, index, vertex3, vertex1, vertex0, vertex3, vertex2, vertex1)
                    else:
                        index = add_data(vertex_data, index, vertex0, vertex2, vertex1, vertex0, vertex3, vertex2)

                # Back face of the voxel.
                if is_void((x, y, z - 1), (wx, wy, wz - 1), world_voxels):
                    ao = get_ao((x, y, z - 1), (wx, wy, wz - 1), world_voxels, plane='Z')
                    flip_id = ao[1] + ao[3] > ao[0] + ao[2]

                    vertex0 = pack_data(x, y, z, voxel_id, 4, ao[0], flip_id)
                    vertex1 = pack_data(x, y + 1, z, voxel_id, 4, ao[1], flip_id)
                    vertex2 = pack_data(x + 1, y + 1, z, voxel_id, 4, ao[2], flip_id)
                    vertex3 = pack_data(x + 1, y, z, voxel_id, 4, ao[3], flip_id)

                    if flip_id:
                        index = add_data(vertex_data, index, vertex3, vertex0, vertex1, vertex3, vertex1, vertex2)
                    else:
                        index = add_data(vertex_data, index, vertex0, vertex1, vertex2, vertex0, vertex2, vertex3)

                # Front face of the voxel.
                if is_void((x, y, z + 1), (wx, wy, wz + 1), world_voxels):
                    ao = get_ao((x, y, z + 1), (wx, wy, wz + 1), world_voxels, plane='Z')
                    flip_id = ao[1] + ao[3] > ao[0] + ao[2]

                    vertex0 = pack_data(x, y, z + 1, voxel_id, 5, ao[0], flip_id)
                    vertex1 = pack_data(x, y + 1, z + 1, voxel_id, 5, ao[1], flip_id)
                    vertex2 = pack_data(x + 1, y + 1, z + 1, voxel_id, 5, ao[2], flip_id)
                    vertex3 = pack_data(x + 1, y, z + 1, voxel_id, 5, ao[3], flip_id)

                    if flip_id:
                        index = add_data(vertex_data, index, vertex3, vertex1, vertex0, vertex3, vertex2, vertex1)
                    else:
                        index = add_data(vertex_data, index, vertex0, vertex2, vertex1, vertex0, vertex3, vertex2)

    return vertex_data[:index + 1]

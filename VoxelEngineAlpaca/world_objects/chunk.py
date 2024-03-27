import random

from settings import *
from meshes.chunk_mesh import ChunkMesh

# VOXEL ID:
# The voxels ids are between 0-255
# 0 is an empty space
# 1-255 are different types of voxels

# VOXEL ARRAYS:
# Instead of 3D arrays I'm using 1D arrays converted to 3D using the following formula:
# AREA = SIZE * SIZE
# IDX = X + (SIZE * Z) + (AREA * Y)

class Chunk:
    def __init__(self, world, position):
        self.app = world.app
        self.world = world
        self.position = position
        self.m_model = self.get_model_matrix()
        self.voxels: np.array = None
        self.mesh: ChunkMesh = None
        self.is_empty = True

        self.center = (glm.vec3(self.position) + 0.5) * CHUNK_SIZE
        self.is_on_frustum = self.app.player.frustum.is_on_frustum

    # Get the model matrix of the chunk based on its coordinates in the world.
    def get_model_matrix(self):
        m_model = glm.translate(glm.mat4(), glm.vec3(self.position) * CHUNK_SIZE)
        return m_model

    # Set the m_model matrix as a uniform in the shader before rendering the chunk.
    def set_uniform(self):
        self.mesh.program['m_model'].write(self.m_model)

    def build_mesh(self):
        self.mesh = ChunkMesh(self)

    def render(self):
        if not self.is_empty:
            self.set_uniform()
            self.mesh.render()

    def build_voxels(self):
        # Empty chunk
        voxels = np.zeros(CHUNK_VOL, dtype='uint8')

        # Fill chunk
        # Chunk coordinates
        cx, cy, cz = glm.ivec3(self.position) * CHUNK_SIZE
        rng = random.randrange(1, 100)

        for x in range(CHUNK_SIZE):
            for z in range(CHUNK_SIZE):
                wx = x + cx
                wz = z + cz
                world_height = int(glm.simplex(glm.vec2(wx, wz) * 0.01) * 32 + 32)
                local_height = min(world_height - cy, CHUNK_SIZE)

                for y in range(local_height):
                    wy = y + cy
                    voxels[x + CHUNK_SIZE * z + CHUNK_AREA * y] = wy + 1  # Default world generation
                    #voxels[x + CHUNK_SIZE * z + CHUNK_AREA * y] = rng  # Each chunk has its own color

        if np.any(voxels):
            self.is_empty = False

        return voxels

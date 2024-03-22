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
        self.voxels: np.array = None
        self.mesh: ChunkMesh = None
        self.build_mesh()

    def build_mesh(self):
        self.mesh = ChunkMesh(self)

    def render(self):
        self.mesh.render()

    def build_voxels(self):
        # Empty chunk
        voxels = np.zeros(CHUNK_VOL, dtype='uint8')

        # Fill chunk
        for x in range(CHUNK_SIZE):
            for z in range(CHUNK_SIZE):
                for y in range(CHUNK_SIZE):
                    # Simplex function for 3D noise
                    voxels[x + CHUNK_SIZE * z + CHUNK_AREA * y] = (
                        x + y + z if int(glm.simplex(glm.vec3(x, y, z) * 0.1) + 1) else 0
                    )
                    # Primitive 3D chunk
                    #voxels[x + CHUNK_SIZE * z + CHUNK_AREA * y] = x + y * z
        return voxels

from settings import *

# VOXEL ID:
# The voxels ids are between 0-255
# 0 is an empty space
# 1-255 are different types of voxels

# VOXEL ARRAYS:
# Instead of 3D arrays I'm using 1D arrays converted to 3D using the following formula:
# AREA = SIZE * SIZE
# IDX = X + (SIZE * Z) + (AREA * Y)

class Chunk:
    def __init__(self, app):
        self.app = app
        self.voxels: np.array = self.build_voxels()

    def build_voxels(self):
        # Empty chunk
        voxels = np.zeros(CHUNK_VOL, dtype='uint8')
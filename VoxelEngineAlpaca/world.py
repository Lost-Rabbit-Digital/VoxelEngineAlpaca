from settings import *
from world_objects.chunk import Chunk
from voxel_handler import VoxelHandler


class World:
    def __init__(self, app):
        self.app = app
        self.chunks = [None for _ in range(WORLD_VOL)]
        # All the voxels of the world will be stored in a separate 2D numpy array.
        # They will then correspond to the list of chunks which will only have a pointer to the corresponding voxels.
        self.voxels = np.empty([WORLD_VOL, CHUNK_VOL], dtype='uint8')
        self.build_chunks()
        self.build_chunk_mesh()
        self.voxel_handler = VoxelHandler(self)

    def world_update(self):
        self.voxel_handler.update()

    def build_chunks(self):
        for x in range(WORLD_W):
            for y in range(WORLD_H):
                for z in range(WORLD_D):
                    chunk = Chunk(self, position=(x, y, z))

                    # Calculate the index in the chunk array based off the position of the voxel.
                    chunk_index = x + WORLD_W * z + WORLD_AREA * y
                    self.chunks[chunk_index] = chunk

                    # Put the voxels into a separate 2D array.
                    self.voxels[chunk_index] = chunk.build_voxels()

                    # Get the pointer to the voxels.
                    chunk.voxels = self.voxels[chunk_index]

    def build_chunk_mesh(self):
        for chunk in self.chunks:
            chunk.build_mesh()

    def update(self):
        pass

    def render(self):
        for chunk in self.chunks:
            chunk.render()

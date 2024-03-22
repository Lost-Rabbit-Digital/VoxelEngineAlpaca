from settings import *
from world_objects.chunk import Chunk


class World:
    def __init__(self, app):
        self.app = app
        self.chunks = [None for _ in range(WORLD_VOL)]
        # All the voxels of the world will be stored in a separate 2D numpy array
        # They will then correspond to the list of chunks which will only have a pointer to the corresponding voxels

    def build_chunks(self):
        pass

    def build_chunk_mesh(self):
        pass

    def update(self):
        pass

    def render(self):
        pass
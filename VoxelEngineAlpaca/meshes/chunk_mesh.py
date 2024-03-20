import numpy as np

from meshes.base_mesh import BaseMesh
from meshes.chunk_mesh_builder import build_chunk_mesh

class ChunkMesh(BaseMesh):
    def __init__(self, chunk):
        super().__init__()
        self.app = chunk.app
        self.chunk = chunk
        self.ctx = self.app.ctx
        self.program = self.app.shader_program.chunk

    def get_vertex_data(self):
        mesh = build_chunk_mesh(
            chunk_voxels=self.chunk.voxels
        )
        return mesh
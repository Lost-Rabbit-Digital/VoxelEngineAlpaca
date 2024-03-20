from settings import *

def build_chunk_mesh(chunk_voxels):
    vertex_data = np.empty(CHUNK_VOL * 18 * 5, dtype='uint8')
    index = 0
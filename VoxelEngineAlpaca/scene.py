from settings import *
import moderngl as mgl
from world import World
from world_objects.voxel_marker import VoxelMarker
from world_objects.water import Water


class Scene:
    def __init__(self, app):
        self.app = app
        self.world = World(self.app)
        self.voxel_marker = VoxelMarker(self.world.voxel_handler)
        self.water = Water(app)

    def update(self):
        self.world.world_update()
        self.voxel_marker.update()

    def render(self):
        # Chunks
        self.world.render()

        # Rendering without the cull face
        self.app.ctx.disable(mgl.CULL_FACE)
        # self.clouds.render()
        self.water.render()
        self.app.ctx.enable(mgl.CULL_FACE)

        # Voxel selection indicator
        self.voxel_marker.render()

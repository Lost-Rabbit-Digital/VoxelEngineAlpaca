from settings import *


class ShaderProgram:
    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx
        self.player = app.player
        # ----- Shaders ----- #
        self.chunk = self.get_program(shader_name='chunk')
        self.voxel_marker = self.get_program(shader_name='voxel_marker')
        # ------------------- #
        self.set_uniforms_on_init()

    def set_uniforms_on_init(self):
        # Chunk
        self.chunk['m_proj'].write(self.player.m_proj)
        self.chunk['m_model'].write(glm.mat4())
        self.chunk['u_texture_array_0'] = 1
        self.chunk['sky_color'].write(SKY_COLOR)

        # Voxel marker
        self.voxel_marker['m_proj'].write(self.player.m_proj)
        self.voxel_marker['m_model'].write(glm.mat4())
        self.voxel_marker['u_texture_0'] = 0

    def update(self):
        # Pass the view matrix from the player to the shader
        self.chunk['m_view'].write(self.player.m_view)
        self.voxel_marker['m_view'].write(self.player.m_view)

    def get_program(self, shader_name):  # Pointer to OpenGL Context
        with open(f'shaders/{shader_name}.vert') as file:  # Grab the shader vert
            vertex_shader = file.read()

        with open(f'shaders/{shader_name}.frag') as file:  # Grab the shader fragment
            fragment_shader = file.read()

        # Return them to the program
        program = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
        return program

from settings import *

class ShaderProgram:
    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx
        self.player = app.player
        # ----- Shaders ----- #
        self.quad = self.get_program(shader_name='quad')
        # ------------------- #
        self.set_uniforms_on_init()

    def set_uniforms_on_init(self):
        # Pass the projection and identity model matrix from the player to the shader
        self.quad['m_proj'].write(self.player.m_proj)
        self.quad['m_model'].write(glm.mat4())

    def update(self):
        # Pass the view matrix from the player to the shader
        self.quad['m_view'].write(self.player.m_view)

    def get_program(self, shader_name): # Pointer to OpenGL Context
        with open(f'shaders/{shader_name}.vert') as file: # Grab the shader vert
            vertex_shader = file.read()

        with open(f'shaders/{shader_name}.frag') as file: # Grab the shader fragment
            fragment_shader = file.read()

        # Return them to the program
        program = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
        return program
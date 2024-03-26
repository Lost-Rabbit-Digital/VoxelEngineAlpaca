import pygame as pg
from camera import Camera
from settings import *

class Player(Camera):
    def __init__(self, app, position=PLAYER_POS, yaw=-90, pitch=0):
        self.app = app
        super().__init__(position, yaw, pitch)

    def update(self):
        self.keyboard_control()
        self.mouse_controls()
        super().update()

    # TODO: Change this to be left click to remove and right click to create voxels
    def handle_event(self, event):
        # Voxel interaction determined by mouse input
        if event.type == pg.MOUSEBUTTONDOWN:
            voxel_handler = self.app.scene.world.voxel_handler
            #  Remove voxels with left mouse button
            if event.button == 1:
                voxel_handler.set_voxel()
            #  Create voxels with right mouse button
            if event.button == 3:
                voxel_handler.switch_interaction_mode()

    # TODO: Optimise this code
    def mouse_controls(self):
        mouse_dx, mouse_dy = pg.mouse.get_rel()
        if mouse_dx:
            self.rotate_yaw(delta_x=mouse_dx * MOUSE_SENSITIVITY)
        if mouse_dy:
            self.rotate_pitch(delta_y=mouse_dy * MOUSE_SENSITIVITY)

    # TODO: Optimise this code
    def keyboard_control(self):
        key_state = pg.key.get_pressed()
        vel = PLAYER_SPEED * self.app.delta_time

        if key_state[pg.K_e]:
            self.move_up(vel)
        if key_state[pg.K_q]:
            self.move_down(vel)
        if key_state[pg.K_a]:
            self.move_left(vel)
        if key_state[pg.K_d]:
            self.move_right(vel)
        if key_state[pg.K_w]:
            self.move_forward(vel)
        if key_state[pg.K_s]:
            self.move_backward(vel)


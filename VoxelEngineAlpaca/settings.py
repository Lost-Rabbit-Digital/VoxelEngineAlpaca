from numba import njit
import numpy as np
import pygame as pg
import glm
import math

# resolution
WIN_RES = glm.vec2(1600, 900)

# colors
BG_COLOR = glm.vec3(1, 0.7, 0)

# icons
WIN_ICON = pg.image.load("VoxelEngineAlpaca/assets/icon.png")
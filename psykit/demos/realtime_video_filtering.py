#!/usr/bin/env python
# -*- coding: utf-8 -*-
# An interesting demo ("antique viewer") for `create_texture` and `draw_texture`.
# - Move mouse cursor to zoom and check image details (draw only part of the texture).
# - Click left button to de-emphasize the background (change texture global alpha)
# - Scroll to rotate the zoomed view (change texture rotation angle)
# - Press `escape` to quit.
#
# 2025-05-10: created by qcc
from math import pi
from psychopy import visual, event, core
from psykit import draw_texture, offscreen, gltools
import pyglet.gl as GL
import numpy as np


# Open window
win = visual.Window(monitor='testMonitor', units='deg', fullscr=False)
WHR = win.size[0]/win.size[1] # Window aspect ratio
# Create texture
movie = visual.MovieStim(win, filename='/Users/ccqian/Movies/figures01.mkv')
whr = movie.videoSize[0]/movie.videoSize[1] # Movie aspect ratio
# Prepare custom shader program to apply a 3x3 gaussian blur
# box_blur = offscreen.create_3x3_kernel_program(movie.videoSize, np.ones((3,3))/9*2)
box_blur = offscreen.create_separable_kernel_program(movie.videoSize, 
    x_kernel=np.ones(5)/5.0*2)
program = box_blur
movie.play()
while True:
    # Update movie texture
    movie.updateVideoFrame()
    # Draw movie texture using custom shader program
    # Flip the texture vertically: src_rect=[0,1, 1,0]
    # Scale the dst_rect to keep aspect ratio while showing the full height
    draw_texture(win, movie._textureId, src_rect=[0,1, 1,0], 
        dst_rect=np.r_[-1*whr/WHR,-1, 1*whr/WHR,1], program=program)
    # Flip
    win.flip()
    pressedKeys = event.getKeys()
    if 'escape' in pressedKeys:
        break
    elif 'h' in pressedKeys:
        program = box_blur
    elif 'space' in pressedKeys:
        program = None
# Clean up
win.close()
core.quit()

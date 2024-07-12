#!/usr/bin/env python
# -*- coding: utf-8 -*-
# An interesting demo ("antique viewer") for `create_texture` and `draw_texture`.
# - Move mouse cursor to zoom and check image details (draw only part of the texture).
# - Click left button to de-emphasize the background (change texture global alpha)
# - Scroll to rotate the zoomed view (change texture rotation angle)
# - Press `escape` to quit.
#
# 2024-07-10: created by qcc
# import sys, os.path as path
# sys.path.insert(0, path.realpath(f"{path.dirname(__file__)}/../.."))
from psychopy import visual, event, core
from psykit import create_texture, draw_texture
from matplotlib.pyplot import imread


# Open window
win = visual.Window(monitor='testMonitor', units='norm', fullscr=False, color='gray')
mouse = event.Mouse()
# Create texture
# im = imread('qtywscy.jpg')
im = imread('jgscy.png')
tex = create_texture(im)
rotation = 0
focusing = False
mouse_hold = False
while True:
    # Draw background texture
    if mouse.getPressed()[0]:
        if not mouse_hold:
            focusing = not focusing
        mouse_hold = True
    else:
        mouse_hold = False
    draw_texture(win, tex, alpha=(0.3 if focusing else 1))
    # Draw foreground texture
    x, y = mouse.getPos()
    rotation += mouse.getWheelRel()[1]
    src_rect = [(x+1)/2-0.05, (y+1)/2-0.05, (x+1)/2+0.05, (y+1)/2+0.05]
    dst_rect = [x-0.2, y-0.2, x+0.2, y+0.2]
    draw_texture(win, tex, src_rect, dst_rect, rotation)
    # Flip
    win.flip()
    if 'escape' in event.getKeys():
        break
# Clean up
win.close()
core.quit()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# An example showing how the use of offscreen window (or framebuffer) to cache
# and reuse intermediate drawing results may be helpful, especially when working
# with StereoWindow where many background stimuli will be drawn twice.
# 
# Try setting `use_buffer = False` to see the difference.
# Press `escape` to quit.
# 2024-07-06: created by qcc
# import sys, os.path as path
# sys.path.insert(0, path.realpath(f"{path.dirname(__file__)}/../.."))
from psychopy import visual, event, core
from psykit import StereoWindow, OffscreenWindow
import numpy as np
import time

use_buffer = True # Try setting it to `False` and see what happens without using the offscreen window

# Open a stereo window
win = StereoWindow(monitor='testMonitor', units='deg', fullscr=False, 
    stereoMode='left/right', color='gray')
win.recordFrameIntervals = True
# Create an offscreen window for drawing
buffer = OffscreenWindow(win)
gabor = visual.GratingStim(win, tex='sin', mask='gauss', size=[5,5], sf=1)
X, Y = np.meshgrid(np.linspace(-5,5,3), np.linspace(-5,5,3))
t = win.flip()
def draw_many_stims(gabor, t):
    gabor.phase = 3*t
    for x, y, ori in zip(X.flat, Y.flat, range(0, 360, 40)):
        gabor.pos = [x, y]
        gabor.ori = ori
        gabor.draw()
drawing_times = []
while True:
    t0 = time.time()
    if use_buffer: # Draw many stimuli to the buffer once and use the result twice
        # Draw stimuli to the offscreen window
        buffer.bind() # Bind the offscreen window's framebuffer to redirect drawing
        draw_many_stims(gabor, t)
        buffer.unbind() # Explicit unbinding is actually not necessary in this case
        # Draw left eye stimuli
        win.setBuffer('left')
        buffer.draw() # Draw the content of the offscreen window as a texture
        # Draw right eye stimuli
        win.setBuffer('right')
        buffer.draw()
    else: # Draw many stimuli twice, which will take some extra time and may cause more frame drops
        # Draw left eye stimuli
        win.setBuffer('left')
        draw_many_stims(gabor, t) # Draw many stimuli once
        # Draw right eye stimuli
        win.setBuffer('right')
        draw_many_stims(gabor, t) # Draw many stimuli again
    drawing_times.append(time.time() - t0)
    # Flip
    t = win.flip()
    if 'escape' in event.getKeys():
        break
# Print mean frame interval
x = win.frameIntervals
m = np.mean(x)
print(f"mean interval: {m*1000:.3f} ms, dropped: {sum(x>1.5*np.median(x))}/{len(x)}, drawing time: {np.median(drawing_times)*1000:.3f} ms")
# Clean up
win.close()
core.quit()

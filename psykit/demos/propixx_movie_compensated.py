#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Example script for play a movie in dichoptic mode with cross-talk compensation
# using ProPixx polarizer.
# It is also a good starting point for fMRI block design experiments.
# The movie will be played in the left eye for 24 s, then in the right eye for
# 24 s, repeated for 6 times in each run. In the next run (e.g., run_idx = 1), 
# it will seek to appropriate position in the movie where the previous run ended.
# The script will automatically switch to 'double-height' mode if the height of
# the display is greater than the width.
# Press `a` to switch between 'native' and 'filled' aspect ratio.
# Press `up`/`down` to increase/decrease cross-talk compensation for both eyes.
# Press `r`/`f` to increase/decrease cross-talk compensation for the left eyes.
# Press `u`/`j` to increase/decrease cross-talk compensation for the right eyes.
# Press `escape` to quit.
import numpy as np
from psychopy import visual, event, core
from psykit import StereoWindow, set_polarizer_mode, reset_propixx
from pypixxlib.propixx import PROPixx

use_propixx = False
TR = 2 # s
run_idx = 0

# Open a stereo window
core.rush(True, realtime=True)
win = StereoWindow(monitor='testMonitor', units='deg', fullscr=True, allowGUI=False, 
    stereoMode='red/blue-anticross', crossTalk=[0,0], color=-0.8, screen=1)
win_size = win.size / win.contentScaleFactor # 2 for Retina, 1 for Windows
win.recordFrameIntervals = True
# Set up ProPixx
if use_propixx:
    # Create ProPixx device
    pixx = PROPixx()
    reset_propixx(pixx)
    # Set polarizer mode
    if win.size[1] > win.size[0]: # Double-height EDID
        modes = ['double-height']
        mode_idx = 0
    else:
        modes = ['left/right', 'RB3D']
        mode_idx = 1
    set_polarizer_mode(win, pixx, modes[mode_idx])
# Experiment parameters
delta = 0.005 # Cross-talk compensation step size
# Timing
if run_idx % 2 == 0: 
    block_seq = [] + ['L', 'R']*6 + ['N']
else:
    block_seq = [] + ['R', 'L']*6 + ['N']
block_dur = dict(N=np.ceil(24/TR)*TR, L=np.ceil(24/TR)*TR, R=np.ceil(24/TR)*TR)
block_pts = np.cumsum([block_dur[block] for block in block_seq])
block_idx = -1
run_dur = block_pts[-1]
# Define stimuli
movie = visual.MovieStim3(win, filename='my-favorite-movie.mkv', units='pix')
movie.seek(run_dur * run_idx)
native_size = movie.size
# Don't left any black space on the screen
if native_size[0]/native_size[1] > win_size[0]/win_size[1]: # Movie is wider than screen
    filled_size = [win_size[1]*native_size[0]/native_size[1], win_size[1]]
else: # Movie is taller than screen
    filled_size = [win_size[0], win_size[0]*native_size[1]/native_size[0]]
aspect = 'filled'
movie.size = filled_size

# Frame loop
t0 = win.flip()
t = 0
while True:
    if t == 0 or t >= block_pts[block_idx]:
        block_idx += 1
        if block_idx >= len(block_seq):
            break
        block = block_seq[block_idx]
        print(f"Block {block_idx} @ {t:.3f} s: {block}")
    # Draw left eye stimuli
    win.setBuffer('left')
    if block == 'L':
        movie.draw()
    # Draw right eye stimuli
    win.setBuffer('right')
    if block == 'R':
        movie.draw()
    # Flip
    t = win.flip() - t0
    # Check keyboard events
    pressedKeys = event.getKeys()
    if 'escape' in pressedKeys:
        break
    elif 'a' in pressedKeys: # Switch aspect ratio
        if aspect == 'native':
            aspect = 'filled'
            movie.size = filled_size
        else:
            aspect = 'native'
            movie.size = native_size
    elif 'up' in pressedKeys: # Increase cross-talk compensation for both eyes
        win.crossTalk = win.crossTalk + delta
        print(win.crossTalk)
    elif 'down' in pressedKeys: # Decrease cross-talk compensation for both eyes
        win.crossTalk = win.crossTalk - delta
        print(win.crossTalk)
    elif 'r' in pressedKeys: # Increase left eye cross-talk compensation
        win.crossTalk = win.crossTalk + [delta, 0]
        print(win.crossTalk)
    elif 'f' in pressedKeys: # Decrease left eye cross-talk compensation
        win.crossTalk = win.crossTalk - [delta, 0]
        print(win.crossTalk)
    elif 'u' in pressedKeys: # Increase right eye cross-talk compensation
        win.crossTalk = win.crossTalk + [0, delta]
        print(win.crossTalk)
    elif 'j' in pressedKeys: # Decrease right eye cross-talk compensation
        win.crossTalk = win.crossTalk - [0, delta]
        print(win.crossTalk)    

# Restore ProPixx to default settings
if use_propixx:
    reset_propixx(pixx)
    pixx.close()
# Clean up
win.close()
core.rush(False)
core.quit()
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Example script for play a movie (with sound) in dichoptic mode 
# with cross-talk compensation using ProPixx polarizer.
# It is also a good starting point for fMRI block design experiments.
# The movie will be played in the left eye for 24 s, then in the right eye for
# 24 s, repeated for 6 times in each run. In the next run (e.g., run_idx = 1), 
# it will seek to appropriate position in the movie where the previous run ended.
# The script will automatically switch to 'double-height' mode if the height of
# the display is greater than the width.
# Press `a` to switch between 'native', 'filled', and 'full' aspect ratio.
# Press `t` to toggle whether to draw test pattern or play movie.
# Press `r` to toggle whether to apply cross-talk compensation.
# Press `e` to show a particular eye.
# Press `left`/`right` to switch test pattern.
# Press `up`/`down` to increase/decrease cross-talk compensation for both eyes.
# Press `g`/`b` to increase/decrease cross-talk compensation for the left eyes.
# Press `h`/`n` to increase/decrease cross-talk compensation for the right eyes.
# Press `s`/`x`, `d`/`c`, `f`/`v` to increase/decrease cross-talk compensation for the left eye R,G,B channels.
# Press `j`/`m`, `k`/`comma`,`l`/`period` to increase/decrease cross-talk compensation for the right eye R,G,B channels.
# Press `escape` to quit.
import numpy as np
from psychopy import visual, event, core
from psykit import StereoWindow, set_polarizer_mode, reset_propixx
from pypixxlib.propixx import PROPixx

use_propixx = False
TR = 2 # s
run_idx = 0
if use_propixx:
    # glasses-03,bg=-0.8: [[0.01, 0.025, 0.05], [0.045, 0.055, 0.085]]
    bg_color = -0.8 # For ProPixx linear gamma
    cross_talk = [[0.01, 0.025, 0.05], [0.045, 0.055, 0.085]] # For ProPixx polarizer glasses
else:
    bg_color = -0.5
    cross_talk = [0.02,0.02]

# Open a stereo window
core.rush(True, realtime=True)
win = StereoWindow(monitor='testMonitor', units='deg', fullscr=True, allowGUI=False, 
    stereoMode='red/blue-anticross', crossTalk=cross_talk, screen=1)
win_size = win.size / win.contentScaleFactor # 2 for Retina, 1 for Windows
if win_size[1] > win_size[0]: # For ProPixx double-height EDID
    win_size[1] /= 2
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
    # Sometimes, we may want to swap the left and right eyes
    if modes[mode_idx] == 'double-height':
        win.stereoMode = 'bottom/top-anticross'
    elif modes[mode_idx] == 'RB3D':
        win.stereoMode = 'blue/red-anticross'
# Experiment parameters
delta = 0.005 # Cross-talk compensation step size
show_test_pattern = False
apply_compensation = True
show_eye = 'block'
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
movie = visual.MovieStim(win, filename='my-favorite-movie.mkv', units='pix')
movie.seek(run_dur * run_idx)
native_size = movie.videoSize # May not be correctly read in some cases
# aspect = 'filled': don't left any black space on the screen
# aspect = 'full': don't crop anything
if native_size[0]/native_size[1] > win_size[0]/win_size[1]: # Movie is wider than screen
    filled_size = [win_size[1]*native_size[0]/native_size[1], win_size[1]]
    full_size = [win_size[0], win_size[0]*native_size[1]/native_size[0]]
else: # Movie is taller than screen
    filled_size = [win_size[0], win_size[0]*native_size[1]/native_size[0]]
    full_size = [win_size[1]*native_size[0]/native_size[1], win_size[1]]
aspect = 'filled'
movie.size = filled_size
print(win.size, win_size, native_size, filled_size, full_size)
rect = visual.rect.Rect(win, units='norm', width=2, height=2, color=bg_color)
im = np.concatenate([np.ones([300,100,3])*[1,-1,-1], np.ones([300,100,3])*[-1,1,-1], np.ones([300,100,3])*[-1,-1,1]], axis=1)
im2 = np.concatenate([np.ones([300,100,3])*[-1,1,1], np.ones([300,100,3])*[1,-1,1], np.ones([300,100,3])*[1,1,-1]], axis=1)
test_patterns = [
    visual.ImageStim(win, image=im, units='deg', size=[10,10]), 
    visual.ImageStim(win, image=im2, units='deg', size=[10,10]), 
]
tp_idx = 0

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
    rect.draw()
    if show_eye == 'L' or (show_eye == 'block' and block == 'L'):
        if show_test_pattern:
            test_patterns[tp_idx].draw()
        else:
            movie.draw()       
    # Draw right eye stimuli
    win.setBuffer('right')
    rect.draw()
    if show_eye == 'R' or (show_eye == 'block' and block == 'R'):
        if show_test_pattern:
            test_patterns[tp_idx].draw()
        else:
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
        elif aspect == 'filled':
            aspect = 'full'
            movie.size = full_size
        else:
            aspect = 'native'
            movie.size = native_size
    elif 't' in pressedKeys: # Toggle whether to draw test pattern or play movie
        show_test_pattern = not show_test_pattern
    elif 'r' in pressedKeys: # Toggle whether to apply cross-talk compensation
        apply_compensation = not apply_compensation
        if apply_compensation:
            win.crossTalk = cross_talk
        else:
            cross_talk = win.crossTalk.copy() # Save value, not reference
            win.crossTalk = [0,0]
    elif 'e' in pressedKeys: # Show a particular eye
        if show_eye == 'block':
            show_eye = 'L'
        elif show_eye == 'L':
            show_eye = 'R'
        elif show_eye == 'R':
            show_eye = 'block'
    elif 'right' in pressedKeys: # Switch test pattern
        tp_idx = (tp_idx + 1) % len(test_patterns)
    elif 'left' in pressedKeys:
        tp_idx = (tp_idx - 1) % len(test_patterns)
    elif 'up' in pressedKeys: # Increase cross-talk compensation for both eyes
        win.crossTalk = win.crossTalk + delta
        print(win.crossTalk)
    elif 'down' in pressedKeys: # Decrease cross-talk compensation for both eyes
        win.crossTalk = win.crossTalk - delta
        print(win.crossTalk)
    elif 'g' in pressedKeys: # Increase left eye cross-talk compensation
        win.crossTalk = win.crossTalk + np.r_[delta, 0].reshape(-1,1)
        print(win.crossTalk)
    elif 'b' in pressedKeys: # Decrease left eye cross-talk compensation
        win.crossTalk = win.crossTalk - np.r_[delta, 0].reshape(-1,1)
        print(win.crossTalk)
    elif 'h' in pressedKeys: # Increase right eye cross-talk compensation
        win.crossTalk = win.crossTalk + np.r_[0, delta].reshape(-1,1)
        print(win.crossTalk)
    elif 'n' in pressedKeys: # Decrease right eye cross-talk compensation
        win.crossTalk = win.crossTalk - np.r_[0, delta].reshape(-1,1)
        print(win.crossTalk)
    elif 's' in pressedKeys: # Increase left eye R cross-talk compensation
        win.crossTalk = win.crossTalk + [[delta,0,0], [0,0,0]]
        print(win.crossTalk)
    elif 'x' in pressedKeys: # Decrease left eye R cross-talk compensation
        win.crossTalk = win.crossTalk - [[delta,0,0], [0,0,0]]
        print(win.crossTalk)
    elif 'd' in pressedKeys: # Increase left eye G cross-talk compensation
        win.crossTalk = win.crossTalk + [[0,delta,0], [0,0,0]]
        print(win.crossTalk)
    elif 'c' in pressedKeys: # Decrease left eye G cross-talk compensation
        win.crossTalk = win.crossTalk - [[0,delta,0], [0,0,0]]
        print(win.crossTalk)
    elif 'f' in pressedKeys: # Increase left eye B cross-talk compensation
        win.crossTalk = win.crossTalk + [[0,0,delta], [0,0,0]]
        print(win.crossTalk)
    elif 'v' in pressedKeys: # Decrease left eye B cross-talk compensation
        win.crossTalk = win.crossTalk - [[0,0,delta], [0,0,0]]
        print(win.crossTalk)
    elif 'j' in pressedKeys: # Increase right eye R cross-talk compensation
        win.crossTalk = win.crossTalk + [[0,0,0], [delta,0,0]]
        print(win.crossTalk)
    elif 'm' in pressedKeys: # Decrease right eye R cross-talk compensation
        win.crossTalk = win.crossTalk - [[0,0,0], [delta,0,0]]
        print(win.crossTalk)
    elif 'k' in pressedKeys: # Increase right eye G cross-talk compensation
        win.crossTalk = win.crossTalk + [[0,0,0], [0,delta,0]]
        print(win.crossTalk)
    elif 'comma' in pressedKeys: # Decrease right eye G cross-talk compensation
        win.crossTalk = win.crossTalk - [[0,0,0], [0,delta,0]]
        print(win.crossTalk)
    elif 'l' in pressedKeys: # Increase right eye B cross-talk compensation
        win.crossTalk = win.crossTalk + [[0,0,0], [0,0,delta]]
        print(win.crossTalk)
    elif 'period' in pressedKeys: # Decrease right eye B cross-talk compensation
        win.crossTalk = win.crossTalk - [[0,0,0], [0,0,delta]]
        print(win.crossTalk)

# Restore ProPixx to default settings
if use_propixx:
    reset_propixx(pixx)
    pixx.close()
# Clean up
win.close()
core.rush(False)
core.quit()
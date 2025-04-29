#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Example script that allows you to switch between different stereo modes.
# Press `space` (or `left`/`right`) to iterate through different stereo modes.
# Press `up`/`down` to increase/decrease cross-talk compensation for both eyes.
# Press `r`/`f` to increase/decrease cross-talk compensation for the left eyes.
# Press `u`/`j` to increase/decrease cross-talk compensation for the right eyes.
# Press `escape` to quit.
from psychopy import visual, event, core
import sys, os.path as path
sys.path.insert(0, path.realpath(f"{path.dirname(__file__)}/../.."))
from psykit.stereomode import StereoWindow

# Open a stereo window
# win = StereoWindow(monitor='testMonitor', units='deg', fullscr=False, 
#     stereoMode='quad-buffered', color='gray')
win = StereoWindow(monitor='testMonitor', units='deg', fullscr=True, 
    stereoMode='left/right', crossTalk=[0.07,0.07], color='gray')
print(f"size = {win.size}, color = {win.color}")
# Stereo modes
modes = ['none', 'sequential', 'left/right', 'right/left', 'side-by-side-compressed', 
    'top/bottom', 'bottom/top', 'top/bottom-anticross', 'bottom/top-anticross', 
    'red/green', 'green/red', 'red/blue', 'blue/red',
    'red/green-anticross', 'green/red-anticross', 'red/blue-anticross', 'blue/red-anticross']
mode_idx = modes.index(win.stereoMode)
# Define stimuli
gabor = visual.GratingStim(win, tex='sin', mask='gauss', size=[5,5], sf=1)
label = visual.TextStim(win, text=modes[mode_idx], pos=[0,5], height=1, 
    color='black', autoDraw=True)
# Frame loop
t = win.flip()
paused = False
while True:
    # Draw left eye stimuli
    win.setBuffer('left')
    if not paused:
        gabor.phase = 3*t
    gabor.pos = [0,0]
    gabor.draw()
    gabor.pos = [-3,-3]
    gabor.draw()
    # Draw right eye stimuli
    win.setBuffer('right')
    if not paused:
        gabor.phase = 2*t
    gabor.pos = [0,0]
    gabor.draw()
    gabor.pos = [3,-3]
    gabor.draw()
    # Flip
    t = win.flip()
    pressedKeys = event.getKeys()
    if 'escape' in pressedKeys:
        break
    elif 'space' in pressedKeys or 'right' in pressedKeys:
        mode_idx = (mode_idx + 1) % len(modes)
        win.stereoMode = modes[mode_idx]
        label.text = modes[mode_idx]
    elif 'left' in pressedKeys:
        mode_idx = (mode_idx - 1) % len(modes)
        win.stereoMode = modes[mode_idx]
        label.text = modes[mode_idx]
    elif 'up' in pressedKeys:
        win.crossTalk = win.crossTalk + 0.01
        print(win.crossTalk)
    elif 'down' in pressedKeys:
        win.crossTalk = win.crossTalk - 0.01
        print(win.crossTalk)
    elif 'r' in pressedKeys:
        win.crossTalk = win.crossTalk + [0.01, 0]
        print(win.crossTalk)
    elif 'f' in pressedKeys:
        win.crossTalk = win.crossTalk - [0.01, 0]
        print(win.crossTalk)
    elif 'u' in pressedKeys:
        win.crossTalk = win.crossTalk + [0, 0.01]
        print(win.crossTalk)
    elif 'j' in pressedKeys:
        win.crossTalk = win.crossTalk - [0, 0.01]
        print(win.crossTalk)    
    elif 'p' in pressedKeys:
        paused = not paused
# Clean up
win.close()
core.quit()
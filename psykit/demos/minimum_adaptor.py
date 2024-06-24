#!/usr/bin/env python
# -*- coding: utf-8 -*-
# A minimum example for using StereoWindow adapted from Window (e.g., for Builder).
from psychopy import visual, event, core
from psykit.stereomode import StereoWindow

# Open an ordinary window (e.g., from the Builder)
win = visual.Window(monitor='testMonitor', units='deg', fullscr=False, color='gray')
# Adapt it into a stereo window
# win = StereoWindow(win, stereoMode='quad-buffered')
win = StereoWindow(win, stereoMode='top/bottom-anticross', crossTalk=[0.07,0.07])
gabor = visual.GratingStim(win, tex='sin', mask='gauss', size=[5,5], sf=1)
t = win.flip()
while True:
    # Draw left eye stimuli
    win.setBuffer('left')
    gabor.phase = 3*t
    gabor.draw()
    # Draw right eye stimuli
    win.setBuffer('right')
    gabor.phase = 2*t
    gabor.draw()
    # Flip
    t = win.flip()
    if 'escape' in event.getKeys():
        break
win.close()
core.quit()
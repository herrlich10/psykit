#!/usr/bin/env python
# -*- coding: utf-8 -*-
# A minimum example for using StereoWindow.
from psychopy import visual, event, core
from psykit.stereomode import StereoWindow

# Open a stereo window
win = StereoWindow(monitor='testMonitor', units='deg', fullscr=False, 
    stereoMode='top/bottom-anticross', crossTalk=[0.07,0.07], color='gray')
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
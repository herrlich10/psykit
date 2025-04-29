#!/usr/bin/env python
# -*- coding: utf-8 -*-
# A minimum example for using 'dual-head' mode of StereoWindow.
# Press `escape` to quit.
from psychopy import visual, event, core
from psykit import StereoWindow
from matplotlib import pyplot as plt

# Open a stereo window
win = StereoWindow(monitor='testMonitor', units='deg', fullscr=False, color='gray', 
    stereoMode='dual-head', screen=0, screen2=1)
win.recordFrameIntervals = True
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
plt.plot(win.frameIntervals)
plt.show()
core.quit()
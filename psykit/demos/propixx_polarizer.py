#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Example script for different ways of rendering 3D display using ProPixx with
# the DepthQ polariser and StereoWindow.
# The script will automatically switch to 'double-height' mode if the height of
# the display is greater than the width.
# Press `space` (or 'left'/'right') to iterate through different stereo modes.
# Press `up`/`down` to increase/decrease cross-talk compensation for both eyes.
# (only for 'RB3D' and 'double-height' modes)
# Press `escape` to quit.
import numpy as np
from psychopy import visual, event, core
import sys, os.path as path
sys.path.insert(0, path.realpath(f"{path.dirname(__file__)}/../.."))
from psykit.stereomode import StereoWindow
from pypixxlib.propixx import PROPixx
from pypixxlib import _libdpx


def reset_propixx(pixx):
    # Image orientation
    pixx.setRearProjectionMode(True) # Set the projector to read-projection mode (instant)
    pixx.setCeilingMountMode(False) # Set the projector to non-ceiling-mount mode (instant)
    # Video mode (color)
    pixx.setVideoMode('C24') # Set color 24-bit video mode (video color translation mode: C24|L48|M16|C48, cached)
    pixx.restoreLinearCLUT() # Set linear color lookup table
    # DLP sequencer (timing)
    pixx.setDlpSequencerProgram('RGB') # Set DLP sequencer program (RGB|RB3D|RGB240|QUAD4X|QUAD12X, instant)
    # 3D VESA port (polariser or shutter glasses)
    pixx.setVideoVesaBlueline(False) # Disable polariser switching (VESA port) synchronized by blue lines (cached)
    pixx.setVesaFreeRun(False) # Disable polariser switching (VESA port) in free run (non-sync) mode (cached)
    pixx.updateRegisterCache() # Update the new modes to the device (apply cached changes)
    # pixx.setCustomStartupConfig() # The projector will remember this configuration.
    
def set_polariser_mode(win, pixx, mode):
    if mode == 'none':
        win.stereoMode = 'sequential'
        pixx.setDlpSequencerProgram('RGB')
        pixx.setVideoVesaBlueline(False)
        pixx.setVesaFreeRun(False)
        pixx.updateRegisterCache()
    elif mode == 'RB3D':
        # Pros
        # - Robust to frame drops
        # - Allow binocuar 120 Hz frame rate
        # Cons
        # - Can only display achromatic stimuli (do not support color stimuli)
        win.stereoMode = 'red/blue-anticross'
        pixx.setDlpSequencerProgram('RB3D')
        pixx.setVideoVesaBlueline(False)
        pixx.setVesaFreeRun(False)
        pixx.updateRegisterCache()
    elif mode == 'blueline':
        # https://docs.vpixx.com/python/a-simple-hello-world-in-stereo
        # Pros
        # - Support color stimuli
        # Cons
        # - This mode is susceptible to frame drops
        # - Only support binocuar 60 Hz frame rate
        win.stereoMode = 'sequential'
        pixx.setDlpSequencerProgram('RGB')
        pixx.setVideoVesaBlueline(True)
        pixx.setVesaFreeRun(False) # This will auto set VidVesaWaveform=PPX_DEPTHQ and VidVesaPhase=0
        pixx.updateRegisterCache()
    elif mode == 'freerun':
        # This is not really useable.
        # The image in the two eyes will random swap from time to time due to 
        # slow drift or frame drops.
        win.stereoMode = 'sequential'
        pixx.setDlpSequencerProgram('RGB')
        pixx.setVideoVesaBlueline(False)
        pixx.setVesaFreeRun(True)
        pixx.updateRegisterCache()
    elif mode == 'double-height':
        # This is the recommended mode for most purposes.
        # Use VPutil to adjust EDID to double-height mode [1920x2160 @ 60 Hz].
        # You may need to adjust your screen resolution (dobule-height) to use this mode.
        # Pros
        # - Robust to frame drops
        # - Support color stimuli
        # Cons
        # - Only support binocuar 60 Hz frame rate
        win.stereoMode = 'top/bottom-anticross'
        pixx.setDlpSequencerProgram('RGB')
        pixx.setVideoVesaBlueline(False)
        pixx.setVesaFreeRun(False)
        pixx.updateRegisterCache()
        
# Create ProPixx device
pixx = PROPixx()
reset_propixx(pixx)
# This is a must for blue line sync mode
# However with StereoWindow, the 'blueline' mode may not work well 
# on some machines even at the highest priority... 
# Check out propixx_polarizer_simple.py which may work better.
core.rush(True, realtime=True)
# Open a stereo window
win = StereoWindow(monitor='testMonitor', units='deg', fullscr=True, allowGUI=False, 
    stereoMode='none', crossTalk=[0,0], color='gray', screen=1)
print(f"size = {win.size}, color = {win.color}, type={win.winType}")
win.recordFrameIntervals = True
# Stereo modes
if win.size[1] > win.size[0]: # Double-height EDID
    modes = ['double-height']
    mode_idx = 0
else:
    modes = ['none', 
        'RB3D', 
        'blueline',
        'freerun',
    ]
    mode_idx = 2
set_polariser_mode(win, pixx, modes[mode_idx])
# Define stimuli
gabor = visual.GratingStim(win, tex='sin', mask='gauss', size=[5,5], sf=1)
label = visual.TextStim(win, text=modes[mode_idx], pos=[0,5], height=1, 
    color='black', autoDraw=True)
rect = visual.rect.Rect(win, units='norm', width=2, height=2)
# Frame loop
t = win.flip()
count = 0
paused = False
while count < np.inf:
    count += 1
    # Draw left eye stimuli
    win.setBuffer('left')
    if modes[mode_idx] != 'RB3D':
        rect.color = [1,0,0]
        rect.draw()
    if not paused:
        gabor.phase = 3*t
    gabor.pos = [0,0]
    gabor.draw()
    gabor.pos = [-3,-3]
    gabor.draw()
    # Draw right eye stimuli
    win.setBuffer('right')
    if modes[mode_idx] != 'RB3D':
        rect.color = [0,1,0]
        rect.draw()
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
        set_polariser_mode(win, pixx, modes[mode_idx])
        label.text = modes[mode_idx]
    elif 'left' in pressedKeys:
        mode_idx = (mode_idx - 1) % len(modes)
        set_polariser_mode(win, pixx, modes[mode_idx])
        label.text = modes[mode_idx]
    elif 'up' in pressedKeys:
        win.crossTalk = win.crossTalk + 0.01
        print(win.crossTalk)
    elif 'down' in pressedKeys:
        win.crossTalk = win.crossTalk - 0.01
        print(win.crossTalk)
    elif 'p' in pressedKeys:
        paused = not paused
# Restore ProPixx to default settings
reset_propixx(pixx)
pixx.close()
# Clean up
win.close()
core.rush(False)

import matplotlib.pyplot as plt
x = win.frameIntervals
m = np.mean(x)
print(f"mean interval: {m*1000:.3f} ms, dropped: {sum(x>1.5*m)}/{len(x)}")
plt.plot(x)
if any(x>1.5*m):
    plt.axhline(1.5*m, color='C3', ls='--')
plt.show()

core.quit()
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Example script that draws many different viausl stimuli in StereoWindow.
# Press `space` (or 'left'/'right') to iterate through different stereo modes.
# Press `return` (or 'up'/'down') to iterate through different visual stimuli.
# Press `escape` to quit.
import numpy as np
from PIL import Image
from psychopy import visual, event, core
import sys, os.path as path
sys.path.insert(0, path.realpath(f"{path.dirname(__file__)}/../.."))
from psykit.stereomode import StereoWindow



# Open a stereo window
# win = StereoWindow(monitor='testMonitor', units='deg', fullscr=False, 
#     stereoMode='quad-buffered', color='gray')
win = StereoWindow(monitor='testMonitor', units='deg', fullscr=False, 
    stereoMode='left/right', crossTalk=[0.07,0.07], color='gray', allowStencil=True)
print(f"size = {win.size}, color = {win.color}")
# Stereo modes
modes = ['none', 'sequential', 'left/right', 'right/left', 'side-by-side-compressed', 
    'top/bottom', 'bottom/top', 'top/bottom-anticross', 'bottom/top-anticross', 
    'red/green', 'green/red', 'red/blue', 'blue/red',
    'red/green-anticross', 'green/red-anticross', 'red/blue-anticross', 'blue/red-anticross']
mode_idx = modes.index(win.stereoMode)
# Define stimuli
gabor = visual.GratingStim(win, tex='sin', mask='gauss', size=[5,5], sf=1)
image = visual.ImageStim(win, image='qtywscy.jpg', mask='gauss', size=[5,5*465/367])
rect = visual.rect.Rect(win, width=5, height=5, color='black')
image2 = visual.SimpleImageStim(win, image='jgscy.png', pos=[-1,0])
dots = visual.DotStim(win, nDots=100, dotSize=5, fieldSize=[5,5], fieldShape='circle', 
    dir=0, coherence=0.5, dotLife=20, speed=2/60) # dotLife is important; speed in units/frame
n = 6
x, y = np.meshgrid(*[(np.arange(n)-(n-1)/2)*2]*2)
phases0 = np.linspace(0,1,n**2)
elements = visual.ElementArrayStim(win, nElements=n**2, elementTex='sin', elementMask='gauss', 
    sizes=3, xys=np.c_[x.flat, y.flat], sfs=1, phases=phases0, 
    oris=np.linspace(0,360,n**2), contrs=np.linspace(0,1,n**2))
gabor2 = visual.GratingStim(win, tex='sin', mask='gauss', size=[5,5], sf=0.5, ori=-30)
aperture = visual.Aperture(win, size=5, shape='triangle')
for buffer in ['left', 'right']:
    win.setBuffer(buffer)
    aperture._reset() # Draw to the stencil buffer of each FBO (and hold it there)
aperture.enabled = False
stims = [gabor, image, rect, image2, dots, elements, gabor2]
try:
    radial = visual.RadialStim(win, tex='sqrXsqr', size=[5,5])
    stims.append(radial)
    has_radial = True
except (AttributeError, TypeError):
    has_radial = False
try:
    noise = visual.NoiseStim(win, mask='circle', size=[5,5], noiseType='filtered')
    stims.append(noise)
    has_noise = True
except (AttributeError, TypeError):
    print('You need to install psychopy-visionscience in the plugin manager.')
    has_noise = False
stim_idx = 0
label = visual.TextStim(win, text=modes[mode_idx], pos=[0,5], height=1, 
    color='black', autoDraw=True)
# Frame loop
t = win.flip()
while True:
    # Draw left eye stimuli
    win.setBuffer('left')
    gabor.phase = 3*t
    rect.ori = 180*t
    elements.phases = 3*t + phases0
    gabor2.phase = 2*t
    if has_radial:
        radial.contrast = np.sign(np.sin(2*np.pi*4*t))
    if has_noise:
        noise.buildNoise()
    aperture.enabled = (stims[stim_idx]==gabor2)
    stims[stim_idx].draw()
    # Draw right eye stimuli
    win.setBuffer('right')
    gabor.phase = 2*t
    rect.ori = 90*t
    gabor2.phase = 2*t + 0.1
    stims[stim_idx].draw()
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
    elif 'return' in pressedKeys or 'down' in pressedKeys:
        stim_idx = (stim_idx + 1) % len(stims)
    elif 'up' in pressedKeys:
        stim_idx = (stim_idx - 1) % len(stims)
# Clean up
win.close()
core.quit()
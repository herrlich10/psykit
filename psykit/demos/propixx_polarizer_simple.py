#!/usr/bin/env python
# -*- coding: utf-8 -*-
# A simplest possible script for realizing blueline sync 3D display using ProPixx 
# with the DepthQ polariser. Note we are not using StereoWindow in this example
# in order to simplify the drawing procedure and minimize frame drops.
# Press `escape` to quit.
import numpy as np
from psychopy import visual, event, core
from pypixxlib.propixx import PROPixx


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


def main(with_propixx=False):        
    # Create ProPixx device
    if with_propixx:
        pixx = PROPixx()
        reset_propixx(pixx)
    # This is a must for blue line sync mode
    core.rush(True, realtime=True) 
    # Open an ordinary window (rather than a StereoWindow)
    win = visual.Window(monitor='testMonitor', units='deg', fullscr=True, allowGUI=False, 
        color='gray', waitBlanking=True, screen=1)
    print(f"size = {win.size}, color = {win.color}, type={win.winType}")
    win.recordFrameIntervals = True
    # Hide the cursor
    win.mouseVisible = False # win.setMouseVisible(False)
    # Stereo modes
    if with_propixx:
        pixx.setVideoVesaBlueline(True)
        pixx.updateRegisterCache()
    # Define stimuli
    gabor = visual.GratingStim(win, tex='sin', mask='gauss', size=[5,5], sf=1)
    blueLine = visual.Rect(win, size=[2,2], units='norm', lineColor=[0,0,255], 
        fillColor=None, colorSpace='rgb255', lineWidth=3)
    blackLine = visual.Rect(win, size=[2,2], units='norm', lineColor=[0,0,0], 
        fillColor=None, colorSpace='rgb255', lineWidth=3)
    # Frame loop
    t = win.flip()
    count = 0
    paused = False
    while count < 2500:
        count += 1
        # Draw left eye stimuli and then flip
        if not paused:
            gabor.phase = 3*t
        gabor.pos = [0,0]
        gabor.draw()
        gabor.pos = [-3,-3]
        gabor.draw()
        blueLine.draw()
        t = win.flip()
        # Draw right eye stimuli and then flip
        if not paused:
            gabor.phase = 2*t
        gabor.pos = [0,0]
        gabor.draw()
        gabor.pos = [3,-3]
        gabor.draw()
        blackLine.draw()
        t = win.flip()
        pressedKeys = event.getKeys()
        if 'escape' in pressedKeys:
            break
        elif 'p' in pressedKeys:
            paused = not paused
    # Restore ProPixx to default settings
    if with_propixx:
        reset_propixx(pixx)
        pixx.close()
    # Show the cursor again before closing
    win.mouseVisible = True # win.setMouseVisible(True) 
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


if __name__ == '__main__':
    main(True)
#    import cProfile
#    cProfile.run("main(True)", sort='tottime')
Introduction
============

This package extends the capacity of the Psychopy package for generating stimuli
for psychophysical experiments.

- The `stereomode` module provides the `StereoWindow` class, a drop-in upgrade for 
`psychopy.visual.Window`, which supports a wide variaty of stereo modes including 
'left/right' (for prisms and mirrors), 'side-by-side-compressed' (for VR goggles), 
'red/green' (for anaglyph glasses), 'sequential' (for blue line sync shutters), 
or 'top/down' (for ProPixx projector), just like the `stereomode` in Psychtoolbox.

- The `gltools` provides an alternative and lightweight wrapper (compared to
`psychopy.tools.gltools`) around modern OpenGL commands, e.g., shader, VAO, FBO, 
etc., used by `stereomode`.

- The `demos` folder contains many example scripts demonstrating how to use 
`psykit.stereomode.StereoWindow` with `psychopy`, as well as ProPixx projector.


Documentation
=============

You may find the following demo stripts useful:
- demos/stereo_modes.py
- demos/visual_stims.py
- demos/adjust_fixation.py
- demos/propixx_polarizer.py


Installation
============

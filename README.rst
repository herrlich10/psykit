Introduction
============

The ``psykit`` package extends the capacity of the PsychoPy package in 
generating stereoscopic stimuli and more.

- PsychoPy comes with a limited support for stereoscopic display out-of-the-box. 
  The ``psykit.stereomode`` module provides the ``StereoWindow`` class, a drop-in 
  upgrade for ``psychopy.visual.Window``, which supports a wide variety of 
  stereo modes similar to Psychtoolbox in Matlab, including

  - 'left/right' (for prisms and mirrors)
  - 'side-by-side-compressed' (for VR goggles)
  - 'red/blue' (for anaglyph glasses)
  - 'sequential' (for blue line sync shutter glasses)
  - 'top/bottom' (for ProPixx projector double-height mode)
  - 'top/bottom-anticross' (same as above but with cross-talk compensation)

  Users can debug in one stereo mode and do experiment in another, without 
  needing to modify their code. Most modes can even be switched back and forth 
  at runtime.

- The ``psykit.gltools`` module provides an alternative and lightweight wrapper 
  (compared to ``psychopy.tools.gltools``) around modern OpenGL commands, e.g., 
  shader, VAO, FBO, etc., used by ``psykit.stereomode``.

- The ``psykit/demos`` folder contains many example scripts demonstrating how to 
  use ``psykit.stereomode.StereoWindow`` with ``psychopy``, as well as various
  3D modes of the ProPixx projector.


Documentation
=============

The basic usage is intuitive:

.. code-block:: python

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


You may also find the following demo stripts useful:

- demos/stereo_modes.py
- demos/visual_stims.py
- demos/adjust_fixation.py
- demos/propixx_polarizer.py


Installation
============

If you installed PsychoPy via the standalone installer, download and unzip the 
``psykit`` source code and copy the package folder into the applicaton folder:

- For macOS: "/Applications/PsychoPy.app/Contents/Resources/lib/python3.8/psykit"
- For Windows: "C:\\Program Files\\PsychoPy\\Lib\\site-packages\\psykit"

Otherwise, simply use ``pip install``:

.. code-block:: shell
    
    pip install psykit
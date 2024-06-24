Introduction
============

The ``psykit`` package extends the capacity of the PsychoPy_ package in 
generating stereoscopic stimuli and more.

- PsychoPy is a great tool for quickly creating psychophysical experiments. 
  However, it has limited support for stereoscopic displays out-of-the-box. 
  The ``psykit.stereomode`` module provides the ``StereoWindow`` class, a drop-in 
  upgrade for ``psychopy.visual.Window``, which supports a wide variety of 
  `stereo modes`_ similar to Psychtoolbox in Matlab, including

  - 'left/right' (for prisms and mirrors)
  - 'side-by-side-compressed' (for some VR goggles)
  - 'red/blue' (for anaglyph glasses)
  - 'sequential' (for blue line sync shutters)
  - 'top/bottom' (for the double-height mode of `ProPixx projector`_)
  - 'top/bottom-anticross' (same as above but with `cross-talk compensation`_)

  Users can debug in one stereo mode and do experiment in another, without 
  needing to modify their code. Most modes can even be switched back and forth 
  `at runtime`_.

- The ``psykit.gltools`` module provides an alternative and lightweight wrapper 
  (compared to ``psychopy.tools.gltools``) around modern OpenGL commands, e.g., 
  shader, VAO, FBO, etc., used by ``psykit.stereomode``.

- The ``psykit/demos`` folder contains many example scripts demonstrating how to 
  use ``psykit.stereomode.StereoWindow`` with ``psychopy``, as well as various
  3D modes of the ProPixx projector.

.. _PsychoPy: https://github.com/psychopy/psychopy
.. _stereo modes: https://github.com/herrlich10/psykit/blob/master/psykit/stereomode.py#L33
.. _ProPixx projector: https://github.com/herrlich10/psykit/blob/master/psykit/demos/propixx_polarizer.py
.. _cross-talk compensation: https://github.com/herrlich10/psykit/blob/master/psykit/demos/stereo_modes.py
.. _at runtime: https://github.com/herrlich10/psykit/blob/master/psykit/demos/stereo_modes.py


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


For Builder users, it is easy to adapt an ordinary Window into a StereoWindow:

.. code-block:: python

    # Open an ordinary window (e.g., from the Builder)
    win = visual.Window(monitor='testMonitor', units='deg', fullscr=False, color='gray')
    # Adapt it into a stereo window
    win = StereoWindow(win, stereoMode='top/bottom-anticross', crossTalk=[0.07,0.07])


You may also find the following demo stripts useful:

- demos/stereo_modes.py       # Switch between modes at runtime and adjust cross-talk compensation
- demos/visual_stims.py       # Draw various stimuli (e.g., Aperture) in StereoWindow
- demos/adjust_fixation.py    # Adjust vergence and coordinate origin for 'left/right' mode
- demos/propixx_polarizer.py  # Work with different 3D modes of ProPixx projector


Installation
============

The most convenient way to install ``psykit`` is via the "Plugin/packages manager"
of Psychopy GUI interface. After opening the "Plugins & Packages" dialog, go to 
the "Packages" tab, click "Open PIP terminal", execute "pip install psykit".
If you want to upgrade an existing installation, execute "pip install -U psykit".

If you installed PsychoPy via the standalone installer, it is also possible to 
download and unzip the ``psykit`` source code and copy the package folder into 
the applicaton folder:

- For macOS: "/Applications/PsychoPy.app/Contents/Resources/lib/python3.8/psykit"
- For Windows: "C:\\Program Files\\PsychoPy\\Lib\\site-packages\\psykit"

Otherwise, simply use ``pip install``:

.. code-block:: shell
    
    pip install psykit
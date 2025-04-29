Introduction
============

The ``psykit`` package extends the capacity of the PsychoPy_ package in 
generating stereoscopic stimuli, using offscreen windows, and more.

- PsychoPy is a great tool for quickly creating psychophysical experiments. 
  However, it has limited support for stereoscopic displays out-of-the-box. 
  The ``psykit.stereomode`` module provides the ``StereoWindow`` class, a drop-in 
  upgrade for ``psychopy.visual.Window``, which supports a wide variety of 
  `stereo modes`_ similar to Psychtoolbox in Matlab, including

  - 'left/right' (for prisms and mirrors)
  - 'side-by-side-compressed' (for some VR goggles)
  - 'dual-head' (for some VR goggles with `two video inputs`_)
  - 'red/blue' (for anaglyph glasses)
  - 'sequential' (for blue line sync shutters)
  - 'top/bottom' (for the double-height mode of `ProPixx projector`_)
  - 'top/bottom-anticross' (same as above but with `cross-talk compensation`_)

  Users can debug in one stereo mode and do experiment in another, without 
  needing to modify their code. Most modes can even be switched back and forth 
  `at runtime`_.

- Sometimes, we need to dynamically render a complex scene and reuse it for 
  multiple times, e.g., drawing a dynamic and complex background for both left-
  and right-eye buffers. The ``psychopy.visual.BufferImageStim`` is not suitable
  in this case because it is fast to draw but slower to init. The 
  ``psykit.offscreen`` module provides the ``OffscreenWindow`` class, essentially 
  a framebuffer designed for drawing various stimuli efficiently. These can then 
  be rendered collectively at high speed. Unlike ``BufferImageStim``, 
  ``OffscreenWindow`` is fast to draw and fast to init, and may significantly 
  `reduce rendering time`_ and the risk of frame drops in the above use case.

- PsychoPy users who come from Psychtoolbox sometimes miss the flexibility of the
  ``Screen('DrawTexture')`` style `low-level API`_, e.g., for drawing only part of 
  a texture. The ``psykit`` package implements some of these low-level functions
  like ``psykit.create_texture`` and ``psykit.draw_texture`` for special use cases.
  See `this example`_ for an interesting demo.

- The ``psykit.gltools`` module provides an alternative and lightweight wrapper 
  (compared to ``psychopy.tools.gltools``) around modern OpenGL commands, e.g., 
  shader, VAO, FBO, etc., which are used by other modules.

- The ``psykit.pupillabs`` module provides utilities to work with pupil-labs 
  eye-trackers like the Neon.

- The ``psykit/demos`` folder contains many example scripts demonstrating our 
  favorite use cases, e.g., how to use ``psykit.stereomode.StereoWindow`` with 
  ``psychopy``, as well as various 3D modes of the ProPixx projector.

.. _PsychoPy: https://github.com/psychopy/psychopy
.. _stereo modes: https://github.com/herrlich10/psykit/blob/master/psykit/stereomode.py#L33
.. _two video inputs: https://github.com/herrlich10/psykit/blob/master/psykit/demos/dualhead_mode.py
.. _ProPixx projector: https://github.com/herrlich10/psykit/blob/master/psykit/demos/propixx_polarizer.py
.. _cross-talk compensation: https://github.com/herrlich10/psykit/blob/master/psykit/demos/stereo_modes.py
.. _at runtime: https://github.com/herrlich10/psykit/blob/master/psykit/demos/stereo_modes.py
.. _reduce rendering time: https://github.com/herrlich10/psykit/blob/master/psykit/demos/offscreen_window.py
.. _low-level API: https://github.com/herrlich10/psykit/blob/master/psykit/demos/draw_texture.py
.. _this example: https://github.com/herrlich10/psykit/blob/master/psykit/demos/draw_texture.py


Documentation
=============

The basic usage is intuitive:

.. code-block:: python

    from psychopy import visual, event, core
    from psykit import StereoWindow # from psykit.stereomode import StereoWindow

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


To use an OffscreenWindow as a drawing buffer to cache and reuse intermediate
drawing results:

.. code-block:: python

    from psykit import OffscreenWindow # from psykit.offscreen import OffscreenWindow

    buffer = OffscreenWindow(win) # Create an offscreen window
    buffer.bind() # Bind the offscreen window's framebuffer to redirect drawings
    draw_many_stims()
    buffer.unbind() # After unbinding, subsequent drawings go back to default screen
    # Draw left eye stimuli
    win.setBuffer('left')
    buffer.draw() # Draw the content of the offscreen window as a texture
    # Draw right eye stimuli
    win.setBuffer('right')
    buffer.draw() # Draw again and save some time


You may also find the following demo stripts useful:

- demos/minimum_example.py    # A minimum quickstart script that uses StereoWindow
- demos/stereo_modes.py       # Switch between modes at runtime and adjust cross-talk compensation
- demos/dualhead_mode.py      # Use 'dual-head' mode to draw two eye's views in two physical screens
- demos/visual_stims.py       # Draw various stimuli (e.g., Aperture) in StereoWindow
- demos/adjust_fixation.py    # Adjust vergence and coordinate origin for 'left/right' mode
- demos/propixx_polarizer.py  # Work with different 3D modes of ProPixx projector
- demos/offscreen_window.py   # Use OffscreenWindow to cache and reuse complex stimuli
- demos/draw_texture.py       # Use draw_texture to only draw a selected part of a texture


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
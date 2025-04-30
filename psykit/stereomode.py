#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 2024-05-13: created by qcc
import platform
import numpy as np
from psychopy import visual, layout
import pyglet.gl as GL
from . import gltools

sys_platform = platform.system()


class StereoWindow(visual.Window):
    def __init__(self, win=None, stereoMode='left/right', crossTalk=None, 
                 flipCallback=None, **kwargs):
        '''
        A subclass of `psychopy.visual.Window` that supports many common 
        stereo modes, similar to Psychtoolbox in Matlab.

        Users can debug in one mode and do experiment in another, without the 
        need to change their code.
        Note that 'quad-buffered' and 'dual-head' modes can only be specified 
        during window initialization. Once set, it cannot be changed. 
        Other modes can be freely switched back and forth at any time.

        You can switch between left- and right-eye scenes for drawing operations 
        using `setBuffer()` method.

        See `demos/visual_stims.py` for basic usage.

        Parameters
        ----------
        win : `psychopy.visual.Window` instance (optional)
            If provided, adapt the existing Window into a StereoWindow. Mainly 
            for using with the Builder.
            By default (win=None), initialize a new StereoWindow from scratch.
        stereoMode : str
            - 'none': non-stereo mono display
            - 'quad-buffered': quad-buffers rendering if your graphics card 
                supports. This is the same as using a `psychopy.visual.Window`
                with `stereo=True`.
            - 'dual-head' (for goggles require two video inputs, e.g. the 
                Resonance CinemaVision CV2020 MRI-compatible goggles): 
                Display two eye's images in two separate windows opened in (possibly) 
                two physical screens, specified by `screen` (default 0) and 
                `screen2` (default 1).
                You just need to setBuffer in turn and flip once as usual. No 
                need to explicitly interact with the 2nd window during drawing.
            - 'sequential' (for shutter glasses and some goggles, e.g., NNL goggles): 
                Temporally interleaved mode (odd and even frames).
                StereoWindow will automatically generate blue sync lines at the 
                top and bottom of the display (left eye = blue, right eye = black).
                You can also register a callback function, which is called 
                immediately after the `flip` for the corresponding eye returns, 
                for sending sync signal to the goggles or shutter glasses, using 
                the `flipCallback` property with the signature of `func(eye)`.
            - 'left/right', 'right/left' (for prisms or mirrors): 
                Display two eye's image side-by-side and in normal aspect ratio, 
                often used together with prisms or mirrors, and for free fusion 
                or cross fusion. 
                No cross-talk, but may have binocular alignment or fusion issues.
                You can adjust the following window properties for better fusion:
                - `fixationVergence`: reduce or increase the distance between 
                    the two eyes' image. This is most useful to facilitate fusion.
                - `fixationTilt`: move one eye's image upward and the other 
                    downward (but without rotating the images).
                - `fixationOffset`: move both eyes' image horizontally or 
                    vertically in the same direction. This is useful for displaying
                    stimuli in the MRI scanner with limited FOV through the coil.
                'left/right': lefteye=left side, righteye=right side (free fusion)
                'right/left': lefteye=right side, righteye=left side (cross fusion)
                See `demos/adjust_fixation.py` for basic usage.
            - 'side-by-side-compressed' (for many VR goggles, e.g., Goovis goggles): 
                Display two eye's image side-by-side, with images horizontally 
                compressed/squeezed by 2. 
                Many head-mounted displays (HMD) for VR require this mode.
            - 'top/bottom', 'bottom/top' (e.g., for ProPixx double-height EDID):
                Stack two eye's image vertically and in normal aspect ratio,
                useful with ProPixx double-height image mode.

                | Mode          | Binocular <br>frame rate | Support <br>color image | Robust to <br>frame drops |
                | ------------- | ------------------------ | ----------------------- | ------------------------- |
                | RB3D          | 120 Hz                   | No                      | Yes                       |
                | Blueline sync | 60 Hz                    | Yes                     | No                        |
                | Double-height | 60 Hz                    | Yes                     | Yes                       |
            
                You can switch to ProPixx double-height image mode as follows:
                VPutil > devsel ppc > 2 > edid > 18 > 18 > n > reboot the bluebox
                To switch back to ordinary mode:
                VPutil > devsel ppc > 2 > edid > 0 > n > reboot the bluebox
            - 'top/bottom-anticross', 'bottom/top-anticross' (e.g., for ProPixx 
                double-height EDID with cross-talk compensation):
                Like the above, but trying to reduce cross-talk and compensate 
                for the altered luminance by displaying an attenuated "anti-image" 
                of the other eye. Assume the background of the display is in 
                mid-luminance gray color.
                You can use the `crossTalk` argument or `setCrossTalk()` method
                to adjust the amount of compensation separately for each eye.
                Currently, the RGB channels are assumed to have the same cross-
                talk coefficient. But it is easy to generalize to an anisotropic
                compensation if needed.
            - 'red/green', 'green/red', 'red/blue', 'blue/red' (for red/green 
                glasses): anaglyph modes, still convenient in some fMRI studies.
                Display the two eyes' image in different color channels, used 
                together with anaglyph glasses. 
                May experience cross-talk at high luminance. Consider one of the 
                anti-cross-talk or compensated anaglyph modes below ('*-anticross')
                if you are using a mid-luminance ("gray") background.
            - 'red/green-anticross', 'green/red-anticross', 'red/blue-anticross', 
                'blue/red-anticross' (for red/green glasses with cross-talk): 
                Like the above, but trying to reduce cross-talk and compensate 
                for the altered luminance by displaying an attenuated "anti-image" 
                of the other eye. Assume the background of the display is in 
                mid-luminance ("gray").
                You can use the `crossTalk` argument or `setCrossTalk()` method
                to adjust the amount of compensation separately for each eye.
        crossTalk : array-like of shape (2,)
            [leakage in the LE from the RE, leakage in the RE from the LE]. E.g.,
            [0.1, 0.05] means the left eye can see 10% of the right eye image, 
            while the right eye can see 5% of the left eye image.
        flipCallback : callable of the signature `func(eye)`
            Immediatedly called after the `flip` for corresponding eye returns 
            in 'sequential' mode. Useful for sending sync signal to the goggles 
            or shutter glasses, e.g., the first generation NNL goggles.
        '''
        # Initialize property variables
        self._fixationOffset = np.r_[0.0, 0.0]
        self._fixationVergence = 0.0
        self._fixationTilt = 0.0
        self._crossTalk = np.zeros([2,3])
        # Handle the special case of 'quad-buffered' mode (requiring special backend window)
        if stereoMode == 'quad-buffered':
            self._stereoMode = stereoMode # Without calling the setter
            if win is None: # Create a StereoWindow from scratch
                kwargs.update(dict(stereo=True)) # Ask for a quad-buffer backend
                super().__init__(**kwargs) # Call base class method
            else: # Adapt from an existing psychopy.visual.Window
                self.__dict__.update(win.__dict__)
                if not win.stereo: # This should go after __dict__.update for proper window closing
                    raise ValueError("For 'quad-buffered' mode, we need a Window with stereo=True.")
        else:
            self._stereoMode = None
            if win is None: # Create a StereoWindow from scratch
                # Handle dual-head (two windows) mode
                if stereoMode == 'dual-head':
                    screen2 = kwargs.pop('screen2', 1)
                    kwargs2 = kwargs.copy()
                    kwargs2.update(screen=screen2, waitBlanking=False)
                    self.win2 = visual.Window(**kwargs2)
                super().__init__(**kwargs) # Call base class method
            else: # Adapt from an existing psychopy.visual.Window
                if stereoMode == 'dual-head':
                    raise NotImplementedError
                self.__dict__.update(win.__dict__)

            # Prepare framebuffers for binocular rendering
            # Create left eye and right eye framebuffers 
            # (for 'sequential' and anaglyph stereo modes)
            self._fboLE, self._texLE = gltools.create_framebuffer(self.size)
            self._fboRE, self._texRE = gltools.create_framebuffer(self.size)
            for buffer in [self._fboLE, self._fboRE, 0]:
                # Initialize FBO color to window background color
                # Without this, the default color is blue if flip before setBuffer
                GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, buffer)
                self.clearBuffer()
            
            # Compile shader programs for different stereo modes
            self._stereoShaders = {}
            for mode in ['red/green', 'green/red', 'red/blue', 'blue/red',
                'red/green-anticross', 'green/red-anticross', 'red/blue-anticross', 'blue/red-anticross']:
                # Compile and link shader programs for anaglyph modes
                program = gltools.compile_shader_program(
                    vertTexture_src, fragAnaglyph_src[mode])
                # Set uniform values, associating sampler2D with correspondent texture unit
                gltools.use_texture(self._texLE, 0, program, b"textureLE")
                gltools.use_texture(self._texRE, 1, program, b"textureRE")
                self._stereoShaders[mode] = program
            # Shader program for 'sequential' and 'side-by-side-compressed' modes
            program = gltools.compile_shader_program(
                vertTexture_src, fragTexture_src)
            gltools.use_texture(self._texLE, 0, program, b"aTex")
            for mode in ['sequential', 'side-by-side-compressed', 'dual-head']:
                self._stereoShaders[mode] = program
            # Shader program for 'left/right' and 'right/left' modes
            program = gltools.compile_shader_program(
                vertCentralX_src, fragTexture_src)
            gltools.use_texture(self._texLE, 0, program, b"aTex")
            for mode in ['left/right', 'right/left']:
                self._stereoShaders[mode] = program
            # Shader program for 'top/bottom' and 'bottom/top' modes
            program = gltools.compile_shader_program(
                vertCentralY_src, fragTexture_src)
            gltools.use_texture(self._texLE, 0, program, b"aTex")
            for mode in ['top/bottom', 'bottom/top']:
                self._stereoShaders[mode] = program
            # Shader program for 'top/bottom-anticross' and 'bottom/top-anticross' modes
            program = gltools.compile_shader_program(
                vertCentralY_src, fragCompensated_src)
            # Have to handle texture units and uniforms later at draw time
            for mode in ['top/bottom-anticross', 'bottom/top-anticross']:
                self._stereoShaders[mode] = program
            GL.glUseProgram(0) # Reset shader program
            
            # Create VAO for drawing framebuffers to screen
            vertices = [
                # position      # tex coords
                1, -1, 0.0,    1, 0, # bottom right
                -1, -1, 0.0,    0, 0, # bottom left
                -1,  1, 0.0,    0, 1, # top left 
                1,  1, 0.0,    1, 1, # top right
            ]
            attributes = [
                ('position', 3, False), # (name, size, normalize)
                ('tex_coords', 2, False),
            ]
            indices = [
                0, 1, 2,    # first triangle
                3, 0, 2,    # second triangle
            ]
            self._screenVAO = gltools.create_vertex_array(vertices, attributes, indices)
            
            # Set stereo mode (except for 'quad-buffered' mode)
            # self.stereoMode = stereoMode
            self._stereoMode = stereoMode
            # Set cross-talk factors
            self.crossTalk = crossTalk
            # Set flip callback
            self.flipCallback = flipCallback # `func(eye)`
            
            # Create psychopy.visual.Line for drawing blue sync lines in 'sequential' mode
            # Note that layout.Vector will always return nominal pixel value, 
            # which is what we need for drawing, while win.size will return 
            # doubled pixel size for Retina display.
            # It seems that pixels are actually labeled as [-1.5, -0.5, 0.5, 1.5].
            # For a [800,600] window, the top line must be drawn at 299.5, not 300.abs
            # However, this behavior is platform dependent.
            if sys_platform == 'Darwin': # For macOS
                # macOS has a different interpretation of the pixel coordinates
                posfix = {'top': np.r_[0,0.5], 'bottom': np.r_[0,0]}
            else: # For Windows
                posfix = {'top': np.r_[0,0], 'bottom': np.r_[0,0.5]}
            self._blueLines = {}
            for loc, y in zip(['top', 'bottom'], [1, -1]):
                start = layout.Vector([-1,y], 'norm', self).pix - np.sign(y)*posfix[loc]
                end = layout.Vector([1,y], 'norm', self).pix - np.sign(y)*posfix[loc]
#                for eye, color in zip(['left', 'right'], [[255,255,255], [0,0,0]]):
#                    # Blue line in left eye, black line in right eye
#                    self._blueLines[eye,loc] = visual.Line(win=self, units='pix', 
#                        start=start, end=end, colorSpace='rgb255',
#                        interpolate=False, lineWidth=3) # MUST set `interpolate` to False
#                    self._blueLines[eye,loc].color = color # Psychopy bug: Must set here
                # There seem to be bugs in PsychoPy 2025.1.0, so that 'rgb255' won't work
                for eye, color in zip(['left', 'right'], [1, -1]):
                    self._blueLines[eye,loc] = visual.Line(win=self, units='pix', 
                        start=start, end=end, color=color, lineWidth=3,
                        interpolate=False) # MUST set `interpolate` to False


    @property
    def stereoMode(self):
        return self._stereoMode

    @stereoMode.setter
    def stereoMode(self, stereoMode):
        '''
        Set stereo mode of the window.

        Note that 'quad-buffered' mode can only be specified during window 
        initialization. Once set, it cannot be changed. 
        Other modes can be freely switched back and forth at any time.

        Parameters
        ----------
        stereoMode : str
            - 'none'
            - 'quad-buffered'
            - 'dual-head'
            - 'sequential'
            - 'left/right', 'right/left'
            - 'side-by-side-compressed' (e.g., Goovis goggles)
            - 'top/bottom', 'bottom/top'
            - 'top/bottom-anticross', 'bottom/top-anticross'
            - 'red/green', 'green/red', 'red/blue', 'blue/red'
            - 'red/green-anticross', 'green/red-anticross', 'red/blue-anticross', 
              'blue/red-anticross'
        '''
        if stereoMode == 'quad-buffered' or self.stereoMode == 'quad-buffered':
            raise ValueError("'quad-buffered' mode can only be specified during window initialization. Once set, it cannot be changed.")
        elif stereoMode == 'dual-head' or self.stereoMode == 'dual-head':
            raise ValueError("'dual-head' mode can only be specified during window initialization. Once set, it cannot be changed.")
        self._stereoMode = stereoMode


    def setBuffer(self, buffer, clear=True):
        '''
        Choose which buffer to draw to ('left' or 'right').

        Parameters
        ----------
        buffer : str
            Buffer to draw to. Can either be 'left' or 'right'.
        clear : bool, optional
            Clear the buffer before drawing. Default is `True`.
        '''
        if self.stereoMode == 'quad-buffered':
            # Call base class method
            super().setBuffer(buffer, clear=clear)
        elif self.stereoMode == 'none': # Mono display (no stereo)
            # Bind the default framebuffer
            GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)
        else: # For all other stereo modes (which are FBO-based)
            # Redirect drawing to FBO of the corresponding eye
            if buffer == 'left':
                # Bind left eye framebuffer and redirect following drawings there
                GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self._fboLE)
            elif buffer == 'right':
                # Bind right eye framebuffer and redirect following drawings there
                GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self._fboRE)
            else:
                raise ValueError(f"Unknown buffer '{buffer}' requested in StereoWindow.setBuffer")
            # Clear the FBO before subsequent drawings
            if clear:
                # GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT | GL.GL_STENCIL_BUFFER_BIT)
                self.clearBuffer() # Only clear color buffer by default (and keep stencil buffer for visual.Aperture)
            # Enable depth and stencil tests according to Window settings
            if self.depthTest:
                GL.glEnable(GL.GL_DEPTH_TEST)
            if self.stencilTest:
                GL.glEnable(GL.GL_STENCIL_TEST)


    def close(self):
        '''Close the window(s).
        '''
        if self.stereoMode == 'dual-head':
            self.win2.close()
        # Call base class method
        super().close()


    def flip(self, clearBuffer=True):
        '''
        Flip the front and back buffers after drawing everything for your frame. 

        Parameters
        ----------
        clearBuffer : bool, optional
            Clear the draw buffer after flipping. Default is `True`.

        Returns
        -------
        float or None
            Wall-clock time in seconds the flip completed. Returns `None` if
            `self.waitBlanking` is `False`.
        '''
        if self.stereoMode in ['none', 'quad-buffered']:
            # Call base class method
            flipTime = super().flip(clearBuffer=clearBuffer)
        else: # For all other FBO-based stereo modes
            # Execute and replace autoDraw
            backup = self._toDraw
            self._toDraw = []
            self._executeAutoDraw(backup)
            # Blip FBOs
            if self.stereoMode in ['side-by-side-compressed']:
                # Note that glViewport along doesn't work with TextStim and SimpleImageStim
                # So we still need to use FBO for 'left/right' and 'side-by-side-compressed'
                # Render on the left part of the screen
                GL.glViewport(0, 0, self.size[0]//2, self.size[1])
                self._blipEyeBuffer(eye='left')
                # Render on the right part of the screen
                GL.glViewport(self.size[0]//2, 0, self.size[0]//2, self.size[1])
                self._blipEyeBuffer(eye='right')
            elif self.stereoMode in ['left/right', 'right/left']:
                eyes = self.stereoMode.split('/')
                sign = lambda eye: 1 if eye=='left' else -1 # Positive for the LE, and negative for the RE
                # Render on the left part of the screen
                GL.glViewport(int(self._fixationOffset[0] + sign(eyes[0])*self._fixationVergence), 
                    int(self._fixationOffset[1] + sign(eyes[0])*self._fixationTilt), 
                    self.size[0]//2, self.size[1])
                self._blipEyeBuffer(eye=eyes[0])
                # Render on the right part of the screen
                GL.glViewport(int(self.size[0]//2 + self._fixationOffset[0] + sign(eyes[1])*self._fixationVergence), 
                    int(self._fixationOffset[1] + sign(eyes[1])*self._fixationTilt), 
                    self.size[0]//2, self.size[1])
                self._blipEyeBuffer(eye=eyes[1])
            elif self.stereoMode in ['top/bottom', 'bottom/top', 'top/bottom-anticross', 'bottom/top-anticross']:
                eyes = {k: v for k, v in zip(self.stereoMode.split('-')[0].split('/'), ['left', 'right'])}
                # Render on the top part of the screen
                GL.glViewport(0, self.size[1]//2, self.size[0], self.size[1]//2)
                self._blipEyeBuffer(eye=eyes['top'])
                # Render on the bottom part of the screen
                GL.glViewport(0, 0, self.size[0], self.size[1]//2)
                self._blipEyeBuffer(eye=eyes['bottom'])
            elif self.stereoMode in ['red/green', 'green/red', 'red/blue', 'blue/red',
                'red/green-anticross', 'green/red-anticross', 'red/blue-anticross', 'blue/red-anticross']:
                # Combine left eye and right eye framebuffers and draw to screen
                self._blipEyeBuffer(eye='both')
            elif self.stereoMode in ['sequential']:
                # We need to flip twice in 'sequential' mode
                self._blipEyeBuffer(eye='left')
                self._drawBlueLine(eye='left')
                flipTime0 = super().flip(clearBuffer=clearBuffer)
                if self.flipCallback is not None:
                    self.flipCallback(eye='left')
                self._blipEyeBuffer(eye='right')
                self._drawBlueLine(eye='right')
            elif self.stereoMode in ['dual-head']:
                # We need to flip twice in 'dual-head' mode
                self._blipEyeBuffer(eye='left')
                self._drawBlueLine(eye='left')
            # Call base class method
            flipTime = super().flip(clearBuffer=clearBuffer)
            if self.stereoMode in ['sequential'] and self.flipCallback is not None:
                self.flipCallback(eye='right')
            elif self.stereoMode in ['dual-head']:
                if self.flipCallback is not None:
                    self.flipCallback(eye='left')
                # Make the second window's OpenGL context current
                self.win2._setCurrent()
                self._blipEyeBuffer(eye='right')
                self._drawBlueLine(eye='right')
                self.win2.flip(clearBuffer=clearBuffer) # waitBlanking=False, return None
                if self.flipCallback is not None:
                    self.flipCallback(eye='right')
                # Restore the main window's OpenGL context current
                self._setCurrent()
            # Restore autoDraw
            self._toDraw = backup
        # Return flip time
        return flipTime


    def _blipEyeBuffer(self, eye):
        '''
        Draw left eye and/or right eye framebuffers to the screen,
        combining the content from the two buffers if necessary 
        (e.g., in anaglyph modes).

        Parameters
        ----------
        eye : str
            'both' | 'left' | 'right'
        '''
        # Prepare OpenGL context
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0) # Back to default
        GL.glDisable(GL.GL_DEPTH_TEST) # Disable test to ensure every fragment is copied
        GL.glDisable(GL.GL_STENCIL_TEST)
        program = self._stereoShaders[self.stereoMode]
        GL.glUseProgram(program) # Use stereo shader
        gltools.glBindVertexArray(self._screenVAO) # Switch to screen-copy VAO
        if eye == 'both':
            gltools.use_texture(self._texLE, 0) # Bind LE to texture unit 0
            gltools.use_texture(self._texRE, 1) # Bind RE to texture unit 1
        elif eye == 'left':
            if self.stereoMode.endswith('anticross'): 
                # Set texture and crossTalk uniforms every frame for top/bottom-anticross
                gltools.use_texture(self._texLE, 0, program, b"textureThis")
                gltools.use_texture(self._texRE, 1, program, b"textureOther")
                GL.glUniform3f(GL.glGetUniformLocation(program, b"crossTalk"), 
                    self._crossTalk[0,0], self._crossTalk[0,1], self._crossTalk[0,2])
            else:
                gltools.use_texture(self._texLE, 0) # Bind LE to texture unit 0
        elif eye == 'right':
            if self.stereoMode.endswith('anticross'):
                gltools.use_texture(self._texRE, 0, program, b"textureThis")
                gltools.use_texture(self._texLE, 1, program, b"textureOther")
                GL.glUniform3f(GL.glGetUniformLocation(program, b"crossTalk"), 
                    self._crossTalk[1,0], self._crossTalk[1,1], self._crossTalk[1,2])
            else:
                gltools.use_texture(self._texRE, 0) # Bind RE to texture unit 0
        # Draw a rectangle (in fact, two triangles)
        # (primitive, number of vertices to draw, dtype of indices, offset of indices)
        GL.glDrawElements(GL.GL_TRIANGLES, 6, GL.GL_UNSIGNED_INT, 0)
        # Reset VAO and shader program (otherwise it may interfere with e.g., SimpleImageStim)
        gltools.glBindVertexArray(0) # Fixed bug: 2024-05-15 by qcc
        GL.glUseProgram(0) # Without this SimpleImageStim will not work
        # Re enable depth and stencil tests according to Window settings
        if self.depthTest:
            GL.glEnable(GL.GL_DEPTH_TEST)
        if self.stencilTest:
            GL.glEnable(GL.GL_STENCIL_TEST)


    def _executeAutoDraw(self, stimList):
        for stim in stimList:
            for buffer in ['left', 'right']:
                self.setBuffer(buffer, clear=False)
                stim.draw()


    def _drawBlueLine(self, eye, loc='bottom'):
        '''
        Draw blue sync lines for 'sequential' mode.
        
        Parameters
        ----------
        eye : str
            Which eye to draw: 'left' | 'right'
            The usual protocol expects a blue line in the left eye frame, and
            a black line at the same location in the right eye frame.
            See e.g., https://docs.vpixx.com/python/a-simple-hello-world-in-stereo
        loc : str
            Where to draw the line: 'top' | 'bottom' | 'both'
        '''
        if loc in ['top', 'both']:
            self._blueLines[eye,'top'].draw()
        if loc in ['bottom', 'both']:
            self._blueLines[eye,'bottom'].draw()


    @property
    def crossTalk(self):
        return self._crossTalk
    
    @crossTalk.setter
    def crossTalk(self, crossTalk):
        '''
        Set cross-talk factors between the two eyes.
        Only works for cross-talk compensated ('*-anticross') stereo modes.

        The value for each eye is between [0,1].
        The vector value should be set as a whole, e.g., 
        `win.crossTalk = [0.1, 0.05]`, but not `win.crossTalk[0] = 0.1`.

        Parameters
        ----------
        crossTalk : array-like of shape (2,) or (2,3)
            Cross-talk factors (for R/G/B channels) of the two eyes.
            The left eye coefficients represent the leakage of the right eye 
            stimulus into the left eye.
            
            If an array of shape (2,) is given, all channels will be set 
            to the same value. E.g.,
            [0.1, 0.05] means the left eye can see 10% of the right eye image, 
            while the right eye can see 5% of the left eye image.
            
            If an array of shape (2,3) is given, the first row is for the LE,
            and the second row is for the RE. E.g.,
            [[0.02, 0.03, 0.06], [0.0, 0.0, 0.1]] means the left eye can see 
            2% of the red, 3% of the green, and 6% of the blue channel of the 
            right eye image.
        '''
        if crossTalk is None:
            crossTalk = np.zeros([2,3])
        else:
            crossTalk = np.asanyarray(crossTalk)
            if crossTalk.size == 2:
                crossTalk = np.ones([2,3]) * crossTalk.reshape(-1,1)
        self._crossTalk[0] = np.maximum(0.0, np.minimum(1.0, crossTalk[0]))
        self._crossTalk[1] = np.maximum(0.0, np.minimum(1.0, crossTalk[1]))
        for mode in ['red/green-anticross', 'green/red-anticross', 'red/blue-anticross', 'blue/red-anticross']:
            program = self._stereoShaders[mode]
            GL.glUseProgram(program) # Use stereo shader
            GL.glUniform2f(GL.glGetUniformLocation(program, b"crossTalk"), 
                self._crossTalk[0][0], self._crossTalk[1][0])
            GL.glUseProgram(0) # Reset shader
        # Note that the crossTalk uniform is set at draw time for top/bottom-anticross


    @property
    def fixationOffset(self):
        '''
        Get the horizontal and vertical offset of the fixation point in the units 
        of the window (e.g., 'deg') in 'left/right' or 'right/left' stereo modes.
        '''
        v = layout.Vector(self._fixationOffset, 'pix', self)
        return getattr(v, self.units)

    @fixationOffset.setter
    def fixationOffset(self, offset):
        '''
        Set the horizontal and vertical offset of the fixation point in the units 
        of the window (e.g., 'deg') in 'left/right' or 'right/left' stereo modes.

        The vector value should be set as a whole, e.g., 
        `win.fixationOffset = [0,0]`, but not `win.fixationOffset[0] = 0`.

        You may also directly access the underlying value in pixels and in place:
        `win._fixationOffset[0] += 5`, which is sometimes more convenient.

        Parameters
        ----------
        offset : array-like of shape (2,)
            [horizontal, vertical]
        '''
        v = layout.Vector(offset, self.units, self)
        self._fixationOffset = v.pix

    @property
    def fixationVergence(self):
        v = layout.Vector([self._fixationVergence, 0], 'pix', self)
        return getattr(v, self.units)[0]

    @fixationVergence.setter
    def fixationVergence(self, vergence):
        '''
        Set binocular vergence (horizontal inward shift, i.e., to the right for 
        the left eye and to the left for the right eye) in the units of the window 
        (e.g., 'deg') in 'left/right' or 'right/left' stereo modes.

        You may also directly access the underlying value in pixels and in place:
        `win._fixationVergence += 5`, which is sometimes more convenient.

        Parameters
        ----------
        vergence : float
            In the units of the window (e.g., 'deg').
        '''
        v = layout.Vector([vergence, 0], self.units, self)
        self._fixationVergence = v.pix[0]

    @property
    def fixationTilt(self):
        v = layout.Vector([0, self._fixationTilt], 'pix', self)
        return getattr(v, self.units)[1]

    @fixationTilt.setter
    def fixationTilt(self, tilt):
        '''
        Set binocular "tilt" (vertical divergent shift, i.e., upward for the 
        left eye and downward for the right eye) in the units of the window 
        (e.g., 'deg') in 'left/right' or 'right/left' stereo modes.

        You may also directly access the underlying value in pixels and in place:
        `win._fixationTilt += 5`, which is sometimes more convenient.

        Parameters
        ----------
        tilt : float
            In the units of the window (e.g., 'deg').
        '''
        v = layout.Vector([0, tilt], self.units, self)
        self._fixationTilt = v.pix[1]



# Old compatibility profile shaders to draw binocular FBOs to screen
# Vertex shader for drawing the whole texture (for most FBO-based modes)
vertTexture_src = '''
    attribute vec3 aPos;        // Location 0
    attribute vec2 aTexCoords;  // Location 1
    varying vec2 TexCoords;     // out
    void main()
    {
        gl_Position = vec4(aPos.x, aPos.y, 0.0, 1.0); 
        TexCoords = aTexCoords;
    }  
'''

# Vertex shader for drawing the central part of the texture in x direction
# (for 'left/right' and 'right/left' modes)
vertCentralX_src = '''
    attribute vec3 aPos;        // Location 0
    attribute vec2 aTexCoords;  // Location 1
    varying vec2 TexCoords;     // out
    void main()
    {
        gl_Position = vec4(aPos.x, aPos.y, 0.0, 1.0);
        float frac = 0.5;
        TexCoords = vec2((1.0-frac)/2.0+frac*aTexCoords.x, aTexCoords.y);
    }  
'''

# Vertex shader for drawing the central part of the texture in y direction
# (for 'top/bottom' and 'bottom/top' modes)
vertCentralY_src = '''
    attribute vec3 aPos;        // Location 0
    attribute vec2 aTexCoords;  // Location 1
    varying vec2 TexCoords;     // out
    void main()
    {
        gl_Position = vec4(aPos.x, aPos.y, 0.0, 1.0);
        float frac = 0.5;
        TexCoords = vec2(aTexCoords.x, (1.0-frac)/2.0+frac*aTexCoords.y);
    }  
'''

# Fragment shaders for non-anaglyph modes ('sequential', 'left/right', etc.)
fragTexture_src = '''
    varying vec2 TexCoords;     // in
    uniform sampler2D aTex;
    void main()
    {
        gl_FragColor = texture2D(aTex, TexCoords);
    }
'''

# Fragment shaders for non-anaglyph modes with cross-talk compensation
fragCompensated_src = '''
    varying vec2 TexCoords;     // in
    uniform sampler2D textureThis;
    uniform sampler2D textureOther;
    uniform vec3 crossTalk;     // RGB cross talk from the other eye
    void main()
    {
        vec4 colorThis = texture2D(textureThis, TexCoords);
        vec4 colorOther = texture2D(textureOther, TexCoords);
        // gl_FragColor = ((colorThis*2.0-1.0) - vec4(crossTalk, 0)*(colorOther*2.0-1.0) +1.0)/2.0;
        // 2025-03-28: New method
        // gl_FragColor = clamp(colorThis - vec4(crossTalk, 0) * colorOther, 0.0, 1.0);
        gl_FragColor = max(colorThis - vec4(crossTalk, 0) * colorOther, 0.0);
    }
'''

fragAnaglyph_src = {}
# Fragment shaders for anaglyph modes
for mode, cmd in [  ('red/green', 'vec4(colorLE.r, colorRE.g, 0.0, 1.0)'),
                    ('green/red', 'vec4(colorRE.r, colorLE.g, 0.0, 1.0)'),
                    ('red/blue',  'vec4(colorLE.r, 0.0, colorRE.b, 1.0)'),
                    ('blue/red',  'vec4(colorRE.r, 0.0, colorLE.b, 1.0)'),
                 ]:
    fragAnaglyph_src[mode] = f'''
        varying vec2 TexCoords;     // in
        uniform sampler2D textureLE;
        uniform sampler2D textureRE;
        void main()
        {{
            vec4 colorLE = texture2D(textureLE, TexCoords);
            vec4 colorRE = texture2D(textureRE, TexCoords);
            gl_FragColor = {cmd};
        }}
    '''

# Fragment shaders for anaglyph modes with cross-talk compensation
for mode, cmd in [  # ('red/green-anticross', 'vec4(((colorLE.r*2.0-1.0) - crossTalk.x*(colorRE.g*2.0-1.0) +1.0)/2.0, ((colorRE.g*2.0-1.0) - crossTalk.y*(colorLE.r*2.0-1.0) +1.0)/2.0, 0.0, 1.0)'),
                    # ('green/red-anticross', 'vec4(((colorRE.r*2.0-1.0) - crossTalk.y*(colorLE.g*2.0-1.0) +1.0)/2.0, ((colorLE.g*2.0-1.0) - crossTalk.x*(colorRE.r*2.0-1.0) +1.0)/2.0, 0.0, 1.0)'),
                    # ('red/blue-anticross',  'vec4(((colorLE.r*2.0-1.0) - crossTalk.x*(colorRE.b*2.0-1.0) +1.0)/2.0, 0.0, ((colorRE.b*2.0-1.0) - crossTalk.y*(colorLE.r*2.0-1.0) +1.0)/2.0, 1.0)'),
                    # ('blue/red-anticross',  'vec4(((colorRE.r*2.0-1.0) - crossTalk.y*(colorLE.b*2.0-1.0) +1.0)/2.0, 0.0, ((colorLE.b*2.0-1.0) - crossTalk.x*(colorRE.r*2.0-1.0) +1.0)/2.0, 1.0)'),
                    # 2025-03-28: New method
                    ('red/green-anticross', 'vec4(max(colorLE.r - crossTalk.x*colorRE.g, 0.0), max(colorRE.g - crossTalk.y*colorLE.r, 0.0), 0.0, 1.0)'),
                    ('green/red-anticross', 'vec4(max(colorRE.r - crossTalk.y*colorLE.g, 0.0), max(colorLE.g - crossTalk.x*colorRE.r, 0.0), 0.0, 1.0)'),
                    ('red/blue-anticross',  'vec4(max(colorLE.r - crossTalk.x*colorRE.b, 0.0), 0.0, max(colorRE.b - crossTalk.y*colorLE.r, 0.0), 1.0)'),
                    ('blue/red-anticross',  'vec4(max(colorRE.r - crossTalk.y*colorLE.b, 0.0), 0.0, max(colorLE.b - crossTalk.x*colorRE.r, 0.0), 1.0)'),
                 ]:
    fragAnaglyph_src[mode] = f'''
        varying vec2 TexCoords;     // in
        uniform sampler2D textureLE;
        uniform sampler2D textureRE;
        uniform vec2 crossTalk;
        void main()
        {{
            vec4 colorLE = texture2D(textureLE, TexCoords);
            vec4 colorRE = texture2D(textureRE, TexCoords);
            gl_FragColor = {cmd};
        }}
    '''


if __name__ == '__main__':
    # Example script (StereoDemo)
    # Press `space` to iterate through different stereo modes.
    # Press `escape` to quit.
    from psychopy import visual, event, core

    # Open a stereo window
    # win = StereoWindow(monitor='testMonitor', units='deg', fullscr=False, 
    #     stereoMode='quad-buffered', color='gray')
    win = StereoWindow(monitor='testMonitor', units='deg', fullscr=False, 
        stereoMode='left/right', crossTalk=[0.07,0.07], color='gray')
    print(f"size = {win.size}, color = {win.color}")
    # Stereo modes
    modes = ['none', 'sequential', 'left/right', 'right/left', 'side-by-side-compressed', 
        'top/bottom', 'bottom/top', 'top/bottom-anticross', 'bottom/top-anticross', 
        'red/green', 'green/red', 'red/blue', 'blue/red',
        'red/green-anticross', 'green/red-anticross', 'red/blue-anticross', 'blue/red-anticross']
    mode_idx = modes.index(win.stereoMode)
    # Define stimuli
    gabor = visual.GratingStim(win, tex='sin', mask='gauss', size=[5,5], sf=1)
    label = visual.TextStim(win, text=modes[mode_idx], pos=[0,5], height=1, 
        color='black', autoDraw=True)
    # Frame loop
    t = win.flip()
    paused = False
    while True:
        # Draw left eye stimuli
        win.setBuffer('left')
        if not paused:
            gabor.phase = 3*t
        gabor.pos = [0,0]
        gabor.draw()
        gabor.pos = [-3,-3]
        gabor.draw()
        # Draw right eye stimuli
        win.setBuffer('right')
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
        elif 'space' in pressedKeys:
            mode_idx = (mode_idx + 1) % len(modes)
            win.stereoMode = modes[mode_idx]
            label.text = modes[mode_idx]
        elif 'p' in pressedKeys:
            paused = not paused
    # Clean up
    win.close()
    core.quit()
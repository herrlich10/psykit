#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pyglet.gl as GL
from . import gltools
import numpy as np


class OffscreenWindow(object):
    def __init__(self, win):
        '''
        Create an offscreen window, which is just a framebuffer.
        
        You can draw any stimulus to the offscreen window efficiently, as if you
        are drawing to an ordinary (onscreen) Window. You can then draw its 
        content as a texture to the onscreen Window efficiently.
        This is unlike the ``psychopy.visual.BufferImageStim`` which is fast to 
        draw but slower to init.
        Essentially, you can create a complex texture incrementally and 
        dynamically in memory, and reuse it many times.

        Parameters
        ----------
        win : `psychopy.visual.Window` instance
            The Window object in which the stimulus will be rendered by default.
        '''
        self.win = win
        self._fbo, self._tex = gltools.create_framebuffer(self.win.size)

    def bind(self, clear=True):
        '''
        Bind the offscreen window so that all following drawings are redirected here.

        The API is designed to be memoryless because binding another offscreen
        window will automatically and implicitly unbind current offscreen window.

        Parameters
        ----------
        clear : bool
            Clear the offscreen window after binding, using the background color
            of the associated onscreen Window. Default is `True`.
        '''
        # Bind the offscreen framebuffer and redirect following drawings there
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self._fbo)
        if clear:
            self.win.clearBuffer()
    
    def unbind(self):
        '''
        Explicitly unbind this offscreen window so that all following drawings 
        will happen in the back buffer of the default onscreen Window.
        '''
        # Bind the default onscreen buffer
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)

    def draw(self):
        '''
        Draw the content of the offscreen window as a texture to the associated
        onscreen Window.
        '''
        draw_texture(self.win, self._tex)


def draw_texture(win, tex, src_rect=None, dst_rect=None, rotation=0, alpha=1,
                 program=None, tex_unit=0):
    '''
    A general purpose drawing function like `Screen('DrawTexture')` in Psychtoolbox.

    You can efficiently draw part of a texture to the specified location of the 
    Window with dynamic scaling and rotation, and even provide your own shader 
    program (both vertex and fragment shaders) for texture postprocessing.

    Parameters
    ----------
    win : `psychopy.visual.Window` instance
        The Window object in which the stimulus will be rendered by default.
        Currently, this is not really used, and the texture will simply be drawn
        to the default onscreen Window or any currently bound framebuffer.
        In other words, multiple-onscreen-windows mode is not currently supported.
    tex : texture id (uint as returned by ``gltools.create_texture`` or 
        ``gltools.create_framebuffer``)
        The 2D texture to draw.
    src_rect : [left,bottom, right,top] in OpenGL texture coordinates from 0 to 1.
        Specify the rect on the texture to draw. 
        The lower left corner is [0,0] and the upper right corner is [1,1].
    dst_rect : [left,bottom, right,top] in OpenGL normalized device coordinates 
        from -1 to 1.
        Specify the rect on the screen to draw the texture into (before rotation).
        The lower left corner is [-1,-1] and the upper right corner is [1,1].
    rotation : float
        Rotate the texture by the specified degrees CCW.
    alpha : float
        Global alpha, which is multiplied to the per pixel alpha of the texture.
        0 for fully transparent, and 1 for opaque.
    program : shader program (as returned by ``gltools.compile_shader_program``)
        Compiled shader program for drawing and postprocessing the texture.
    tex_unit : int
        Texture units (`GL_TEXTURE0` to `GL_TEXTURE15`) allow us to bind more 
        than one texture at the same time and sample from multiple textures in 
        the fragment shader.
    '''
    # Create our VAO on-the-fly
    if src_rect is None:
        src_rect = [0,0, 1,1] # [left,bottom, right,top] in OpenGL texture coordinates from 0 to 1
    if dst_rect is None:
        dst_rect = [-1,-1, 1,1] # [left,bottom, right,top] in OpenGL normalized device coordinates from -1 to 1
    vertices = [
        # position                        # tex coords
        dst_rect[2], dst_rect[1], 0.0,    src_rect[2], src_rect[1], # bottom right
        dst_rect[0], dst_rect[1], 0.0,    src_rect[0], src_rect[1], # bottom left
        dst_rect[0], dst_rect[3], 0.0,    src_rect[0], src_rect[3], # top left 
        dst_rect[2], dst_rect[3], 0.0,    src_rect[2], src_rect[3], # top right
    ]
    attributes = [
        ('position', 3, False), # (name, size, normalize)
        ('tex_coords', 2, False),
    ]
    indices = [
        0, 1, 2,    # first triangle
        3, 0, 2,    # second triangle
    ]
    vao = gltools.create_vertex_array(vertices, attributes, indices)
    # Prepare OpenGL context
    # GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0) # We don't need this here
    # The drawing destination can be the default Window or currently binded FBO.
    GL.glDisable(GL.GL_DEPTH_TEST) # Disable test to ensure every fragment is copied
    GL.glDisable(GL.GL_STENCIL_TEST)
    # Use our shader program
    if program is None:
        program = _texture_program
    GL.glUseProgram(program)
    GL.glUniform1f(GL.glGetUniformLocation(program, b'globalAlpha'), alpha)
    # Apply allocentric rotation transform inside the vertex shader
    NT = gltools.translation([-(dst_rect[0]+dst_rect[2])/2, -(dst_rect[1]+dst_rect[3])/2, 0])
    T = gltools.translation([(dst_rect[0]+dst_rect[2])/2, (dst_rect[1]+dst_rect[3])/2, 0])
    R = gltools.rotation(rotation/180*np.pi)
    trans = T @ R @ NT 
    gltools.set_uniform(program, b'transform', trans)
    # Bind our VAO
    gltools.glBindVertexArray(vao)
    # Bind our texture and activate the texture unit
    gltools.use_texture(tex, tex_unit)
    # Draw a rectangle (in fact, two triangles)
    # (primitive, number of vertices to draw, dtype of indices, offset of indices)
    # GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)
    GL.glDrawElements(GL.GL_TRIANGLES, 6, GL.GL_UNSIGNED_INT, 0)
    # GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
    # Reset VAO and shader program (otherwise it may interfere with e.g., SimpleImageStim)
    gltools.glBindVertexArray(0)
    GL.glUseProgram(0)
    # Re enable depth and stencil tests according to Window settings
    if win.depthTest:
        GL.glEnable(GL.GL_DEPTH_TEST)
    if win.stencilTest:
        GL.glEnable(GL.GL_STENCIL_TEST)


# Old compatibility profile shaders
# Vertex shader for drawing a texture with in-plane rotation
vertTexture_src = '''
    attribute vec3 aPos;        // Location 0
    attribute vec2 aTexCoords;  // Location 1
    varying vec2 TexCoords;     // out
    uniform mat4 transform;
    void main()
    {
        gl_Position = transform * vec4(aPos.x, aPos.y, 0.0, 1.0); 
        TexCoords = aTexCoords;
    }  
'''

# Fragment shaders for drawing a texture
fragTexture_src = '''
    varying vec2 TexCoords;     // in
    uniform sampler2D aTex;
    uniform float globalAlpha;
    void main()
    {
        gl_FragColor = texture2D(aTex, TexCoords);
        gl_FragColor.w *= globalAlpha; // Modulated by global alpha
    }
'''

_texture_program = gltools.compile_shader_program(vertTexture_src, fragTexture_src)
# # For the single texture case, the following doesn't seem to be needed
# GL.glUseProgram(_texture_program)
# GL.glUniform1i(GL.glGetUniformLocation(_texture_program, b'aTex'), 0)
# GL.glUseProgram(0)
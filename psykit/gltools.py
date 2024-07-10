#!/usr/bin/env python
# -*- coding: utf-8 -*-
# A lightweight alternative to Psychopy.tools.gltools, which is somewhat less 
# intuitive and sometimes may not work out of the box.
# The functions provided here do not try to cover all possible use cases, but
# rather focus on the most fundamental (and somewhat restricted) ones.
# Good for beginners and for learning purpose.
# Inspired by https://learnopengl.com/. Thanks @JoeyDeVries!
# For a more full-fledged and modern wrapper for OpenGL, see e.g., ModernGL.
# 2024-05-10: created by qcc
from pyglet.gl import *
import numpy as np
import ctypes
import platform


# ========== Compatibility issues ==========
if platform.system() == 'Darwin': # A lesson from Psychopy
    glGenVertexArrays = glGenVertexArraysAPPLE
    glBindVertexArray = glBindVertexArrayAPPLE


# ========== ctypes ==========
def str_to_lp_lp_c_char(s, encoding='utf-8'):
    '''
    Cast Python str to C char** (pointer to char* or char[]), i.e., lp_lp_c_char.
    '''
    # Convert the string to a ctypes char pointer
    c_char_p_string = ctypes.c_char_p(s.encode(encoding))
    # Create a pointer to the char* (NUL terminated) and cast it to char**
    lp_lp_c_char = ctypes.cast(ctypes.pointer(c_char_p_string), ctypes.POINTER(ctypes.POINTER(ctypes.c_char)))
    return lp_lp_c_char


# ========== Transformations ==========
def normalize(v):
    '''
    Normalize the vector to get a unit vector.
    '''
    return v / np.linalg.norm(v)


def scaling(sxyz=[1,1,1]):
    '''
    Create a 4x4 3D scaling matrix.
    '''
    sx, sy, sz = sxyz
    return np.array([
        [sx, 0,  0,  0],
        [0,  sy, 0,  0],
        [0,  0,  sz, 0],
        [0,  0,  0,  1],
    ])


def translation(txyz=[0,0,0]):
    '''
    Create a 4x4 3D translation matrix.
    '''
    tx, ty, tz = txyz
    return np.array([
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz],
        [0, 0, 0, 1],
    ])


def rotation(angle=0, axis=[0,0,1]):
    '''
    Create a 4x4 3D rotation matrix that rotate `angle` along `axis`.

    Parameters
    ----------
    angle : float
        Amount of rotation in radian
    axis : array of shape (3,)
    '''
    c, s = np.cos(angle), np.sin(angle)
    u, v, w = axis/np.linalg.norm(axis)
    return np.array([
        [c + u*u*(1-c),    u*v*(1-c) - w*s,  u*w*(1-c) + v*s, 0],
        [v*u*(1-c) + w*s,  c + v*v*(1-c),    v*w*(1-c) - u*s, 0],
        [w*u*(1-c) - v*s,  w*v*(1-c) + u*s,  c + w*w*(1-c),   0],
        [0,                0,                0,               1],
    ])


def perspective(fov, aspect, near=0.1, far=100):
    '''
    Create a perspective projection matrix. 
    The matrix can be used as the projection matrix in OpenGL.
    
    Parameters
    ----------
    fov : float
        Vertical field-of-view in radian. 
        Using a smaller (larger) value has the effect of zoom-in (zoom-out).
        45 degrees is a commonly used value.
    aspect : float
        Aspect ratio = width / height of the viewport (or window).
    near : float
        Distance to the near plane.
    far : float
        Distance to the far plane.
    
    References
    ----------
    https://www.songho.ca/opengl/gl_projectionmatrix.html
    The matrix is transposed in our code to be inline with other matrices here.
    '''
    tangent = np.tan(fov/2.0) # Tangent of half fovY
    top = near * tangent #  Half height of near plane
    right = top * aspect # Half width of near plane
    return np.array([
        [near/right, 0.0, 0.0, 0.0],
        [0.0, near/top, 0.0, 0.0],
        [0.0, 0.0, -(far+near)/(far-near), -(2*far*near)/(far-near)],
        [0.0, 0.0, -1, 0.0],
    ])


def look_at(position, target=[0,0,0], up=[0,1,0]):
    '''
    Create a "look at" matrix for an up-right camera at `position` looking at
    the `target`. The matrix can be used as the view matrix in OpenGL.
    
    References
    ----------
    https://learnopengl.com/Getting-started/Camera
    '''
    position = np.asarray(position)
    camera_z = normalize(position - target) # Camera direction (pointing towards the back of the camera)
    camera_x = normalize(np.cross(up, camera_z)) # Camera right
    camera_y = np.cross(camera_z, camera_x) # Camera up
    rot = np.c_[np.vstack([camera_x, camera_y, camera_z, np.zeros(3)]), [0,0,0,1]]
    trans = np.c_[np.vstack([np.eye(3), np.zeros(3)]), np.r_[-position,1]]
    return rot @ trans


# ========== Shaders ==========
def compile_shader_program(vertex_source, fragment_source):
    '''
    Compile vertex and fragment shaders and link them for later use.

    Parameters
    ----------
    vertex_source : str
        Source code for the vertex shader.
    fragment_source : str
        Source code for the fragment shader.

    Related functions
    -----------------
    Consider using `moderngl.Program` which is more Pythonic and provides code inspection.
    `psychopy.visual.shaders.compileProgram` is similar to what we have here.
    '''
    # Compile vertex shader
    vertexShader = glCreateShader(GL_VERTEX_SHADER)
    # glShaderSource(vertexShader, 1, str_to_lp_lp_c_char(vertex_source), None) # "1" is the number of strings in the char**
    glShaderSource(vertexShader, 1, str_to_lp_lp_c_char(vertex_source), None) # "1" is the number of strings in the char**
    glCompileShader(vertexShader)
    check_shader_status(vertexShader, label='Vertex')
    # Compile fragment shader
    fragmentShader = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fragmentShader, 1, str_to_lp_lp_c_char(fragment_source), None)
    glCompileShader(fragmentShader)
    check_shader_status(fragmentShader, label='Fragment')
    # Link shader program
    shaderProgram = glCreateProgram()
    glAttachShader(shaderProgram, vertexShader)
    glAttachShader(shaderProgram, fragmentShader)
    glLinkProgram(shaderProgram)
    check_shader_status(shaderProgram, stage='link')
    # Delete no longer used shader compilation intermediate objects
    glDeleteShader(vertexShader)
    glDeleteShader(fragmentShader)
    return shaderProgram


def check_shader_status(shader, stage='compile', raise_error=True, 
    max_message_len=512, label=None):
    '''
    Check whether shader compilation or shader program linkage is successful.
    Print the error message if not.

    Parameters
    ----------
    shader : shader object returned by glCreateShader
    stage : str
        - 'compile'
        - 'link'
    '''
    success = GLint()
    if stage == 'compile':
        glGetShaderiv(shader, GL_COMPILE_STATUS, success)
    elif stage == 'link':
        glGetProgramiv(shader, GL_LINK_STATUS, success)
    if not success:
        infoLog = (ctypes.c_char*max_message_len)()
        if stage == 'compile':
            glGetShaderInfoLog(shader, max_message_len, None, infoLog)
            message = f"{'Shader' if label is None else label+' shader'} compilation failed with the following message:\n" + infoLog.value.decode('utf-8')
        elif stage == 'link':
            glGetProgramInfoLog(shader, max_message_len, None, infoLog)
            message = f"Shader program linkage failed with the following message:\n" + infoLog.value.decode('utf-8')
        if raise_error:
            raise ValueError(message)
        else:
            print(message)


# ========== Uniforms ==========
def set_uniform(program, name, value):
    '''
    Set uniform value for shader programs.

    Appropriate OpenGL function will be called according to the type, dtype, and
    shape of the ``value``, e.g., a transformation should be a 4x4 float ndarray.
    Currently, only support 4x4 matrix with float values, e.g., transformations.

    Parameters
    ----------
    program : 
        Shader program for which the uniform value will be set.
    name : bytes
        Name of the uniform variable in the shader.
        e.g., b"transform"
    value : 
        New value for the uniform variable.
    '''
    loc = glGetUniformLocation(program, name)
    if isinstance(value, np.ndarray):
        if value.shape == (4,4):
            if value.dtype.kind == 'f':  
                # (uniform's location, how many matrices to send, transpose (default=GL_FALSE is F order), pointer to matrix values)
                data = (GLfloat*value.size)(*value.flat)
                glUniformMatrix4fv(loc, 1, GL_TRUE, data)


# ========== Vertex buffer object (VBO) ==========
def create_vertex_buffer(vertices, usage=GL_STATIC_DRAW, bind=False):
    '''
    Create a vertex buffer object (VBO) for storing vertex data (e.g., vertex
    coordinates, color, texture coordinates, etc.) on the GPU.

    Parameters
    ----------
    vertices : array of shape (n,k) or (k*n,)
        Each vertex may associate with k float values as its data.
        It is reasonable to assume all vertex data are float, because vertex
        coordinates are usually float, and all data must share one dtype.
    usage : int
        - GL_STREAM_DRAW: the data is set only once and used by the GPU at most a few times.
        - GL_STATIC_DRAW: the data is set only once and used many times.
        - GL_DYNAMIC_DRAW: the data is changed a lot and used many times.
    bind : bool
        Whether to remain binding to GL_ARRAY_BUFFER after creation.
    '''
    # Create a VBO and bind it to GL_ARRAY_BUFFER
    vbo = GLuint()  # Placeholder for the VBO
    glGenBuffers(1, vbo)  # Generate one new VBO
    glBindBuffer(GL_ARRAY_BUFFER, vbo)  # Bind the VBO
    # Copy the vertex data into the VBO
    vertices = np.ravel(vertices)
    vertex_data = (GLfloat*len(vertices))(*vertices)
    glBufferData(GL_ARRAY_BUFFER, ctypes.sizeof(vertex_data), vertex_data, usage)
    # Unbind the VBO
    if not bind:
        glBindBuffer(GL_ARRAY_BUFFER, 0)
    return vbo


def create_element_buffer(indices, usage=GL_STATIC_DRAW, bind=False):
    '''
    Create a element buffer object (EBO) for storing vertex indices on the GPU.
    Index starts from zero.

    Parameters
    ----------
    indices : array of shape (n,3) or (3*n,)
        Each triangle element may associate with 3 vertex indices (unsigned int).
    usage : 
        - GL_STREAM_DRAW: the data is set only once and used by the GPU at most a few times.
        - GL_STATIC_DRAW: the data is set only once and used many times.
        - GL_DYNAMIC_DRAW: the data is changed a lot and used many times.
    bind : bool
        Whether to remain binding to GL_ELEMENT_ARRAY_BUFFER after creation.
    '''
    # Create a EBO and bind it to GL_ELEMENT_ARRAY_BUFFER
    ebo = GLuint()  # Placeholder for the EBO
    glGenBuffers(1, ebo)  # Generate one new EBO
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)  # Bind the EBO
    # Copy the index data into the EBO
    indices = np.ravel(indices)
    assert (indices.dtype.kind == 'i')  # np.issubdtype(dtype, np.integer)
    index_data = (GLuint*len(indices))(*indices)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, ctypes.sizeof(index_data), index_data, usage)
    # Unbind the EBO
    if not bind:
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
    return ebo


# ========== Vertex array object (VAO) ==========
def create_vertex_array(vertices, attributes, indices=None, usage=GL_STATIC_DRAW, 
    indices_usage=None, bind=False):
    '''
    Create a vertex array object (VAO) to store (subsequent) vertex attribute calls 
    for fast switching between different vertex data and attribute configurations
    (e.g., to facilitate drawing multiple different objects).

    Parameters
    ----------
    vertices : array of shape (n,k) or (k*n,)
        Each vertex may associate with k float values as its data.
    attributes : list of (str, int, bool)
        List of attribute description: (name, number of values, need normalization). 
        These information is used to set vertex attributes pointers.
        It is reasonable to assume all vertex attribute values are float, because 
        vertex coordinates are usually float, and all data must share one dtype.
    indices : array of shape (n,3) or (3*n,)
        Each triangle element may associate with 3 vertex indices (unsigned int).
    usage : int
        - GL_STREAM_DRAW: the data is set only once and used by the GPU at most a few times.
        - GL_STATIC_DRAW: the data is set only once and used many times.
        - GL_DYNAMIC_DRAW: the data is changed a lot and used many times.
    bind : bool
        Whether to remain binding to GL_ARRAY_BUFFER after creation.
    '''
    # Create a Vertex Array Object (VAO)
    vao = GLuint() # Placeholder for the VAO
    glGenVertexArrays(1, vao) # Generate one new VAO
    glBindVertexArray(vao) # Bind the VAO
    # Create a VBO and bind it to GL_ARRAY_BUFFER
    create_vertex_buffer(vertices, usage=usage, bind=True)
    # Create a EBO and bind it to GL_ELEMENT_ARRAY_BUFFER
    if indices is not None:
        if indices_usage is None:
            indices_usage = usage
        create_element_buffer(indices, usage=indices_usage, bind=True)
    # Set the vertex attributes pointers
    for k, (attribute, (stride, offset)) in enumerate(zip(attributes, compute_stride_offset(attributes))):
        name, size, need_norm = attribute
        # (attribute index, number of values, dtype, need normalization, stride, offset)
        glVertexAttribPointer(k, size, GL_FLOAT, int(need_norm), 
            stride*ctypes.sizeof(GLfloat), offset*ctypes.sizeof(GLfloat))
        glEnableVertexAttribArray(k)
    # End recording
    # Release GL_ARRAY_BUFFER and GL_ELEMENT_ARRAY_BUFFER after recording is 
    # essential, because they will not be automatically released and may 
    # interfere with other operations causing mysterious crash...
    glBindVertexArray(0)
    glBindBuffer(GL_ARRAY_BUFFER, 0) # Without Shape and SimpleImageStim will not work
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0) # Fixed bug: 2024-05-15 by qcc
    if bind:
        glBindVertexArray(vao) # Bind this VAO
    return vao


def bind_vertex_array(vao):
    '''
    Platform independent wrapper for `glBindVertexArray(vao)`.
    A lesson from psychopy.tools.gltools.createVAO().
    '''
    glBindVertexArray(vao)


def compute_stride_offset(attributes):
    '''
    Compute the stride and offset for each attribute.

    Parameters
    ----------
    attributes : list of (str, int, bool)
        List of attribute description: (name, number of values, need normalization). 

    Returns
    -------
    results : list of (stride, offset)
    '''
    sizes = [attribute[1] for attribute in attributes]
    stride = sum(sizes)
    offsets = np.cumsum(np.r_[0, sizes])[:len(sizes)]
    return [(stride, int(offset)) for offset in offsets]


# ========== Textures ==========
def create_texture(data, size=None, unit=0, warp=GL_REPEAT, 
    min_filter=None, mag_filter=GL_LINEAR, mipmap=True, bind=False):
    '''
    Create a 2D texture.

    Currently, only support RGB and RGBA textures, either uint8 or float32.

    Parameters
    ----------
    data : 3D array of shape (height,width,n_channels)
        If data is None, texture is initialzed as GL_UNSIGNED_BYTE for using as
        the color buffer (texture attachment) of a framebuffer.
    size : [width, height] in pixels
        Will be ignored if `data` is not None.
    unit : int
        Texture units (`GL_TEXTURE0` to `GL_TEXTURE15`) allow us to bind more 
        than one texture at the same time and sample from multiple textures in 
        the fragment shader.
    warp : GL_REPEAT | GL_MIRRORED_REPEAT | GL_CLAMP_TO_EDGE | GL_CLAMP_TO_BORDER
        What happens when sampling outside the texture
    min_filter : GL_LINEAR | GL_NEAREST | GL_LINEAR_MIPMAP_LINEAR | GL_NEAREST_MIPMAP_NEAREST
        Minifying filter. 
        If None, GL_LINEAR_MIPMAP_LINEAR if mipmap=True else GL_LINEAR.
    mag_filter : GL_LINEAR | GL_NEAREST
        Magnifying filter
    mipmap : bool
        Whether to enable mipmap (for efficient and high quality downscaling).
    bind : bool
        Whether to remain binding to GL_TEXTURE_2D after creation.

    Returns
    -------
    texture : ctypes.c_uint
        Texture id
    '''
    # Create a 2D texture at the specified unit
    texture = GLuint() # Placeholder for the texture
    glGenTextures(1, texture) # Create one new texture
    glActiveTexture(eval(f"GL_TEXTURE{unit}")) # Activate specified texture unit
    glBindTexture(GL_TEXTURE_2D, texture) # Bind the texture
    # Set the texture wrapping/filtering options (on the currently bound texture object)
    if min_filter is None:
        min_filter = GL_LINEAR_MIPMAP_LINEAR if mipmap else GL_LINEAR
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, warp)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, warp)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, min_filter)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, mag_filter)
    # Load texture data
    src_fmt = None
    if data is not None:
        data = data[::-1] # flipud: array origin is at upper left but texture is at lower left
        height, width, n_channels = data.shape
        if n_channels == 3:
            src_fmt = GL_RGB
        elif n_channels == 4:
            src_fmt = GL_RGBA
        if data.dtype.kind in ['i', 'u']: # np.issubdtype(dtype, np.integer), assuming 0~255
            src_dtype = GL_UNSIGNED_BYTE
            data = (GLubyte*data.size)(*data.astype(np.uint8).flat)
        elif data.dtype.kind == 'f': # np.issubdtype(dtype, np.floating), assuming 0~1 or -1~1
            assert (data.max() <= 1)
            src_dtype = GL_FLOAT
            data = (GLfloat*data.size)(*data.astype(np.float32).flat)
    else:
        assert (size is not None)
        width, height = size
        src_fmt = GL_RGB
        src_dtype = GL_UNSIGNED_BYTE
    # Relax 4-byte-alignment requirement for RGB ubyte data
    not_aligned = (src_fmt == GL_RGB and src_dtype == GL_UNSIGNED_BYTE)
    if not_aligned:
        alignment = GLint()
        glGetIntegerv(GL_UNPACK_ALIGNMENT, alignment)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1) # Relax alignment
    # (texture target (so that GL_TEXTURE_1D and 3D are unaffected), mipmap level (base level=0), 
    #   texture color format, texture width, texture height, lagacy, 
    #   source color format, source dtype, source data)
    if src_fmt == GL_RGB:
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, src_fmt, src_dtype, data)
    elif src_fmt == GL_RGBA:
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, src_fmt, src_dtype, data)
    else:
        NotImplementedError(f"Only support GL_RGB and GL_RGBA texture at the moment.")
    if not_aligned:
        glPixelStorei(GL_UNPACK_ALIGNMENT, alignment) # Restore alignment
    # Generate mipmap for minifying
    if mipmap:
        glGenerateMipmap(GL_TEXTURE_2D)
    # Unbind the texture
    if not bind:
        glBindTexture(GL_TEXTURE_2D, 0)
    return texture


def use_texture(texture, unit=0, program=None, uniform=None):
    '''
    Use a texture for drawing. 
    We need to bind the texture and activate the texture unit everytime, while 
    set the fragment shader sampler uniform value (to the unit number) once.

    Parameters
    ----------
    texture : ctypes.c_uint
        Texture id.
    unit : int
        Texture unit (can be 0-15).
    program : 
        Shader program for rendering the texture.
    uniform : bytes
        sampler2D uniform variable name in the fragment shader.
        e.g., b"texture1"
    '''
    glActiveTexture(eval(f"GL_TEXTURE{unit}")) # Activate texture unit
    glBindTexture(GL_TEXTURE_2D, texture) # Bind the texture
    if program is not None:
        glUseProgram(program) # Need to use the program before setting its uniform
        glUniform1i(glGetUniformLocation(program, uniform), unit)


# ========== Framebuffer ==========
def create_framebuffer(size, texture_kws=None, bind=False):
    '''
    Create a (completed) framebuffer (FBO) along with its attachments (color, 
    depth, stencil buffers) for offscreen rendering and post-processing.

    Parameters
    ----------
    size : [width, height] in pixels
        Size of the framebuffer. Usually the same as the window size.
    texture_kws : dict
        Additional keyword arguments for creating the texture attachment, e.g., 
        'unit' (texture unit), 'min_filter', 'mipmap'.
    bind : bool
        Whether to remain binding to GL_FRAMEBUFFER after creation.

    Returns
    -------
    framebuffer : ctypes.c_uint
        FBO id. Bind it for offscreen rendering.
    texture : ctypes.c_uint
        Texture id. This can be used as an ordinary texture for drawing.
    '''
    # Create a new framebuffer
    framebuffer = GLuint() # Placeholder for the FBO
    glGenFramebuffers(1, framebuffer) # Create one new FBO
    glBindFramebuffer(GL_FRAMEBUFFER, framebuffer) # Bind the FBO

    # Create a texture attachment as color buffer
    texture_kws = dict(dict(min_filter=GL_LINEAR, mipmap=False), **({} if texture_kws is None else texture_kws))
    texture = create_texture(data=None, size=size, **texture_kws)
    # Attach it to currently bound framebuffer object
    # (FBO target, type of attachment, texture target, the actual texture, mipmap level)
    # As framebuffer is usually sampled point-to-point, we don't need mipmap.
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, int(texture_kws['mipmap']))

    # Create a renderbuffer attachment as depth and stencil buffer
    rbo = create_renderbuffer(size)
    # Attach it to currently bound framebuffer object
    # (FBO target, type of attachment, renderbuffer target, the actual renderbuffer)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, rbo)

    # Check if the framebuffer is complete
    assert (glCheckFramebufferStatus(GL_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE)
    # Unbind the framebuffer
    if not bind:
        glBindFramebuffer(GL_FRAMEBUFFER, 0) # Back to default
    return framebuffer, texture


def create_renderbuffer(size, format=GL_DEPTH24_STENCIL8, bind=False):
    '''
    Create a renderbuffer (RBO), which is usually used as the depth and stencil 
    buffers of a framebuffer, i.e., used as framebuffer attachment.
    Renderbuffers are different from textures in that they are optimized for 
    writing and cannot be sampled from.

    Parameters
    ----------
    size : [width, height] in pixels
    format : GL_DEPTH24_STENCIL8
        Internal format.
    bind : bool
        Whether to remain binding to GL_RENDERBUFFER after creation.
    '''
    # Create a new renderbuffer
    rbo = GLuint() # Placeholder for the RBO
    glGenRenderbuffers(1, rbo) # Create one new RBO
    glBindRenderbuffer(GL_RENDERBUFFER, rbo) # Bind the RBO
    # Create storage for the renderbuffer
    # (renderbuffer binding target, internal format, W, H)
    width, height = size
    glRenderbufferStorage(GL_RENDERBUFFER, format, width, height)
    # Unbind the RBO
    if not bind:
        glBindRenderbuffer(GL_RENDERBUFFER, 0)
    return rbo

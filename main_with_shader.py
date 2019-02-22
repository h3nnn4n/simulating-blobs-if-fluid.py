# -----------------------------------------------------------------------------
# Based on `Python & OpenGL for Scientific Visualization`
# www.labri.fr/perso/nrougier/python+opengl
# Copyright (c) 2017, Nicolas P. Rougier
# Distributed under the 2-Clause BSD License.
# Modified by Renan S Silva (h3nnn4n)
# -----------------------------------------------------------------------------

import random
import sys
import ctypes
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut

from simulating_blobs_of_fluid.simulation import Simulation
import random

particle_count = 200
simulation = Simulation(particle_count=particle_count, dt=0.016, box_width=500)
particle_position = np.zeros((particle_count, 2), np.float32)
program = None
screen_x = 800
screen_y = 800


def read_shader(filename):
    with open(filename, 'rt') as f:
        lines = f.readlines()

    code = ''.join(lines)

    return code


def display():
    simulation.step()

    for k, p in enumerate(simulation.particles):
        particle_position[k, 0] = p.position.x
        particle_position[k, 1] = p.position.y

    particle_position[0, 0] = 0
    particle_position[0, 1] = 0

    loc = gl.glGetUniformLocation(program, "particle_pos")
    gl.glUniform2fv(loc, particle_count, particle_position)

    loc = gl.glGetUniformLocation(program, "resolution")
    gl.glUniform2f(loc, float(screen_x), float(screen_y))

    loc = gl.glGetUniformLocation(program, "particle_bouding_radius")
    gl.glUniform1f(loc, float(simulation.box_radius))

    gl.glClear(gl.GL_COLOR_BUFFER_BIT)
    gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)
    glut.glutSwapBuffers()


def reshape(width, height):
    gl.glViewport(0, 0, width, height)


def keyboard(key, x, y):
    if key == b'\x1b':
        sys.exit()


def main():
    global particle_count
    global particle_position
    # GLUT init
    # --------------------------------------
    glut.glutInit()
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA)
    glut.glutCreateWindow('Awesome fluid simulation')
    glut.glutReshapeWindow(screen_x, screen_y)
    glut.glutReshapeFunc(reshape)
    glut.glutDisplayFunc(display)
    glut.glutIdleFunc(display)
    glut.glutKeyboardFunc(keyboard)

    # Build data
    # --------------------------------------
    data = np.zeros(4, [("position", np.float32, 2),
                        ("color", np.float32, 4)])
    data['position'] = (-1, +1), (+1, +1), (-1, -1), (+1, -1)
    data['color'] = (1, 1, 0, 1), (1, 0, 0, 1), (0, 0, 1, 1), (0, 1, 0, 1)

    # Build & activate program
    # --------------------------------------
    # Request a program and shader slots from GPU
    global program
    program = gl.glCreateProgram()
    vertex = gl.glCreateShader(gl.GL_VERTEX_SHADER)
    fragment = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)

    vertex_code = read_shader('shader.vert')
    fragment_code = read_shader('shader.frag')

    # Set shaders source
    gl.glShaderSource(vertex, vertex_code)
    gl.glShaderSource(fragment, fragment_code)

    # Compile shaders
    gl.glCompileShader(vertex)
    if not gl.glGetShaderiv(vertex, gl.GL_COMPILE_STATUS):
        error = gl.glGetShaderInfoLog(vertex).decode()
        print(error)
        raise RuntimeError("Shader compilation error")

    gl.glCompileShader(fragment)
    gl.glCompileShader(fragment)
    if not gl.glGetShaderiv(fragment, gl.GL_COMPILE_STATUS):
        error = gl.glGetShaderInfoLog(fragment).decode()
        print(error)
        raise RuntimeError("Shader compilation error")

    # Attach shader objects to the program
    gl.glAttachShader(program, vertex)
    gl.glAttachShader(program, fragment)

    # Build program
    gl.glLinkProgram(program)
    if not gl.glGetProgramiv(program, gl.GL_LINK_STATUS):
        print(gl.glGetProgramInfoLog(program))
        raise RuntimeError('Linking error')

    # Get rid of shaders (no more needed)
    gl.glDetachShader(program, vertex)
    gl.glDetachShader(program, fragment)

    # Make program the default program
    gl.glUseProgram(program)

    # Build buffer
    # --------------------------------------

    # Request a buffer slot from GPU
    buffer = gl.glGenBuffers(1)

    # Make this buffer the default one
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffer)

    # Upload data
    gl.glBufferData(gl.GL_ARRAY_BUFFER, data.nbytes, data, gl.GL_DYNAMIC_DRAW)

    # Bind attributes
    # --------------------------------------
    stride = data.strides[0]
    offset = ctypes.c_void_p(0)
    loc = gl.glGetAttribLocation(program, "position")
    gl.glEnableVertexAttribArray(loc)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffer)
    gl.glVertexAttribPointer(loc, 3, gl.GL_FLOAT, False, stride, offset)

    offset = ctypes.c_void_p(data.dtype["position"].itemsize)
    loc = gl.glGetAttribLocation(program, "color")
    gl.glEnableVertexAttribArray(loc)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffer)
    gl.glVertexAttribPointer(loc, 4, gl.GL_FLOAT, False, stride, offset)

    # Bind uniforms
    # --------------------------------------
    loc = gl.glGetUniformLocation(program, "scale")
    gl.glUniform1f(loc, 1.0)

    # Enter mainloop
    # --------------------------------------
    glut.glutMainLoop()


if __name__ == "__main__":
    main()

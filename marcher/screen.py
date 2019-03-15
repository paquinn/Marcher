import os
from _ctypes import byref
from ctypes import create_string_buffer

import pygame
import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *
from pygame.time import get_ticks


def print_log(shader):
    length = c_int()
    glGetShaderiv(shader, GL_INFO_LOG_LENGTH, byref(length))

    if length.value > 0:
        log = create_string_buffer(length.value)
        print(glGetShaderInfoLog(shader))


def compile_shader(source, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)

    status = c_int()
    glGetShaderiv(shader, GL_COMPILE_STATUS, byref(status))
    if not status.value:
        print_log(shader)
        glDeleteShader(shader)
        raise ValueError('Shader compilation failed')
    return shader


def main():
    pygame.init()
    size = width, height = 650, 350
    screen_center = (size[0] / 2, size[1] / 2)
    fps = 60

    black = 0, 0, 0

    screen = pygame.display.set_mode(size, DOUBLEBUF | OPENGL)
    pygame.mouse.set_visible(False)
    pygame.mouse.set_pos(screen_center)
    clock = pygame.time.Clock()
    # gluPerspective(45, (size[0]/size[1]), 0.1, 50.0)

    # vert_dir = os.path.join(os.path.dirname(__file__), 'vert.glsl')
    frag_dir = os.path.join(os.path.dirname(__file__), 'frag2.glsl')
    # v_shader = open(vert_dir).read()
    f_shader = open(frag_dir).read()

    program = glCreateProgram()

    vertex_shader = None
    fragment_shader = None

    # vertex_shader = compile_shader(v_shader, GL_VERTEX_SHADER)
    # glAttachShader(program, vertex_shader)

    fragment_shader = compile_shader(f_shader, GL_FRAGMENT_SHADER)
    glAttachShader(program, fragment_shader)

    glLinkProgram(program)

    # if vertex_shader:
    #     glDeleteShader(vertex_shader)
    if fragment_shader:
        glDeleteShader(fragment_shader)

    resID = glGetUniformLocation(program, "iResolution")
    timeID = glGetUniformLocation(program, "iTime")

    glUseProgram(program)
    glUniform2fv(resID, 1, size)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        # screen.fill(black)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
        glUniform1f(timeID, get_ticks() / 1000)
        glRecti(-1, -1, 1, 1)
        clock.tick(fps)
        pygame.display.flip()


if __name__ == '__main__':
    main()

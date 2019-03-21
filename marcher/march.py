# marcher.py
import inspect

import os
from _ctypes import byref
from ctypes import create_string_buffer

import pygame
import sys
from OpenGL.GL import *
from pygame.locals import *
from pygame.time import get_ticks


class vec:
    def __init__(self, *floats):
        self.floats = []
        # Able to build vecs out of other vecs as in glsl
        for f in floats:
            if type(f) is float or type(f) is int:
                # Make sure everything is a float here
                self.floats.append(float(f))
            elif type(f) is vec:
                self.floats.extend(f.floats)
        self.dim = len(self.floats)

    def __str__(self):
        return 'vec' + str(self.dim) + '(' + ','.join([str(f) for f in self.floats]) + ')'

    def __mul__(self, scalar):
        # Make sure its a float
        scalar = float(scalar)
        return vec(*[scalar * f for f in self.floats])

    __rmul__ = __mul__


# For when you want to be sure of a vec dimension
def vec2(f1, f2):
    return vec(f1, f2)


def vec3(f1, f2, f3):
    return vec(f1, f2, f3)


def make_param(arg_type):
    if arg_type is float:
        return 'float'
    elif arg_type is vec3:
        return 'vec3'


# Base case for recursive compilation
class Var:
    def __init__(self, name):
        self.name = name

    def __call__(self, *_):
        return self

    def __str__(self):
        return self.name


class Function:

    registry = {}
    partials = {}

    class Call:
        def __init__(self, name, args):
            self.name = name
            self.args = list(args)

        def get_args(self):
            return self.args

        def get_usage(self):
            usage = set([self.name])
            for arg in self.get_args():
                if isinstance(arg, Function.Call):
                    usage |= arg.get_usage()
            return usage

        def __str__(self):
            args_list = ','.join([str(arg) for arg in self.get_args()])
            return self.name + '(' + args_list + ')'

    def _call(self, *args):
        return self.__class__.Call(self.name, args)

    def _partial_call(self, *second):
        def partial(*first):
            return self._call(*(first + second))
        return partial


    @staticmethod
    def _default_return():
        return None

    @classmethod
    def register(cls, *dependencies):
        def decorator(fn):
            fun = cls(fn, dependencies)
            setattr(cls, fun.name, fun)
            cls.registry[fun.name] = fun
            cls.partials[fun._call] = fun._partial_call
            return fun._call
        return decorator

    def __init__(self, fn, dependencies):
        self.name = fn.__name__
        assert self.name not in self.registry, "Name %r has already been used" % self.name
        self.params = fn.__annotations__.copy()
        default = self._default_return()
        self.return_type = self.params.pop('return', default)
        assert self.return_type, "%r has no return type specified and no default type" % self.name
        assert not default or self.return_type == default, \
            "r%'s specified return type does not match default" % self.name

        self.fn = fn
        self.dependencies = set(dependencies)

    def get_body(self):
        split = inspect.getsource(self.fn).split('"""')
        assert (len(split) == 3), "%r has no body" % self.name
        return split[1].strip()

    def get_dependencies(self):
        return self.dependencies

    def toposort(self, visited, cycle, stack):
        visited.add(self.name)
        cycle.add(self.name)
        for dep in self.get_dependencies():
            if dep not in visited:
                self.registry[dep].toposort(visited, cycle, stack)
            elif dep in cycle:
                assert False, "Cycle detected, recursion is not supported"
        stack.insert(0, self.name)
        cycle.remove(self.name)

    def __str__(self):
        fun = make_param(self.return_type)+' '+self.name
        fun += '('+','.join([make_param(arg_type)+' '+arg for arg, arg_type in self.params.items()])+')\n'
        fun += '{\n'
        fun += self.get_body()
        fun += '\n}'
        return fun


class Primitive(Function):

    class Call(Function.Call):
        def __init__(self, name, args, location, f=None):
            super().__init__(name, args)
            self.location = location
            self.f = f

        def __call__(self, f):
            apply = f if not self.f else self.f(f)
            return self.__class__(self.name, self.args.copy(), self.location, apply)

        def at(self, location):
            return self.__class__(self.name, self.args.copy(), location, self.f)

        def wrap_location(self):
            if self.location:
                return Translate(self.location, f=self.f)
            else:
                return self.f

        def get_args(self):
            assert self.f, "Compiling a partial"
            return [self.wrap_location()] + self.args

    @staticmethod
    def _default_return():
        return float

    def _call(self, *args, at=None, f=None):
        return self.__class__.Call(self.name, args, at, f)


class Combinator(Function):
    class Call(Function.Call):

        def at(self, location: vec3):
            return self.__class__(self.name, [arg.at(location) for arg in self.args])

        def __call__(self, f):
            return self.__class__(self.name, [arg(f) for arg in self.args])

    @staticmethod
    def _default_return():
        return float


class Operator(Function):
    class Call(Function.Call):

        def __init__(self, name, args, f=None):
            super().__init__(name, args)
            self.f = f

        def __call__(self, f):
            apply = f if not self.f else self.f(f)
            return self.__class__(self.name, self.args.copy(), apply)

        # TODO Wrong way around
        def __mul__(self, other):
            return self.__class__(other.name, other.args.copy(), self)

        # __rmul__ = __mul__

        def get_args(self):
            assert self.f, "Compiling a partial"
            return [self.f] + self.args

    @staticmethod
    def _default_return():
        return vec3

    def _call(self, *args, f=None):
        return self.__class__.Call(self.name, args, f)


class Object(Primitive):
    class Call(Primitive.Call):

        def get_args(self):
            assert self.f, "Compiling a partial"
            return self.args + [self.wrap_location(), Var('res')]

    def __init__(self, fn, dependencies):
        super().__init__(fn, dependencies)
        # Need to make sure the p and res args come at the beginning
        # tmp = self.params
        # self.params = OrderedDict()
        self.params['p'] = vec3
        self.params['res'] = float
        # for arg, arg_type in tmp.items():
        #     self.params[arg] = arg_type
        self.lines = []
        # self.usages = set()

    def _call(self, *args, at=None, f=None):
        return super()._call(*args, at=at, f=f)

    # def res(self, fn, *args):
    #     self.lines.append(self.partials[fn](args)(Var('res'))(Var('p')))

    def res(self, fn, *args):
        line = (Var('res'), fn(*((Var('res'),) + args))(Var('p')))
        self.lines.append(line)
        self.dependencies |= line[1].get_usage()

    def p(self, fn, *args):
        if isinstance(fn, Operator.Call):
            line = (Var('p'), fn(Var('p')))
        else:
            line = (Var('p'), fn(*args)(Var('p')))
        self.lines.append(line)
        self.dependencies |= line[1].get_usage()

    # Lazy evaluation of function for body and dependencies
    def evaluate(self):
        if not self.lines:
            dummy_args = (len(self.fn.__annotations__)) * [None]
            self.fn(*([self] + dummy_args))

    def gen_body(self):
        body = ''
        for var, value in self.lines:
            body += str(var)+'='+str(value)+';\n'
        body += 'return '+str(Var('res'))+';'
        return body

    def get_body(self):
        self.evaluate()
        return self.gen_body()

    def get_dependencies(self):
        self.evaluate()
        return self.dependencies


# --- Primitives --- #
@Primitive.register()
def Plane(p: vec3): """
    return p.y;
"""

@Primitive.register()
def Sphere(p: vec3, r: float) -> float: """
    return length(p) - r;
"""

@Primitive.register()
def Box(p: vec3, b: vec3): """
    vec3 d = abs(p) - b;
    return min(max(d.x, max(d.y, d.z)), 0.0) + length(max(d, 0.0));
"""

# --- Combinators --- #
@Combinator.register()
def Union(d1: float, d2: float): """
    return min(d1, d2);
"""

@Combinator.register()
def Intersect(d1: float, d2: float): """
    return max(d1, d2);
"""

@Combinator.register()
def Subtract(d1: float, d2: float): """
    return max(d1, -d2);
"""


@Operator.register()
def Translate(p: vec3, t: vec3): """
    return p - t; 
"""

@Operator.register()
def Repeat(p: vec3, n: float): """
    return mod(p * n) - n * 0.5; 
"""

class Camera:
    def __init__(self, **kwargs):
        default = {"MAX_STEPS": 100,
                   "MAX_DISTANCE": 100.0,
                   "MIN_DISTANCE": 0.001,
                   "AA": 1,
                   "BACKGROUND": 0.5,
                   "RO": vec3(1, 1, 1),
                   "TA": vec3(0, 0, 0),
                   "LIGHT_POS": vec3(1, 4, 1),
                   "LOOK": 1}

        self.params = {**default, **kwargs}

    def get_statics(self):
        s = ''
        for param, value in self.params.items():
            s += '#define ' + param + ' ' + str(value) + '\n'
        return s

    @staticmethod
    def print_log(shader):
        length = c_int()
        glGetShaderiv(shader, GL_INFO_LOG_LENGTH, byref(length))

        if length.value > 0:
            log = create_string_buffer(length.value)
            print(glGetShaderInfoLog(shader))

    def compile_shader(self, source, shader_type):
        shader = glCreateShader(shader_type)
        glShaderSource(shader, source)
        glCompileShader(shader)

        status = c_int()
        glGetShaderiv(shader, GL_COMPILE_STATUS, byref(status))
        if not status.value:
            self.print_log(shader)
            glDeleteShader(shader)
            raise ValueError('Shader compilation failed')
        return shader

    @staticmethod
    def insert(into, outside, at):
        split = outside.index(at)
        return outside[:split] + into + outside[split:]

    def compile(self, obj):
        statics = self.get_statics()
        stack = []
        obj.toposort(set(), set(), stack)
        functions = ''
        for fn in reversed(stack):
            functions += str(Function.registry[fn]) + '\n'
        frag_dir = os.path.join(os.path.dirname(__file__), 'marcher.glsl')
        f_shader = open(frag_dir).read()
        f_shader = self.insert(statics, f_shader, '// [statics]')
        f_shader = self.insert(functions, f_shader, '// [functions]')

        return f_shader

    def view(self, obj):
        shader = self.compile(obj)
        self.render(shader)

    def save(self, obj, file):
        shader = self.compile(obj)
        open(file, 'w').write(obj)

    def render(self, shader):
        pygame.init()
        size = width, height = 650, 350
        screen_center = (size[0] / 2, size[1] / 2)
        fps = 60

        screen = pygame.display.set_mode(size, DOUBLEBUF | OPENGL)
        pygame.mouse.set_visible(False)
        pygame.mouse.set_pos(screen_center)
        clock = pygame.time.Clock()

        program = glCreateProgram()

        fragment_shader = None

        fragment_shader = self.compile_shader(shader, GL_FRAGMENT_SHADER)
        glAttachShader(program, fragment_shader)

        glLinkProgram(program)

        if fragment_shader:
            glDeleteShader(fragment_shader)

        resID = glGetUniformLocation(program, "iResolution")
        mouseID = glGetUniformLocation(program, "iMouse")
        timeID = glGetUniformLocation(program, "iTime")

        glUseProgram(program)
        glUniform2fv(resID, 1, size)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glUniform1f(timeID, get_ticks() / 1000)
            m = pygame.mouse.get_pos()
            glUniform2fv(mouseID, 1, (m[0], height - m[1]))
            print('fps', clock.get_fps())
            glRecti(-1, -1, 1, 1)
            clock.tick(fps)
            pygame.display.flip()


def main():
    pass
if __name__ == '__main__':
    main()
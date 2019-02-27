import os

from marcher.camera import *
from marcher.primitives import *


class Scene:
    def __init__(self, camera=Camera(), s=None, objs=[]):
        self.camera = camera
        self.objs = objs
        self.s = s

    def smooth(self, s=None):
        self.s = s if s > 0.0 else None
        return self

    def union(self, obj):
        self.objs.append(Union("res", obj, self.s))
        return self

    def intersect(self, obj):
        self.objs.append(Intersect("res", obj, self.s))
        return self

    def subtract(self, obj):
        self.objs.append(Subtract("res", obj, self.s))
        return self

    def mapping(self):
        s = 'float map(vec3 p) {\n'
        s += '\tfloat res = 1e20;\n'
        for obj in self.objs:
            s += '\tres = '+str(obj)+';\n'
        s += '\treturn res;\n'
        s += '}\n'
        return s

    def __str__(self):
        frag_dir = os.path.join(os.path.dirname(__file__), 'frag.glsl')
        f_shader = open(frag_dir).read()

        f_shader = insert(self.mapping(), f_shader, '// [scene]')
        f_shader = insert(str(self.camera), f_shader, '// [camera]')

        return f_shader

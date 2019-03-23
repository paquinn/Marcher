# torus.py

from marcher.march import *

@Primitive.register()
def Torus(p: vec3, t: vec2): """
    vec2 q = vec2(length(p.xy)-t.x,p.z);
    return length(q)-t.y;
"""


@Object.register()
def Scene(self):
    self.res(Union, Torus(vec2(2, 0.75)))

Camera((600, 350), AA=2).view(Object.Scene)
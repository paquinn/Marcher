# object.py
from marcher.march import *

@Object.register()
def MyObject(self):
    self.res(Union, Box(vec3(1.8, 1.8, 1.8)))
    self.res(Intersect, Sphere(2 * 1.2))
    shape = vec2(Var('(1.8 - .5) * (0.5 + 0.5 * sin(1.7 * iTime)) + .6'), 2)
    self.res(Subtract, CylinderX(shape))
    self.res(Subtract, CylinderY(shape))
    self.res(Subtract, CylinderZ(shape))

@Object.register()
def Balls(self):
    offset = Var('0.4 + 1.0 + sin(1.7 * iTime)')
    r = 0.5
    self.p(Mirror())
    self.res(Union, Sphere(r, at=(vec3(offset, 0, 0))))
    self.res(Union, Sphere(r, at=(vec3(0, offset, 0))))
    self.res(Union, Sphere(r, at=(vec3(0, 0, offset))))

@Object.register()
def Scene(self):
    self.res(Union, MyObject())
    self.res(Union, Balls())
    self.res(Union, Plane(at=vec3(0, -2.5, 0)))

c = Camera((650, 380), AA=2)
c.save(Object.Scene, "gen.glsl")
c.view(Object.Scene)

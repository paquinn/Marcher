from marcher.march import *

@Object.register()
def MyObject(self):
    self.res(Union, Box(vec3(1, 1, 1)))
    self.res(Intersect, Sphere(1.3))
    r = 0.5
    l = 2
    self.res(Subtract, CylinderX(vec2(r, l)))
    self.res(Subtract, CylinderY(vec2(r, l)))
    self.res(Subtract, CylinderZ(vec2(r, l)))

@Object.register()
def Infinite(self):
    r = 4.5
    self.p(Repeat(vec3(r, r, r)))
    self.res(Union, MyObject())


c = Camera((650, 380), AA=2)
c.save(Object.Infinite, "gen.glsl")
c.view(Object.Infinite)
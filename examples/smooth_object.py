# smooth.py

from marcher.march import *
@Combinator.register()
def SUnion(d1: float, d2: float, k: float): """
    float h = clamp( 0.5 + 0.5*(d2-d1)/k, 0.0, 1.0 );
    return mix( d2, d1, h ) - k*h*(1.0-h);
"""

@Combinator.register()
def SIntersect(d1: float, d2: float, k: float): """
    float h = clamp( 0.5 - 0.5*(d2-d1)/k, 0.0, 1.0 );
    return mix( d2, d1, h ) + k*h*(1.0-h);
"""

@Combinator.register()
def SSubtract(d2: float, d1: float, k: float): """
    float h = clamp( 0.5 - 0.5*(d2+d1)/k, 0.0, 1.0 );
    return mix( d2, -d1, h ) + k*h*(1.0-h);
"""

@Object.register()
def MyObject(self):

    s = 0.05
    self.res(SUnion, Box(vec3(1, 1, 1)), s)
    self.res(SIntersect, Sphere(1.3), s)
    shape = vec2(0.5, 2)
    self.res(SSubtract, CylinderX(shape), s)
    self.res(SSubtract, CylinderY(shape), s)
    self.res(SSubtract, CylinderZ(shape), s)



c = Camera((650, 380), AA=2)
c.save(Object.MyObject, "gen.glsl")
c.view(Object.MyObject)
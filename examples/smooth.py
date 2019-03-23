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
def MyScene(self):
    sm = 0.5
    box = Box(vec3(1.4, .6, 1.4))
    sph = Sphere(1., at=vec3(0, 1 - 0.6/2, 0))
    u = SUnion(box, sph, sm)
    s = SSubtract(box, sph, sm)
    i = SIntersect(box, sph, sm)
    self.p(Translate, vec3(-3, 0, 0))
    self.res(Union, u)
    self.p(Translate, vec3(3, 0, 0))
    self.res(Union, s)
    self.p(Translate, vec3(3, 0, 0))
    self.res(Union, i)


c = Camera((650, 380), AA=2)
c.save(Object.MyScene, "gen.glsl")
c.view(Object.MyScene)
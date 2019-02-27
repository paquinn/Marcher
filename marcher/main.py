from marcher.util import *
from marcher.primitives import *
from marcher.operators import *
from marcher.scene import *


def main():

    small = 0.3
    # program = Scene(Camera(AA=2,
    #                        RO=vec3_str((2, 2, 2)),
    #                        LIGHT_POS=vec3_str((2, 2, 4))))\
    #     .union(Sphere(2.))\
    #     .intersect(Box((3., 3., 3.)))\
    #     .smooth(0.3)\
    #     .subtract(Sphere(small, (1, 0, 0)))\
    #     .subtract(Sphere(small, (0, 1, 0)))\
    #     .subtract(Sphere(small, (0, 0, 1)))\
    #     .subtract(Sphere(0.7))\
    #     .union(Plane((0, -2, 0)))

    program = Scene(Camera(AA=2,
                           RO=vec3_str((2, 2, 2)),
                           LIGHT_POS=vec3_str((2, 2, 4))))\
        .union(Intersect(Sphere(2., (1, 0, 0)), Sphere(2., (-1, 0, 0))))\
        .union(Plane((0, -2, 0)))

    # print(program)
    open('frag_gen.glsl', 'w').write(str(program))


if __name__ == '__main__':
    main()
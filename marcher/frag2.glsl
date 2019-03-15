uniform vec2 iResolution;
uniform float iTime;
float circle(vec2 ref, vec2 center, float radius) {
    float dist = length(ref - center);
    float outside = smoothstep(radius - .005, radius + .005, dist);
    return 1. - outside;
}

const vec4 blue = vec4(0., 0., .8, 1.);
const vec4 red = vec4(.8, 0., 0., 1.);
const vec4 yellow = vec4(.8, 0.8, 0., 1.);

float xVar = 1./3.;
float yVar = 1./3.;
float radius = .25;

void main()
{

    vec2 fragCoord = gl_FragCoord.xy;

	vec2 uv = fragCoord.xy / iResolution.xy;
    vec2 ref = 2. * (fragCoord.xy - .5 * iResolution.xy) / iResolution.y;
    float xMax = iResolution.x / iResolution.y;
    gl_FragColor = vec4(0.);

    float x = cos(iTime) * yVar;
    float c = circle(ref, vec2(-xVar, x), radius);
    gl_FragColor += c * blue;

    x = -cos(iTime) * yVar;
    c = circle(ref, vec2(xVar, x), radius);
    gl_FragColor += c * red;


    x = sin(iTime) * xVar;
    c = circle(ref, vec2(x, 0.), radius);
    gl_FragColor += c * yellow;
}
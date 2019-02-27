//---Rendering Parameters---
#define MAX_STEPS 100
#define MAX_DISTANCE 100.0
#define MIN_DISTANCE 0.001
#define AA 2
#define BACKGROUND 0.5
#define RO vec3(2,2,2)
#define TA vec3(0,0,0)
#define LIGHT_POS vec3(2,2,4)
#define LOOK 1
// [camera]

//---Primitive Distance Estimators---
float sdPlane(vec3 p) {
    return p.y;
}

float sdSphere(vec3 p, float r) {
    return length(p) - r;
}

float sdBox(vec3 p, vec3 b) {
    vec3 d = abs(p) - b;
    return min(max(d.x, max(d.y, d.z)), 0.0) + length(max(d, 0.0));
}

float sdCylinderY(vec3 p, vec2 h) {
    vec2 d = abs(vec2(length(p.xz),p.y)) - h;
    return min(max(d.x,d.y),0.0) + length(max(d,0.0));
}

float sdCylinderZ(vec3 p, vec2 h) {
    vec2 d = abs(vec2(length(p.xy),p.z)) - h;
    return min(max(d.x,d.y),0.0) + length(max(d,0.0));
}

float sdCylinderX(vec3 p, vec2 h) {
    vec2 d = abs(vec2(length(p.yz),p.x)) - h;
    return min(max(d.x,d.y),0.0) + length(max(d,0.0));
}

//---Combinator Operators---
float opIntersect(float d1, float d2) {
    return max(d1, d2);
}

float opUnion(float d1, float d2) {
    return min(d1, d2);
}

float opSubtract(float d1, float d2) {
    return max(d1, -d2);
}

//---Smoothed Combinator Operators---
float opSmoothUnion( float d1, float d2, float k ) {
    float h = clamp( 0.5 + 0.5*(d2-d1)/k, 0.0, 1.0 );
    return mix( d2, d1, h ) - k*h*(1.0-h);
}

float opSmoothSubtract( float d2, float d1, float k ) {
    float h = clamp( 0.5 - 0.5*(d2+d1)/k, 0.0, 1.0 );
    return mix( d2, -d1, h ) + k*h*(1.0-h);
}

float opSmoothIntersect( float d1, float d2, float k ) {
    float h = clamp( 0.5 - 0.5*(d2-d1)/k, 0.0, 1.0 );
    return mix( d2, d1, h ) + k*h*(1.0-h);
}

//---Transformers---
vec3 opTranslate(vec3 p, vec3 t) {
    return p - t;
}

vec3 opRep(vec3 p, vec3 c) {
    return mod(p, c) - 0.5 * c;
}

float opSineDisplacement(vec3 p, float k) {
    return sin(k*p.x)*sin(k*p.y)*sin(k*p.z);
}

//---Scene Definition---
float map(vec3 p) {
	float res = 1e20;
	res = opUnion(res,opIntersect(sdSphere(opTranslate(p,vec3(1,0,0)),2.0),sdSphere(opTranslate(p,vec3(-1,0,0)),2.0)));
	res = opUnion(res,sdPlane(opTranslate(p,vec3(0,-2,0))));
	return res;
}
// [scene]

//---Rendering Code---
float raymarch(vec3 ro, vec3 rd) {
	float dO = 0.0;

    for (int i = 0; i < MAX_STEPS; i++) {
    	vec3 p = ro + rd*dO;
        float dS = map(p);
        dO += dS;
        if(dO > MAX_DISTANCE || dS < MIN_DISTANCE) break;
    }

    return dO;
}

vec3 normal(in vec3 p) {
    float d = map(p);
    vec2 e = vec2(1., 0) * 0.01;
    vec3 n = d - vec3(map(p-e.xyy),map(p-e.yxy), map(p-e.yyx));
    return normalize(n);
}

float light(vec3 p, vec3 lp) {
    vec3 l = normalize(lp - p);
    vec3 n = normal(p);

   	float dif = clamp(dot(n, l), 0., 1.);
    float d = raymarch(p + MIN_DISTANCE * n * 2., l);
    if (d < length(lp - p)) dif *= 0.1;
    return dif;
}

float lighting(vec3 p) {
    vec3 l = LIGHT_POS;
    float dif = 0.0;
    dif += light(p, l);
    return clamp(dif, 0.0, 1.0);
}

mat3 setCamera( in vec3 ro, in vec3 ta, float cr )
{
	vec3 cw = normalize(ta-ro);
	vec3 cp = vec3(sin(cr), cos(cr),0.0);
	vec3 cu = normalize( cross(cw,cp) );
	vec3 cv =          ( cross(cu,cw) );
    return mat3( cu, cv, cw );
}

vec3 render(in vec3 ro, in vec3 rd) {
    float d = raymarch(ro, rd);

    vec3 p = ro + rd * d;
    float dif = lighting(p);

    return vec3(dif);
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{

    vec2 mouse = iMouse.xy/iResolution.xy;
    float time = 15.0 + iTime;

	vec3 ray_origin = vec3(6.*sin(10.*mouse.x), 2. + 10.*mouse.y, 6.*cos(10.*mouse.x));
    vec3 ta = TA;
	mat3 ca = setCamera(ray_origin, ta, 0.0);

    vec3 tot = vec3(0.0);
#if AA > 1
    for (int i = 0; i < AA; i++) {
        for (int j = 0; j < AA; j++) {
            vec2 o = vec2(float(i), float(j)) / float(AA) - 0.5;
    		vec2 p = (2.0*(fragCoord + o) - iResolution.xy)/iResolution.y;
#else
            vec2 p = (2.0*fragCoord - iResolution.xy)/iResolution.y;
#endif
            vec3 ray_direction = ca * normalize(vec3(p.x, p.y, 2.0));
            vec3 col = render(ray_origin, ray_direction);

			tot += col;
#if AA > 1
		}
	}
	tot /= float(AA * AA);
#endif

    fragColor = vec4(tot, 0);
}
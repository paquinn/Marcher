uniform vec2 iResolution;
uniform float iTime;
uniform vec2 iMouse;

// [statics]

// [functions]

//---Rendering Code---

float raymarch(vec3 ro, vec3 rd) {
	float dO = 0.0;

    for (int i = 0; i < MAX_STEPS; i++) {
    	vec3 p = ro + rd*dO;
        float dS = DE(p);
        dO += dS;
        if(dO > MAX_DISTANCE || dS < MIN_DISTANCE) break;
    }

    return dO;
}

vec3 normal(in vec3 p) {
    float d = DE(p);
    vec2 e = vec2(1., 0) * 0.01;
    vec3 n = d - vec3(DE(p-e.xyy),DE(p-e.yxy), DE(p-e.yyx));
    return normalize(n);
}


mat3 setCamera( in vec3 ro, in vec3 ta, float cr )
{
	vec3 cw = normalize(ta-ro);
	vec3 cp = vec3(sin(cr), cos(cr),0.0);
	vec3 cu = normalize( cross(cw,cp) );
	vec3 cv =          ( cross(cu,cw) );
    return mat3( cu, cv, cw );
}

float calcAO( in vec3 pos, in vec3 nor ) {
	float occ = 0.0;
    float sca = 1.0;
    for( int i=0; i<5; i++ )
    {
        float hr = 0.01 + 0.12*float(i)/4.0;
        vec3 aopos =  nor * hr + pos;
        float dd = DE(aopos);
        occ += -(dd-hr)*sca;
        sca *= 0.95;
    }
    return clamp( 1.0 - 3.0*occ, 0.0, 1.0 ) * (0.5+0.5*nor.y);
}

float calcSoftshadow( in vec3 ro, in vec3 rd, in float mint, in float tmax )
{
    // bounding volume

    float res = 1.0;
    float t = mint;
    for( int i=0; i<16; i++ )
    {
		float h = DE( ro + rd*t );
        res = min( res, 8.0*h/t );
        t += clamp( h, 0.02, 0.10 );
        if( res<0.005 || t>tmax ) break;
    }
    return clamp( res, 0.0, 1.0 );
}

vec3 render(in vec3 ro, in vec3 rd) {
    vec3 col = BACKGROUND +rd.y*0.8;

    float t = raymarch(ro, rd);


    if (t < MAX_DISTANCE) {
        vec3 pos = ro + rd * t;
        vec3 nor = normal(pos);
        vec3 ref = reflect(rd, nor);
        col = MATERIAL;
        float occ = calcAO( pos, nor );
        vec3  lig = normalize( vec3(-0.4, 0.7, -0.6) );
        vec3  hal = normalize( lig-rd );
        float amb = clamp( 0.5+0.5*nor.y, 0.0, 1.0 );
        float dif = clamp( dot( nor, lig ), 0.0, 1.0 );
        float bac = clamp( dot( nor, normalize(vec3(-lig.x,0.0,-lig.z))), 0.0, 1.0 )*clamp( 1.0-pos.y,0.0,1.0);
        float dom = smoothstep( -0.2, 0.2, ref.y );
        float fre = pow( clamp(1.0+dot(nor,rd),0.0,1.0), 2.0 );


        dif *= calcSoftshadow( pos, lig, 0.02, 2.5 );
        dom *= calcSoftshadow( pos, ref, 0.02, 2.5 );

        float spe = pow( clamp( dot( nor, hal ), 0.0, 1.0 ),16.0)*
                    dif *
                    (0.04 + 0.96*pow( clamp(1.0+dot(hal,rd),0.0,1.0), 5.0 ));

        vec3 lin = vec3(0.0);
        lin += 1.40*dif*vec3(1.00,0.80,0.55);
        lin += 0.20*amb*vec3(0.40,0.60,1.00)*occ;
        lin += 0.40*dom*vec3(0.40,0.60,1.00)*occ;
        lin += 0.50*bac*vec3(0.25,0.25,0.25)*occ;
        lin += 0.25*fre*vec3(1.00,1.00,1.00)*occ;
        col = col*lin;
        col += 9.00*spe*vec3(1.00,0.90,0.70);

        col = mix( col, vec3(0.8,0.9,1.0), 1.0-exp( -0.0002*t*t*t ) );
    }

    return vec3( clamp(col,0.0,1.0) );
}

void main()
{

    vec2 mouse = iMouse.xy/iResolution.xy;
    float time = 15.0 + iTime;

	vec3 ray_origin = vec3(10.*sin(10.*mouse.x), 2. + 20.*(mouse.y - 0.5), 10.*cos(10.*mouse.x));
    vec3 ta = TA;
	mat3 ca = setCamera(ray_origin, ta, 0.0);

    vec3 tot = vec3(0.0);
#if AA > 1
    for (int i = 0; i < AA; i++) {
        for (int j = 0; j < AA; j++) {
            vec2 o = vec2(float(i), float(j)) / float(AA) - 0.5;
    		vec2 p = (2.0*(gl_FragCoord.xy + o) - iResolution.xy)/iResolution.y;
#else
            vec2 p = (2.0*gl_FragCoord.xy - iResolution.xy)/iResolution.y;
#endif
            vec3 ray_direction = ca * normalize(vec3(p.x, p.y, 2.0));
            vec3 col = render(ray_origin, ray_direction);

			tot += col;
#if AA > 1
		}
	}
	tot /= float(AA * AA);
#endif

    gl_FragColor = vec4(tot, 0);
}
import React, { useEffect, useRef } from 'react';

/**
 * Holographic 3D Topography Shader — Full-width Perspective & Inward-Stretched Valley
 * 
 * Features:
 * - 3D Perspective ray/valley projection (inward stretched landscape)
 * - Multi-octave Simplex / FBM noise heightmap
 * - Glowing topographic isolines / contour lines (step & smoothstep)
 * - Mouse ripple / vortex warp interaction
 * - Holographic chromatic aberration (RGB channel splitting near cursor)
 * - Intense center lens flare & glow on mouse influence
 * - Subtle ambient particle field floating and drifting across the depth
 * - Istikshaf technical noir color scheme (#070A09, #B6F542, #40D9E8)
 */
export const ElectricityShader: React.FC<{ className?: string }> = ({ className = '' }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    function syncSize() {
      if (!canvas) return;
      const rect = canvas.getBoundingClientRect();
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const w = Math.floor(rect.width * dpr) || 1920;
      const h = Math.floor(rect.height * dpr) || 1080;
      if (canvas.width !== w || canvas.height !== h) {
        canvas.width = w;
        canvas.height = h;
      }
    }

    let ro: ResizeObserver | null = null;
    if (typeof ResizeObserver !== 'undefined') {
      ro = new ResizeObserver(syncSize);
      ro.observe(canvas);
    }
    syncSize();

    const gl = (canvas.getContext('webgl') || canvas.getContext('experimental-webgl')) as WebGLRenderingContext | null;
    if (!gl) return;

    // ── Vertex Shader ──
    const vs = `
      attribute vec2 a_position;
      void main() {
        gl_Position = vec4(a_position, 0.0, 1.0);
      }
    `;

    // ── Fragment Shader ──
    const fs = `
      precision highp float;
      uniform float u_time;
      uniform vec2  u_resolution;
      uniform vec2  u_mouse;        // Screen space pixels (0..res.x, 0..res.y)
      uniform float u_mouse_active; // 1.0 when mouse is inside, decays to 0.0

      // --- Simplex / 2D Noise functions ---
      vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
      vec2 mod289(vec2 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
      vec3 permute(vec3 x) { return mod289(((x * 34.0) + 1.0) * x); }

      float snoise(vec2 v) {
        const vec4 C = vec4(0.211324865405187,  // (3.0-sqrt(3.0))/6.0
                            0.366025403784439,  // 0.5*(sqrt(3.0)-1.0)
                           -0.577350269189626,  // -1.0 + 2.0 * C.x
                            0.024390243902439); // 1.0 / 41.0
        vec2 i  = floor(v + dot(v, C.yy));
        vec2 x0 = v - i + dot(i, C.xx);
        vec2 i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
        vec4 x12 = x0.xyxy + C.xxzz;
        x12.xy -= i1;
        i = mod289(i);
        vec3 p = permute(permute(i.y + vec3(0.0, i1.y, 1.0)) + i.x + vec3(0.0, i1.x, 1.0));
        vec3 m = max(0.5 - vec3(dot(x0, x0), dot(x12.xy, x12.xy), dot(x12.zw, x12.zw)), 0.0);
        m = m * m;
        m = m * m;
        vec3 x_ = 2.0 * fract(p * C.www) - 1.0;
        vec3 h = abs(x_) - 0.5;
        vec3 ox = floor(x_ + 0.5);
        vec3 a0 = x_ - ox;
        m *= 1.79284291400159 - 0.85373472095314 * (a0 * a0 + h * h);
        vec3 g;
        g.x  = a0.x  * x0.x  + h.x  * x0.y;
        g.yz = a0.yz * x12.xz + h.yz * x12.yw;
        return 130.0 * dot(m, g);
      }

      // --- Multi-octave FBM for organic terrain height ---
      float fbm(vec2 p) {
        float total = 0.0;
        float amp = 0.5;
        vec2 shift = vec2(37.0, 17.0);
        mat2 rot = mat2(cos(0.45), sin(0.45), -sin(0.45), cos(0.45));
        for (int i = 0; i < 4; i++) {
          total += amp * snoise(p);
          p = rot * p * 2.0 + shift;
          amp *= 0.5;
        }
        return total;
      }

      // Height evaluation at point p with mouse distortion
      float evaluateHeight(vec2 p, vec2 mouseUV, float mouseInf, float time) {
        // Continuous slow terrain drift
        vec2 drift = vec2(time * 0.04, time * 0.025);
        vec2 coord = p * 2.2 + drift;

        // Mouse ripple / warp
        if (mouseInf > 0.01) {
          float d = length(p - mouseUV);
          float wave = sin(d * 18.0 - time * 5.0) * exp(-d * 3.5);
          coord += normalize(p - mouseUV + 0.001) * wave * 0.35 * mouseInf;
        }

        return fbm(coord);
      }

      // Random generator for stars/particles
      float hash(vec2 p) {
        p = fract(p * vec2(234.34, 435.345));
        p += dot(p, p + 34.23);
        return fract(p.x * p.y);
      }

      void main() {
        // Normalized coordinates (-aspect .. aspect, -1.0 .. 1.0)
        vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / u_resolution.y;

        // Mouse in same coordinate space
        vec2 mouseUV = (u_mouse - 0.5 * u_resolution.xy) / u_resolution.y;
        float mouseDist = length(uv - mouseUV);
        float mouseInf = exp(-mouseDist * mouseDist * 12.0) * u_mouse_active;

        // ── 3D Inward-Stretched Perspective Projection ──
        // Horizon set slightly below center to create an expansive sweeping valley
        float horizon = -0.15;
        float dy = uv.y - horizon;

        // Curved tunnel/valley coordinate projection
        float depth = 1.0 / (abs(dy) + 0.12);
        // Perspective stretch in X as depth increases (stretching inwards)
        float px = uv.x * depth * 0.85;
        float py = (dy > 0.0 ? 1.0 : -1.0) * (depth * 0.45) + (uv.x * uv.x * 0.3 * sign(dy));
        vec2 terrainP = vec2(px, py);

        // ── Colors from Istikshaf Design System ──
        vec3 bgColor    = vec3(0.027, 0.039, 0.035); // #070A09
        vec3 neonGreen  = vec3(0.714, 0.961, 0.259); // #B6F542 (Brand Primary)
        vec3 cyanAccent = vec3(0.251, 0.851, 0.910); // #40D9E8 (Smart Meter Cyan)
        vec3 amberGlow  = vec3(0.960, 0.725, 0.259); // #F5B942 (Monthly Amber)
        vec3 pureWhite  = vec3(1.0, 1.0, 1.0);

        // ── Holographic Chromatic Aberration Sample ──
        // Split RGB channels near cursor
        float chromOffset = 0.025 * mouseInf;
        float hR = evaluateHeight(terrainP + vec2(chromOffset, 0.0), mouseUV, mouseInf, u_time);
        float hG = evaluateHeight(terrainP, mouseUV, mouseInf, u_time);
        float hB = evaluateHeight(terrainP - vec2(chromOffset, 0.0), mouseUV, mouseInf, u_time);

        // ── Topographic Contour / Isoline Extraction ──
        float contourDensity = 14.0;
        
        // Green channel isolines (base)
        float valG = hG * contourDensity;
        float lineG = abs(fract(valG) - 0.5);
        float isoG = 1.0 - smoothstep(0.0, 0.07, lineG);

        // Red & Blue offset isolines for chromatic aberration
        float valR = hR * contourDensity;
        float isoR = 1.0 - smoothstep(0.0, 0.07, abs(fract(valR) - 0.5));

        float valB = hB * contourDensity;
        float isoB = 1.0 - smoothstep(0.0, 0.07, abs(fract(valB) - 0.5));

        // Fine secondary topographic contour lines
        float fineVal = hG * contourDensity * 2.5;
        float fineIso = 1.0 - smoothstep(0.0, 0.05, abs(fract(fineVal) - 0.5));

        // Perspective depth fade (atmospheric falloff towards horizon and corners)
        float depthFade = smoothstep(0.0, 0.45, abs(dy)) * smoothstep(12.0, 1.0, depth);
        
        // Base terrain composite
        vec3 terrainColor = vec3(0.0);
        
        // Chromatic split contribution
        terrainColor.r += isoR * 0.9;
        terrainColor.g += isoG * 1.1;
        terrainColor.b += isoB * 1.2;

        // Tint lines with brand neon green and smart-meter cyan gradient
        vec3 lineTint = mix(neonGreen, cyanAccent, clamp(hG * 1.2 + 0.3, 0.0, 1.0));
        terrainColor *= lineTint;

        // Add fine lines & height glow
        terrainColor += fineIso * cyanAccent * 0.25;
        terrainColor += smoothstep(-0.2, 0.6, hG) * neonGreen * 0.04;

        // Energy pulses traveling along the terrain waves
        float pulse = sin(valG * 1.5 - u_time * 4.0) * 0.5 + 0.5;
        terrainColor += isoG * pulse * cyanAccent * 0.3;

        // Apply depth fading to terrain
        vec3 col = bgColor + terrainColor * depthFade;

        // ── Floating Subtle Particle Field (Stars & Energy Dust) ──
        // Screen-space point grid for sparse glowing particles
        vec2 particleGrid = floor((uv + vec2(10.0)) * 28.0);
        float pRand = hash(particleGrid);
        
        if (pRand > 0.91) {
          vec2 pCenter = (particleGrid + 0.5) / 28.0 - vec2(10.0);
          
          // Subtle particle float animation
          float pPhase = u_time * 0.8 + pRand * 6.28;
          pCenter += vec2(sin(pPhase) * 0.015, cos(pPhase * 0.7) * 0.015);
          
          // Particle distance and glow
          float pDist = length(uv - pCenter);
          float pSize = 0.0035 + (pRand - 0.91) * 0.04;
          float pGlow = smoothstep(pSize * 4.0, 0.0, pDist);
          float pCore = smoothstep(pSize, 0.0, pDist);
          
          // Color particles neon green with cyan/amber highlights
          vec3 pCol = (pRand > 0.97) ? cyanAccent : (pRand > 0.94 ? amberGlow : neonGreen);
          col += pCol * (pGlow * 0.4 + pCore * 0.8) * (0.6 + 0.4 * sin(pPhase * 2.0));
        }

        // ── Intense Cursor Lens Flare & Holographic Glow ──
        if (u_mouse_active > 0.01) {
          // Intense core flare
          float coreFlare = exp(-mouseDist * 24.0) * u_mouse_active;
          // Diffuse surrounding glow
          float haloFlare = exp(-mouseDist * 5.0) * u_mouse_active;
          // Ring flare
          float ringFlare = smoothstep(0.18, 0.14, mouseDist) * smoothstep(0.10, 0.14, mouseDist) * u_mouse_active;

          col += pureWhite * coreFlare * 0.75;
          col += neonGreen * coreFlare * 1.2;
          col += cyanAccent * haloFlare * 0.35;
          col += amberGlow * ringFlare * 0.4;
        }

        // ── Horizontal Center Horizon Light Beam ──
        float horizonBeam = exp(-abs(dy) * 45.0) * 0.12 * smoothstep(1.2, 0.0, abs(uv.x));
        col += mix(neonGreen, cyanAccent, 0.5) * horizonBeam;

        // ── Vignette & Edge Fade ──
        vec2 vUv = gl_FragCoord.xy / u_resolution.xy;
        float vignette = smoothstep(0.0, 0.4, vUv.x) * smoothstep(1.0, 0.6, vUv.x) *
                         smoothstep(0.0, 0.4, vUv.y) * smoothstep(1.0, 0.6, vUv.y);
        col = mix(bgColor, col, clamp(vignette * 1.3, 0.0, 1.0));

        gl_FragColor = vec4(clamp(col, 0.0, 1.0), 1.0);
      }
    `;

    function compileShader(type: number, src: string) {
      const s = gl!.createShader(type)!;
      gl!.shaderSource(s, src);
      gl!.compileShader(s);
      if (!gl!.getShaderParameter(s, gl!.COMPILE_STATUS)) {
        console.warn('Shader compile log:', gl!.getShaderInfoLog(s));
      }
      return s;
    }

    const prog = gl.createProgram()!;
    gl.attachShader(prog, compileShader(gl.VERTEX_SHADER, vs));
    gl.attachShader(prog, compileShader(gl.FRAGMENT_SHADER, fs));
    gl.linkProgram(prog);
    gl.useProgram(prog);

    const buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
    const pos = gl.getAttribLocation(prog, 'a_position');
    gl.enableVertexAttribArray(pos);
    gl.vertexAttribPointer(pos, 2, gl.FLOAT, false, 0, 0);

    const uTime = gl.getUniformLocation(prog, 'u_time');
    const uRes = gl.getUniformLocation(prog, 'u_resolution');
    const uMouse = gl.getUniformLocation(prog, 'u_mouse');
    const uMouseActive = gl.getUniformLocation(prog, 'u_mouse_active');

    // Track mouse coordinates with smooth easing
    let targetMouseX = canvas.width / 2;
    let targetMouseY = canvas.height / 2;
    let currentMouseX = targetMouseX;
    let currentMouseY = targetMouseY;
    let mouseActive = 0.0;
    let targetMouseActive = 0.0;

    const handleMouseMove = (e: MouseEvent) => {
      const rect = canvas!.getBoundingClientRect();
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      targetMouseX = (e.clientX - rect.left) * dpr;
      targetMouseY = (rect.height - (e.clientY - rect.top)) * dpr; // Invert Y for WebGL
      targetMouseActive = 1.0;
    };

    const handleMouseEnter = () => {
      targetMouseActive = 1.0;
    };

    const handleMouseLeave = () => {
      targetMouseActive = 0.0;
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseenter', handleMouseEnter);
    window.addEventListener('mouseleave', handleMouseLeave);

    let raf: number;
    function render(t: number) {
      if (typeof ResizeObserver === 'undefined') syncSize();
      gl!.viewport(0, 0, canvas!.width, canvas!.height);

      // Smooth mouse interpolation
      currentMouseX += (targetMouseX - currentMouseX) * 0.1;
      currentMouseY += (targetMouseY - currentMouseY) * 0.1;
      mouseActive += (targetMouseActive - mouseActive) * 0.08;

      if (uTime) gl!.uniform1f(uTime, t * 0.001);
      if (uRes) gl!.uniform2f(uRes, canvas!.width, canvas!.height);
      if (uMouse) gl!.uniform2f(uMouse, currentMouseX, currentMouseY);
      if (uMouseActive) gl!.uniform1f(uMouseActive, mouseActive);

      gl!.drawArrays(gl!.TRIANGLE_STRIP, 0, 4);
      raf = requestAnimationFrame(render);
    }
    render(0);

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseenter', handleMouseEnter);
      window.removeEventListener('mouseleave', handleMouseLeave);
      if (ro) ro.disconnect();
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className={className}
      style={{ display: 'block', width: '100%', height: '100%' }}
    />
  );
};

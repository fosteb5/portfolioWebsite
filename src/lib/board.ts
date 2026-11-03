/**
 * The lit circuit board behind every hero.
 *
 * A canvas paints the board into three channels: red for copper height,
 * green for exposed gold, blue for silkscreen. A small WebGL2 fragment shader then
 * lights that map from the pointer, so the copper reads through the glossy mask.
 * No 3D library is involved, which keeps this to a few kilobytes.
 */
import type { BoardColour } from '../content';
import { BOARDS } from './boards';
import { layoutWord, type Point } from './trace-font';

const VERTEX = `#version 300 es
out vec2 v;
void main(){vec2 p=vec2((gl_VertexID<<1)&2,gl_VertexID&2);v=p;gl_Position=vec4(p*2.-1.,0.,1.);}`;

const FRAGMENT = `#version 300 es
precision highp float;
in vec2 v; out vec4 o;
uniform sampler2D M;
uniform vec2 Lamp;
uniform float Aspect,Gain;
uniform vec3 Void,Mask,Copper,Gold,Silk;
void main(){
  vec4 m=texture(M,v);
  vec2 px=1./vec2(textureSize(M,0));
  float s=1.6;
  float hx=texture(M,v+vec2(px.x*s,0.)).r-texture(M,v-vec2(px.x*s,0.)).r;
  float hy=texture(M,v+vec2(0.,px.y*s)).r-texture(M,v-vec2(0.,px.y*s)).r;
  vec2 q=vec2(v.x*Aspect,v.y);
  vec3 N=normalize(vec3(-hx*1.7,-hy*1.7,1.));
  vec3 P=vec3(q,0.),Lp=vec3(Lamp.x*Aspect,Lamp.y,.36);
  vec3 L=normalize(Lp-P),H=normalize(L+vec3(0.,0.,1.));
  float d=length(Lp.xy-P.xy),fall=1./(1.+d*d*11.);
  float dif=max(dot(N,L),0.),nh=max(dot(N,H),0.);
  // The map stores 0 for clearance, 0.47 for the ground pour and 1 for a trace.
  vec3 base=m.r<.47?mix(Void,Mask,m.r/.47):mix(Mask,Copper,(m.r-.47)/.53);
  vec3 col=base*(.84+.84*Gain*dif*fall);
  col+=mix(vec3(.82,.94,.88),base*2.2,.5)*(pow(nh,340.)*.3+pow(nh,48.)*.05)*fall*min(Gain,1.);
  col=mix(col,Gold*(.8+.32*dif*fall)+vec3(1.,.9,.62)*pow(nh,26.)*fall*.28,m.g);
  col=mix(col,Silk*(.9+.14*fall),m.b);
  o=vec4(col,1.);
}`;

const hexToRgb = (hex: string): [number, number, number] => {
  const n = parseInt(hex.slice(1), 16);
  return [(n >> 16 & 255) / 255, (n >> 8 & 255) / 255, (n & 255) / 255];
};

interface Trace { points: Point[]; width: number }
interface Pad { x: number; y: number; r: number; hole: number }
type Rect = [number, number, number, number];

interface PaintSpec {
  W: number;
  H: number;
  k: number;
  words: { text: string; left: number; top: number; unit: number }[];
  keepouts: Rect[];
  chipLabel: string;
  mark: string;
  gutter: number;
}

/** Paints the board. Returns the canvas and where the main net leaves it. */
function paintMap(spec: PaintSpec) {
  const { W, H, k, words, keepouts, chipLabel, mark } = spec;
  const canvas = document.createElement('canvas');
  canvas.width = W;
  canvas.height = H;
  const g = canvas.getContext('2d', { willReadFrequently: true })!;

  const u = words[0].unit;
  const landscape = W / H > 1.2;
  const traces: Trace[] = [];
  const pads: Pad[] = [];
  const rects: Rect[] = [];

  const heavy = 0.66 * u;
  const thin = 0.25 * u;
  const clear = 0.5 * u;

  /* Lettering */
  let nameRight = 0;
  let nameTop = Infinity;
  let nameBottom = 0;
  for (const word of words) {
    const layout = layoutWord(word.text);
    const s = word.unit;
    for (const glyph of layout.glyphs) {
      for (const stroke of glyph.strokes) {
        traces.push({ points: stroke.map(([x, y]): Point => [word.left + x * s, word.top + y * s]), width: 0.66 * s });
      }
      for (const [x, y] of glyph.pads) {
        pads.push({ x: word.left + x * s, y: word.top + y * s, r: 0.56 * s, hole: 0.24 * s });
      }
    }
    nameRight = Math.max(nameRight, word.left + layout.width * s);
    nameTop = Math.min(nameTop, word.top);
    nameBottom = Math.max(nameBottom, word.top + 6 * s);
  }

  const footTop = keepouts.length ? Math.min(...keepouts.map((r) => r[1])) : H;

  /* U1 and its routing */
  const room = landscape ? W - nameRight : H;
  const showChip = landscape ? room > 15 * u : footTop - nameBottom > 13 * u;
  let netX = W - spec.gutter * 0.5;

  if (showChip) {
    const a = landscape ? Math.min(3.9 * u, H * 0.14) : Math.min(4.2 * u, (footTop - nameBottom) * 0.2);
    const cx = landscape ? nameRight + (W - nameRight) * 0.52 : W * 0.64;
    const cy = landscape ? (nameTop + nameBottom) / 2 : nameBottom + (footTop - nameBottom) * 0.5;
    const n = 7;
    const pitch = (a * 2) / (n + 1);
    const padLong = a * 0.36;
    const padWide = pitch * 0.54;
    const off = (i: number) => (i - (n - 1) / 2) * pitch;

    for (let i = 0; i < n; i++) {
      const o = off(i);
      rects.push(
        [cx + o - padWide / 2, cy - a - padLong, padWide, padLong],
        [cx + o - padWide / 2, cy + a, padWide, padLong],
        [cx - a - padLong, cy + o - padWide / 2, padLong, padWide],
        [cx + a, cy + o - padWide / 2, padLong, padWide],
      );
      const y = cy + o;
      const right = cx + a + padLong;
      const fanY = cy + o * 2.1;
      const dx = Math.abs(fanY - y);
      if (i < n - 1 || landscape) {
        traces.push({ points: [[right, y], [right + 1.1 * pitch, y], [right + 1.1 * pitch + dx, fanY], [W + 20, fanY]], width: thin });
      }
      const left = cx - a - padLong;
      const stubY = cy + o * 1.8;
      const dl = Math.abs(stubY - y);
      const end = left - pitch - dl - (i % 2) * 1.4 * pitch;
      traces.push({ points: [[left, y], [left - pitch, y], [left - pitch - dl, stubY], [end, stubY]], width: thin });
      pads.push({ x: end, y: stubY, r: 0.34 * u, hole: 0.14 * u });
    }

    const gap = Math.max(pitch * 1.1, 0.9 * u);
    const lean = pitch * 1.7;
    const chipBottom = cy + a + padLong;
    const chipTop = cy - a - padLong;
    const topFirst = landscape ? nameTop - 1.8 * u : nameBottom + 1.7 * u + (n - 1) * gap;
    const bottomFirst = landscape ? nameBottom + 1.8 * u : chipBottom + lean + 0.8 * u;
    const bottomLimit = footTop - 0.9 * u;

    for (let i = 0; i < n; i++) {
      const x = cx + off(i);
      const inBus = landscape ? i % 2 === 0 || i === 3 : true;
      const row = landscape ? [0, 0, 1, 2, 3, 3, 4][i] : i;
      const yTop = topFirst - row * gap;
      if (inBus && yTop > -2 && yTop + lean < chipTop) {
        traces.push({ points: [[x, chipTop], [x, yTop + lean], [x - lean, yTop], [-20, yTop]], width: thin });
      }
      // The last bottom pin is the main net, so the bus stops one short.
      const yBottom = bottomFirst + row * gap;
      if (inBus && i < n - 1 && yBottom < bottomLimit && yBottom - lean > chipBottom) {
        traces.push({ points: [[x, chipBottom], [x, yBottom - lean], [x - lean, yBottom], [-20, yBottom]], width: thin });
      }
    }

    /* The main net: leaves U1 and carries on down the page. */
    const netStart = cx + off(n - 1);
    const dropTo = Math.min(footTop - 1.4 * u, H - 1.6 * u);
    const toLane = netX - netStart;
    if (landscape) {
      traces.push({ points: [[netStart, chipBottom], [netStart, dropTo - toLane], [netX, dropTo], [netX, H + 20]], width: heavy * 0.7 });
    } else {
      const y = cy + off(n - 1);
      const right = cx + a + padLong;
      const dy = netX - right - pitch;
      traces.push({ points: [[right, y], [right + pitch, y], [netX, y + dy], [netX, H + 20]], width: heavy * 0.7 });
    }

    /* Ground pad under the chip */
    rects.push([cx - a * 0.48, cy - a * 0.48, a * 0.96, a * 0.96]);

    paintLayers();

    g.fillStyle = '#00f';
    g.strokeStyle = '#00f';
    g.lineWidth = Math.max(1.5 * k, 0.14 * u);
    g.strokeRect(cx - a, cy - a, a * 2, a * 2);
    g.beginPath();
    g.arc(cx - a + pitch * 0.8, cy - a + pitch * 0.8, pitch * 0.28, 0, 6.2832);
    g.fill();
    const label = (px: number) => `700 ${px}px "B612 Mono", monospace`;
    g.textBaseline = 'alphabetic';
    g.textAlign = 'left';
    g.font = label(Math.max(11 * k, a * 0.21));
    g.fillText('U1', cx - a, chipTop - pitch * 0.7);
    g.textAlign = 'center';
    g.font = label(Math.max(9 * k, a * 0.19));
    g.fillText(chipLabel, cx, cy + a * 0.82);
    if (mark && landscape) {
      g.textAlign = 'right';
      g.font = label(Math.max(11 * k, 0.72 * u));
      g.fillText(mark, W - spec.gutter, Math.max(nameTop, 90 * k));
    }
  } else {
    paintLayers();
  }

  function stroke(t: Trace, width: number, style: string) {
    g.strokeStyle = style;
    g.lineWidth = width;
    g.beginPath();
    t.points.forEach(([x, y], i) => (i ? g.lineTo(x, y) : g.moveTo(x, y)));
    g.stroke();
  }

  function paintLayers() {
    g.lineCap = 'round';
    g.lineJoin = 'round';

    // Pour first, then cut clearance around every piece of copper.
    g.fillStyle = 'rgb(120,0,0)';
    g.fillRect(0, 0, W, H);
    traces.forEach((t) => stroke(t, t.width + clear * 2, '#000'));
    g.fillStyle = '#000';
    pads.forEach((p) => { g.beginPath(); g.arc(p.x, p.y, p.r + clear, 0, 6.2832); g.fill(); });
    rects.forEach(([x, y, w, h]) => g.fillRect(x - clear, y - clear, w + clear * 2, h + clear * 2));

    // Stitching vias, only where the pour is clear of copper and of the text above it.
    const data = g.getImageData(0, 0, W, H).data;
    const open = (x: number, y: number) => {
      for (let i = 0; i < 8; i++) {
        const px = Math.round(x + Math.cos(i * 0.785) * u * 0.8);
        const py = Math.round(y + Math.sin(i * 0.785) * u * 0.8);
        if (px < 0 || py < 0 || px >= W || py >= H || data[(py * W + px) * 4] < 100) return false;
      }
      const inName = x < nameRight + 1.6 * u && y > nameTop - 1.6 * u && y < nameBottom + 1.6 * u;
      // Nothing is drilled through the printed board mark either.
      const onMark = mark !== '' && x > W - spec.gutter - 14 * u && y > nameTop - 3 * u && y < nameTop + 1.5 * u;
      return !inName && !onMark && !keepouts.some(([rx, ry, rw, rh]) => x > rx - u && x < rx + rw + u && y > ry - u && y < ry + rh + u);
    };
    const step = Math.max(6 * u, 150 * k);
    for (let y = step * 0.5, row = 0; y < H; y += step, row++) {
      for (let x = (row % 2) * step * 0.5 + step * 0.5; x < W; x += step) {
        if (open(x, y)) pads.push({ x, y, r: 0.3 * u, hole: 0.13 * u });
      }
    }

    g.globalCompositeOperation = 'lighter';
    traces.forEach((t) => stroke(t, t.width, '#f00'));
    g.fillStyle = '#f00';
    pads.forEach((p) => { g.beginPath(); g.arc(p.x, p.y, p.r, 0, 6.2832); g.fill(); });
    g.fillStyle = '#0f0';
    pads.forEach((p) => {
      g.beginPath();
      g.arc(p.x, p.y, p.r, 0, 6.2832);
      g.closePath();
      g.moveTo(p.x + p.hole, p.y);
      g.arc(p.x, p.y, p.hole, 0, 6.2832);
      g.closePath();
      g.fill('evenodd');
    });
    rects.forEach((r) => g.fillRect(...r));
  }

  return { canvas, netX: netX / k };
}

export interface BoardHandle {
  /** Horizontal position of the main net where it leaves the board, in CSS pixels. */
  netX: number;
  destroy(): void;
}

/** Hands the thread back to the browser between the expensive steps. */
const breathe = () => new Promise<void>((resolve) => setTimeout(resolve, 0));

/** Waits for the shaders without blocking. Asking for their status early would stall the page. */
async function programReady(gl: WebGL2RenderingContext, program: WebGLProgram) {
  const parallel = gl.getExtension('KHR_parallel_shader_compile');
  if (!parallel) return;
  const done = parallel.COMPLETION_STATUS_KHR as number;
  while (!gl.getProgramParameter(program, done)) await new Promise((resolve) => setTimeout(resolve, 24));
}

/** Starts the lit board in a section that has a canvas.board-canvas, or returns null without WebGL2. */
export async function mountBoard(section: HTMLElement, reduceMotion: boolean, isCancelled: () => boolean): Promise<BoardHandle | null> {
  const canvas = section.querySelector<HTMLCanvasElement>('canvas.board-canvas');
  if (!canvas) return null;
  const gl = canvas.getContext('webgl2', { alpha: false, antialias: false, powerPreference: 'low-power' });
  if (!gl) return null;

  const compile = (type: number, source: string) => {
    const shader = gl.createShader(type)!;
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    return shader;
  };
  const program = gl.createProgram()!;
  const vertex = compile(gl.VERTEX_SHADER, VERTEX);
  const fragment = compile(gl.FRAGMENT_SHADER, FRAGMENT);
  gl.attachShader(program, vertex);
  gl.attachShader(program, fragment);
  gl.linkProgram(program);
  await programReady(gl, program);
  if (isCancelled()) return null;
  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
    console.error(gl.getProgramInfoLog(program), gl.getShaderInfoLog(fragment));
    return null;
  }
  gl.useProgram(program);
  gl.bindVertexArray(gl.createVertexArray());

  const uniform = (name: string) => gl.getUniformLocation(program, name);
  const uLamp = uniform('Lamp');
  const uAspect = uniform('Aspect');
  const board = BOARDS[(section.dataset.board ?? 'green') as BoardColour];
  gl.uniform3f(uniform('Void'), ...hexToRgb(board.void));
  gl.uniform3f(uniform('Mask'), ...hexToRgb(board.mask));
  gl.uniform3f(uniform('Copper'), ...hexToRgb(board.cu));
  gl.uniform3f(uniform('Gold'), ...hexToRgb(board.trace));
  gl.uniform3f(uniform('Silk'), ...hexToRgb(board.silk));
  gl.uniform1f(uniform('Gain'), board.gain);

  gl.bindTexture(gl.TEXTURE_2D, gl.createTexture());
  gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
  // The map is painted at the size it is shown, so mipmaps would add cost and no quality.
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);

  const lamp = { x: -0.1, y: 0.55 };
  let aspect = 2;
  let netX = 0;

  const draw = () => {
    gl.uniform2f(uLamp, lamp.x, lamp.y);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
  };

  function rebuild() {
    const box = section.getBoundingClientRect();
    const k = Math.min(devicePixelRatio || 1, 1.75);
    const W = Math.max(2, Math.round(box.width * k));
    const H = Math.max(2, Math.round(box.height * k));
    canvas!.width = W;
    canvas!.height = H;
    aspect = W / H;
    gl!.viewport(0, 0, W, H);
    gl!.uniform1f(uAspect, aspect);

    const words = [...section.querySelectorAll<SVGSVGElement>('svg[data-word]')]
      .filter((svg) => !svg.closest('[data-keepout]'))
      .map((svg) => {
        const r = svg.getBoundingClientRect();
        const vb = svg.viewBox.baseVal;
        const unit = r.height / vb.height;
        return {
          text: svg.dataset.word ?? '',
          left: (r.left - box.left - vb.x * unit) * k,
          top: (r.top - box.top - vb.y * unit) * k,
          unit: unit * k,
        };
      });
    if (!words.length) return;

    const keepouts = [...section.querySelectorAll<HTMLElement>('[data-keepout]')].map((el): Rect => {
      const r = el.getBoundingClientRect();
      return [(r.left - box.left) * k, (r.top - box.top) * k, r.width * k, r.height * k];
    });

    const gutter = parseFloat(getComputedStyle(section).getPropertyValue('--gutter')) || Math.max(20, box.width * 0.05);
    const painted = paintMap({
      W,
      H,
      k,
      words,
      keepouts,
      chipLabel: section.dataset.chip ?? '',
      mark: section.dataset.mark ?? '',
      gutter: gutter * k,
    });
    netX = painted.netX;
    gl!.texImage2D(gl!.TEXTURE_2D, 0, gl!.RGBA, gl!.RGBA, gl!.UNSIGNED_BYTE, painted.canvas);
    draw();
  }

  /* The lamp follows the pointer, and drifts on its own when nothing is steering it. */
  let targetX: number | null = null;
  let targetY = 0.5;
  let lastInput = -1e9;
  let frame = 0;
  let running = false;
  let sweep = 0;
  let last = 0;

  const onPointer = (e: PointerEvent) => {
    if (e.pointerType === 'touch') return;
    const r = section.getBoundingClientRect();
    if (e.clientY < r.top || e.clientY > r.bottom) { targetX = null; return; }
    targetX = (e.clientX - r.left) / r.width;
    targetY = 1 - (e.clientY - r.top) / r.height;
    lastInput = performance.now();
    if (reduceMotion) { lamp.x = targetX; lamp.y = targetY; draw(); }
  };
  addEventListener('pointermove', onPointer, { passive: true });

  const tick = (now: number) => {
    const dt = Math.min((now - last) / 1000, 0.05);
    last = now;
    const t = now / 1000;
    let goalX: number;
    let goalY: number;
    if (targetX !== null && now - lastInput < 6000) {
      goalX = targetX;
      goalY = targetY;
    } else if (sweep < 1) {
      sweep = Math.min(1, sweep + dt / 2.4);
      const e = 1 - Math.pow(1 - sweep, 3);
      goalX = -0.1 + e * 0.72;
      goalY = 0.52 + Math.sin(e * 3.1) * 0.1;
    } else {
      goalX = 0.5 + 0.42 * Math.sin(t * 0.3);
      goalY = 0.5 + 0.3 * Math.sin(t * 0.43 + 1);
    }
    const rate = 1 - Math.exp(-dt * (targetX !== null ? 9 : 2.6));
    lamp.x += (goalX - lamp.x) * rate;
    lamp.y += (goalY - lamp.y) * rate;
    draw();
    if (running) frame = requestAnimationFrame(tick);
  };

  const setRunning = (on: boolean) => {
    if (reduceMotion || on === running) return;
    running = on;
    if (on) { last = performance.now(); frame = requestAnimationFrame(tick); }
    else cancelAnimationFrame(frame);
  };

  const visible = new IntersectionObserver((entries) => setRunning(entries[entries.length - 1].isIntersecting));
  await breathe();
  if (isCancelled()) {
    removeEventListener('pointermove', onPointer);
    return null;
  }
  rebuild();
  if (reduceMotion) { lamp.x = 0.32; lamp.y = 0.58; draw(); }
  visible.observe(section);

  const onVisibility = () => setRunning(!document.hidden && section.getBoundingClientRect().bottom > 0);
  document.addEventListener('visibilitychange', onVisibility);

  let resizeTimer = 0;
  let width = innerWidth;
  const onResize = () => {
    if (innerWidth === width) return; // Mobile toolbars change the height. The board does not need to redraw.
    width = innerWidth;
    clearTimeout(resizeTimer);
    resizeTimer = window.setTimeout(rebuild, 160);
  };
  addEventListener('resize', onResize, { passive: true });

  return {
    get netX() { return netX; },
    destroy() {
      setRunning(false);
      clearTimeout(resizeTimer);
      visible.disconnect();
      removeEventListener('pointermove', onPointer);
      removeEventListener('resize', onResize);
      document.removeEventListener('visibilitychange', onVisibility);
      gl.getExtension('WEBGL_lose_context')?.loseContext();
    },
  };
}

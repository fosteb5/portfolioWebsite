/**
 * The main net: one route that leaves U1 in the hero and runs through every section.
 * Each section draws its own stretch, so nothing tall has to repaint while scrolling.
 * Routes are octilinear and are rebuilt whenever the layout changes.
 */

/** Half the page gutter. Measured, because --gutter is a clamp() rather than a number. */
const LANE_LEFT = () => {
  const wrap = document.querySelector('.wrap');
  const gutter = wrap ? parseFloat(getComputedStyle(wrap).paddingLeft) : 40;
  return Math.max(10, gutter * 0.5);
};

/** Builds path data, rounding each corner into a 45 degree chamfer. */
function chamfer(points: [number, number][], size = 18) {
  let d = `M${points[0][0]} ${points[0][1]}`;
  for (let i = 1; i < points.length - 1; i++) {
    const [px, py] = points[i - 1];
    const [x, y] = points[i];
    const [nx, ny] = points[i + 1];
    const inLen = Math.hypot(x - px, y - py);
    const outLen = Math.hypot(nx - x, ny - y);
    const c = Math.min(size, inLen / 2, outLen / 2);
    d += `L${x - ((x - px) / inLen) * c} ${y - ((y - py) / inLen) * c}L${x + ((nx - x) / outLen) * c} ${y + ((ny - y) / outLen) * c}`;
  }
  const [ex, ey] = points[points.length - 1];
  return `${d}L${ex} ${ey}`;
}

// pathLength="1" lets scroll drive the stroke as a plain 0 to 1, however long the route becomes.
function setRoute(svg: SVGSVGElement, d: string) {
  const live = svg.querySelector('.net-live');
  if (live) {
    svg.querySelector('.net-base')?.setAttribute('d', d);
    live.setAttribute('d', d);
    return;
  }
  svg.innerHTML = `<path class="net-base" d="${d}"/><path class="net-live" pathLength="1" d="${d}"/>`;
}

/** Position inside a section, ignoring transforms so entrance animations cannot skew a route. */
const offset = (el: Element, parent: Element) => {
  if (el instanceof HTMLElement) {
    let x = 0;
    let y = 0;
    let node: HTMLElement | null = el;
    while (node && node !== parent && parent.contains(node)) {
      x += node.offsetLeft;
      y += node.offsetTop;
      node = node.offsetParent as HTMLElement | null;
    }
    return { x, y, w: el.offsetWidth, h: el.offsetHeight };
  }
  const a = el.getBoundingClientRect();
  const b = parent.getBoundingClientRect();
  return { x: a.left - b.left, y: a.top - b.top, w: a.width, h: a.height };
};

export interface Nets {
  about?: SVGSVGElement;
  toolbox?: SVGSVGElement;
  experience?: SVGSVGElement;
  resume?: SVGSVGElement;
  contact?: SVGSVGElement;
}

export function collectNets(): Nets {
  const get = (id: string) => document.querySelector<SVGSVGElement>(`#${id} > svg[data-net]`) ?? undefined;
  return { about: get('about'), toolbox: get('toolbox'), experience: get('experience'), resume: get('resume'), contact: get('contact') };
}

/** Lays out every stretch of the net from the current page geometry. */
export function routeNets(nets: Nets, entryX: number) {
  const laneL = LANE_LEFT();
  const clientW = document.documentElement.clientWidth;
  const laneR = clientW - laneL;
  const x0 = Math.min(entryX || laneR, clientW - 8);

  if (nets.about) {
    const section = nets.about.parentElement!;
    const h = section.offsetHeight;
    const title = section.querySelector('.about-title');
    const t = title ? offset(title, section) : { x: laneL * 2, y: 120, w: 0, h: 0 };
    const y = Math.max(40, t.y - 34);
    setRoute(nets.about, chamfer([[x0, 0], [x0, y], [laneL, y], [laneL, h]], 22));
  }

  if (nets.toolbox) {
    const section = nets.toolbox.parentElement!;
    const chip = section.querySelector('[data-chip]');
    const c = chip ? offset(chip, section) : { x: clientW / 2, y: 120, w: 0, h: 0 };
    const cx = c.x + c.w / 2;
    // On narrow screens the heading sits above the chip, so the route slips in beneath it.
    const stacked = clientW < 1024;
    const y = stacked ? c.y - 14 : Math.max(24, c.y - 44);
    setRoute(nets.toolbox, chamfer([[laneR, 0], [laneR, y], [cx, y], [cx, c.y + 2]], stacked ? 10 : 22));
  }

  if (nets.experience) {
    const section = nets.experience.parentElement!;
    setRoute(nets.experience, `M${laneL} 0V${section.offsetHeight}`);
  }

  if (nets.resume) {
    const section = nets.resume.parentElement!;
    const pad = section.querySelector('[data-test-point]');
    const p = pad ? offset(pad, section) : { x: clientW * 0.7, y: 80, w: 200, h: 200 };
    const cx = p.x + p.w / 2;
    const h = section.offsetHeight;
    const y = Math.max(30, p.y - 40);
    setRoute(nets.resume, chamfer([[laneL, 0], [laneL, y], [cx, y], [cx, h]], 22));
    nets.resume.dataset.exitX = String(cx);
    nets.resume.dataset.height = String(h);
  }

  if (nets.contact) {
    const section = nets.contact.parentElement!;
    const row = section.querySelector('.connector');
    const c = row ? offset(row, section) : { x: 0, y: section.offsetHeight - 240, w: clientW, h: 0 };
    const exit = Number(nets.resume?.dataset.exitX) || laneR;
    // Down the right-hand lane, clear of the heading, then along into J1.
    const y = c.y + 8;
    const target = c.x + c.w - 90;
    setRoute(nets.contact, chamfer([[exit, 0], [exit, 28], [laneR, 28], [laneR, y], [target, y], [target, y + 22]], 18));
  }
}

/** The chip's fan-out to each toolbox group. Outer groups turn first, so nothing crosses. */
export function routeFan(section: HTMLElement) {
  const fan = section.querySelector<SVGSVGElement>('[data-fan]');
  const pins = [...section.querySelectorAll<SVGRectElement>('[data-pin]')];
  const pads = [...section.querySelectorAll<HTMLElement>('[data-group-pad]')];
  if (!fan || !pads.length || !pins.length || fan.getBoundingClientRect().width === 0) return;

  const box = fan.getBoundingClientRect();
  const count = pads.length;
  const middle = (count - 1) / 2;
  const step = Math.floor(pins.length / (count + 1));
  const span = box.height;
  const paths: string[] = [];

  pads.forEach((pad, i) => {
    const pin = pins[step * (i + 1)].getBoundingClientRect();
    const target = pad.getBoundingClientRect();
    const x1 = pin.left + pin.width / 2 - box.left;
    const y1 = pin.bottom - box.top;
    const x2 = target.left + target.width / 2 - box.left;
    const y2 = target.top - box.top;
    const rank = Math.abs(i - middle) / Math.max(middle, 1);
    const turn = y1 + (y2 - y1) * (0.62 - rank * 0.34);
    paths.push(chamfer([[x1, y1], [x1, turn], [x2, turn], [x2, y2]], Math.min(16, span * 0.16)));
  });

  fan.innerHTML = paths.map((d) => `<path d="${d}"/>`).join('');
}

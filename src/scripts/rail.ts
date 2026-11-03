import { drawTrace, prefersReducedMotion, whenIdle } from './motion';

/**
 * The projects carousel. The strip is a native horizontal scroller that snaps each board to the centre,
 * so touch, trackpads and Shift with the wheel work as they do anywhere else, and the page scrolls straight past.
 * This adds the arrow pads, the via navigator, arrow keys, dragging with a mouse, a slight parallax inside each
 * board's window, and the trace lettering that draws the first time each board comes into view.
 */
export function initRail(section: HTMLElement) {
  const view = section.querySelector<HTMLElement>('[data-rail-view]');
  const modules = Array.from(section.querySelectorAll<HTMLElement>('[data-module]'));
  if (!view || !modules.length) return () => undefined;

  const vias = Array.from(section.querySelectorAll<HTMLButtonElement>('[data-rail-go]'));
  const steps = Array.from(section.querySelectorAll<HTMLButtonElement>('[data-rail-step]'));
  const count = section.querySelector('[data-rail-count]');
  const live = section.querySelector('[data-rail-live]');
  const bus = section.querySelector<HTMLElement>('[data-rail-bus]');
  const fill = section.querySelector<HTMLElement>('[data-rail-fill]');
  const signal = section.querySelector<HTMLElement>('[data-rail-signal]');
  const arts = modules.map((module) => module.querySelector<HTMLElement>('[data-module-art]'));
  const reduce = prefersReducedMotion();
  const wide = matchMedia('(min-width: 1024px)');
  // Set up when the section comes near, not at load: measuring every stroke of seven names is slow on a phone.
  let draws: (ReturnType<typeof drawTrace> | null)[] = [];
  let cancelIdle = () => undefined as void;
  const prepareDraws = () => {
    if (reduce || draws.length) return;
    draws = modules.map((module, i) => {
      const name = module.querySelector('.module-name');
      // The board already in view keeps its name; the rest wait to draw when they arrive.
      return name && i !== active ? drawTrace(name, 0.8).pause() : null;
    });
  };

  let active = -1;
  let onScreen = false;
  let announced = false;

  const centreOf = (module: HTMLElement) => module.offsetLeft + module.offsetWidth / 2;
  const nearest = () => {
    const mid = view.scrollLeft + view.clientWidth / 2;
    let best = 0;
    modules.forEach((module, i) => {
      if (Math.abs(centreOf(module) - mid) < Math.abs(centreOf(modules[best]) - mid)) best = i;
    });
    return best;
  };

  /* The gold signal rides the bus to the via of the board in view, and the trace fills up to it. */
  const placeSignal = () => {
    const dot = vias[active]?.querySelector('i');
    if (!dot || !bus || !signal || !fill) return;
    const x = dot.getBoundingClientRect().left + dot.offsetWidth / 2 - bus.getBoundingClientRect().left;
    signal.style.transform = `translateX(${x - signal.offsetWidth / 2}px)`;
    fill.style.transform = `scaleX(${x / bus.clientWidth})`;
  };

  const setActive = (i: number) => {
    if (i === active) return;
    const first = active === -1;
    active = i;
    vias.forEach((via, k) => (k === i ? via.setAttribute('aria-current', 'true') : via.removeAttribute('aria-current')));
    if (count) count.textContent = String(i + 1).padStart(2, '0');
    if (live && !first && announced) live.textContent = `Showing ${modules[i].getAttribute('aria-label')}`;
    placeSignal();
    if (onScreen) draws[i]?.play();
  };

  const go = (i: number) => {
    const n = modules.length;
    const target = modules[((i % n) + n) % n];
    announced = true;
    view.scrollTo({ left: centreOf(target) - view.clientWidth / 2, behavior: reduce ? 'auto' : 'smooth' });
  };

  /* Scrolling: pick the board in view, and drift each window's picture against its board on wide screens. */
  let frame = 0;
  const onScroll = () => {
    if (frame) return;
    frame = requestAnimationFrame(() => {
      frame = 0;
      setActive(nearest());
      if (reduce || !wide.matches) return;
      const mid = view.scrollLeft + view.clientWidth / 2;
      modules.forEach((module, k) => {
        const art = arts[k];
        if (art) art.style.transform = `translateX(${(((mid - centreOf(module)) / view.clientWidth) * 26).toFixed(1)}px)`;
      });
    });
  };
  const onWide = () => {
    if (!wide.matches) arts.forEach((art) => art && (art.style.transform = ''));
    onScroll();
  };

  const onStep = (e: Event) => go(active + Number((e.currentTarget as HTMLElement).dataset.railStep));
  const onVia = (e: Event) => go(Number((e.currentTarget as HTMLElement).dataset.railGo));
  const onKey = (e: KeyboardEvent) => {
    if ((e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') || e.altKey || e.ctrlKey || e.metaKey) return;
    e.preventDefault();
    go(active + (e.key === 'ArrowRight' ? 1 : -1));
  };

  /*
   * Sideways wheel, from a trackpad swipe or Shift with a mouse wheel, moves one board per gesture.
   * Left to the browser, mandatory snapping pulls short wheel steps back to the same board. Vertical wheel
   * is left alone so the page scrolls straight past.
   */
  let wheelSum = 0;
  let wheelUsed = false;
  let wheelIdle = 0;
  const onWheel = (e: WheelEvent) => {
    const dx = Math.abs(e.deltaX) > Math.abs(e.deltaY) ? e.deltaX : e.shiftKey ? e.deltaY : 0;
    if (!dx) return;
    e.preventDefault();
    e.stopPropagation(); // keep the page's smooth scrolling from also moving the page
    clearTimeout(wheelIdle);
    wheelIdle = window.setTimeout(() => {
      wheelSum = 0;
      wheelUsed = false;
    }, 180);
    if (wheelUsed) return;
    wheelSum += dx;
    if (Math.abs(wheelSum) < 30) return;
    wheelUsed = true;
    go(active + Math.sign(wheelSum));
  };

  /* Dragging with a mouse. The pointer is only captured once it has moved, so a plain click on a link still works. */
  let drag: { id: number; x: number; left: number; from: number; moved: boolean } | null = null;
  let swallowClick = false;
  const onDown = (e: PointerEvent) => {
    if (e.pointerType !== 'mouse' || e.button !== 0 || (e.target as Element).closest('button')) return;
    drag = { id: e.pointerId, x: e.clientX, left: view.scrollLeft, from: active, moved: false };
  };
  const onMove = (e: PointerEvent) => {
    if (!drag || e.pointerId !== drag.id) return;
    const dx = e.clientX - drag.x;
    if (!drag.moved) {
      if (Math.abs(dx) < 6) return;
      drag.moved = true;
      view.classList.add('is-dragging');
      view.setPointerCapture(e.pointerId);
    }
    view.scrollLeft = drag.left - dx;
  };
  const onUp = (e: PointerEvent) => {
    if (!drag || e.pointerId !== drag.id) return;
    const { moved, x, from } = drag;
    drag = null;
    if (!moved) return;
    view.classList.remove('is-dragging');
    swallowClick = true;
    setTimeout(() => (swallowClick = false), 0);
    // A flick moves one board on even if it didn't get halfway; otherwise settle on the nearest.
    const dx = e.clientX - x;
    const i = nearest();
    go(i === from && Math.abs(dx) > 60 ? i - Math.sign(dx) : i);
  };
  const onClick = (e: MouseEvent) => {
    if (!swallowClick) return;
    e.preventDefault();
    e.stopPropagation();
  };
  const noDragGhost = (e: DragEvent) => e.preventDefault();

  /* Load every board's picture once the section is near, and start the lettering when it is on screen. */
  const near = new IntersectionObserver(([entry]) => {
    if (!entry.isIntersecting) return;
    section.querySelectorAll('img').forEach((img) => (img.loading = 'eager'));
    cancelIdle = whenIdle(prepareDraws);
    near.disconnect();
  }, { rootMargin: '100% 0px' });
  const seen = new IntersectionObserver(([entry]) => {
    if (!entry.isIntersecting) return;
    onScreen = true;
    seen.disconnect();
  }, { threshold: 0.3 });
  const resized = new ResizeObserver(() => placeSignal());

  view.addEventListener('scroll', onScroll, { passive: true });
  view.addEventListener('keydown', onKey);
  view.addEventListener('wheel', onWheel, { passive: false });
  view.addEventListener('pointerdown', onDown);
  view.addEventListener('pointermove', onMove);
  view.addEventListener('pointerup', onUp);
  view.addEventListener('pointercancel', onUp);
  view.addEventListener('dragstart', noDragGhost);
  window.addEventListener('click', onClick, true);
  wide.addEventListener('change', onWide);
  steps.forEach((button) => button.addEventListener('click', onStep));
  vias.forEach((button) => button.addEventListener('click', onVia));
  near.observe(section);
  seen.observe(section);
  if (bus) resized.observe(bus);
  setActive(nearest());
  onScroll();

  return () => {
    cancelAnimationFrame(frame);
    clearTimeout(wheelIdle);
    cancelIdle();
    view.removeEventListener('scroll', onScroll);
    view.removeEventListener('keydown', onKey);
    view.removeEventListener('wheel', onWheel);
    view.removeEventListener('pointerdown', onDown);
    view.removeEventListener('pointermove', onMove);
    view.removeEventListener('pointerup', onUp);
    view.removeEventListener('pointercancel', onUp);
    view.removeEventListener('dragstart', noDragGhost);
    window.removeEventListener('click', onClick, true);
    wide.removeEventListener('change', onWide);
    steps.forEach((button) => button.removeEventListener('click', onStep));
    vias.forEach((button) => button.removeEventListener('click', onVia));
    near.disconnect();
    seen.disconnect();
    resized.disconnect();
    draws.forEach((draw) => draw?.kill());
  };
}

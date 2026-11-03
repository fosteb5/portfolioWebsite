import { gsap, prefersReducedMotion } from './motion';
import { getLenis } from './scroll';

/**
 * Page transition: opening a project drops you through a via.
 * A gold-ringed disc of the next board grows from where you clicked. The page swaps
 * behind it, then a hole opens in the disc and the new layer shows through.
 */

const GOLD = '#E2B65A';
const RING = 12;

let origin = { x: 0, y: 0 };
let colour = '#0C4A3A';
let armed = false;

const radius = (x: number, y: number) =>
  Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y)) + RING + 4;

function paintDisc(el: HTMLElement, r: number) {
  el.style.background = `radial-gradient(circle at ${origin.x}px ${origin.y}px, ${colour} ${r}px, ${GOLD} ${r}px, ${GOLD} ${r + RING}px, transparent ${r + RING + 0.5}px)`;
}

function paintHole(el: HTMLElement, r: number) {
  el.style.background = `radial-gradient(circle at ${origin.x}px ${origin.y}px, transparent ${r}px, ${GOLD} ${r + 0.5}px, ${GOLD} ${r + RING}px, ${colour} ${r + RING + 0.5}px)`;
}

function tween(duration: number, ease: string, onUpdate: (value: number) => void, to: number) {
  return new Promise<void>((resolve) => {
    const state = { value: 0 };
    gsap.to(state, { value: to, duration, ease, onUpdate: () => onUpdate(state.value), onComplete: resolve });
  });
}

export function initTransitions() {
  const via = document.getElementById('via');
  if (!via) return;

  document.addEventListener('click', (e) => {
    const link = (e.target as Element).closest<HTMLElement>('a[href]');
    armed = false;
    if (!link || prefersReducedMotion()) return;
    const to = link.getAttribute('href') ?? '';
    if (!to.startsWith('/') || to.startsWith('/#') || to.endsWith('.pdf')) {
      if (!link.dataset.via) return;
    }
    origin = { x: e.clientX || innerWidth / 2, y: e.clientY || innerHeight / 2 };
    colour = link.dataset.via ?? '#0C4A3A';
    armed = true;
  }, true);

  document.addEventListener('astro:before-preparation', (event) => {
    const e = event as Event & { loader: () => Promise<void>; navigationType: string };
    if (!armed || e.navigationType === 'traverse') return;
    const load = e.loader;
    e.loader = async () => {
      getLenis()?.stop();
      via.style.visibility = 'visible';
      paintDisc(via, 0);
      const cover = tween(0.62, 'power3.inOut', (r) => paintDisc(via, r), radius(origin.x, origin.y));
      await Promise.all([cover, load()]);
    };
  });

  document.addEventListener('astro:page-load', () => {
    getLenis()?.start();
    if (!armed) return;
    armed = false;
    tween(0.72, 'power3.inOut', (r) => paintHole(via, r), radius(origin.x, origin.y)).then(() => {
      via.style.visibility = 'hidden';
      via.style.background = 'none';
    });
  });
}

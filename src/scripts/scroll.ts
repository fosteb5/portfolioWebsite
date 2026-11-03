import Lenis from 'lenis';
import { gsap, ScrollTrigger } from './motion';

let lenis: Lenis | null = null;

export const getLenis = () => lenis;

/** Moves to a section, and takes keyboard focus there so tabbing continues from it. */
export function goTo(target: HTMLElement, immediate = false) {
  // A pinned section reports its pinned position, so aim for the spacer that holds its place.
  const spacer = target.closest<HTMLElement>('.pin-spacer');
  // Lenis measures the page lazily, so refresh it in case this page was only just swapped in.
  lenis?.resize();
  // A pin has to start exactly at the top, so cancel the scroll padding Lenis would leave for the nav.
  const padding = spacer ? parseFloat(getComputedStyle(document.documentElement).scrollPaddingBlockStart) || 0 : 0;
  lenis?.scrollTo(spacer ?? target, { immediate, force: true, duration: 1.5, offset: padding });
  if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
  target.focus({ preventScroll: true });
}

function onClick(event: MouseEvent) {
  const link = (event.target as Element).closest<HTMLAnchorElement>('a[href*="#"]');
  if (!link || event.defaultPrevented || event.metaKey || event.ctrlKey || event.shiftKey) return;
  const url = new URL(link.href);
  if (url.pathname !== location.pathname || !url.hash) return;
  const target = document.getElementById(url.hash.slice(1));
  if (!target) return;
  event.preventDefault();
  history.pushState(history.state, '', url.hash);
  goTo(target);
}

export function initScroll() {
  if (lenis) return;
  lenis = new Lenis({ autoRaf: false, lerp: 0.12 });
  lenis.on('scroll', ScrollTrigger.update);
  gsap.ticker.add((time) => lenis?.raf(time * 1000));
  gsap.ticker.lagSmoothing(0);
  // Capture phase, so this runs before the page router sees the click.
  document.addEventListener('click', onClick, true);
  document.addEventListener('astro:after-swap', () => {
    lenis?.scrollTo(0, { immediate: true, force: true });
    lenis?.resize();
  });
}

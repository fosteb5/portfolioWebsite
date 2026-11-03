import { gsap } from 'gsap';
import { DrawSVGPlugin } from 'gsap/DrawSVGPlugin';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { SplitText } from 'gsap/SplitText';

gsap.registerPlugin(ScrollTrigger, DrawSVGPlugin, SplitText);
gsap.defaults({ ease: 'expo.out', duration: 1 });

export { gsap, ScrollTrigger, SplitText };

export const prefersReducedMotion = () => matchMedia('(prefers-reduced-motion: reduce)').matches;
export const hasFinePointer = () => matchMedia('(hover: hover) and (pointer: fine)').matches;

/** Runs work after the browser has painted, so it never holds up the first frame. */
export function whenIdle(work: () => void, timeout = 1200): () => void {
  if ('requestIdleCallback' in window) {
    const id = requestIdleCallback(work, { timeout });
    return () => cancelIdleCallback(id);
  }
  const id = setTimeout(work, 200);
  return () => clearTimeout(id);
}

/** Copper draws along its strokes, then the pads land. Returns a paused-ready timeline. */
export function drawTrace(root: Element, duration = 1.1) {
  const strokes = gsap.utils.toArray<SVGPathElement>(root.querySelectorAll('.tr'));
  const pads = gsap.utils.toArray<SVGCircleElement>(root.querySelectorAll('.tr-pad'));
  const halo = root.querySelectorAll('.tr-halo');
  const tl = gsap.timeline();
  if (halo.length) tl.from(halo, { autoAlpha: 0, duration: 0.5, ease: 'none' }, 0);
  tl.fromTo(strokes, { drawSVG: '0%' }, { drawSVG: '100%', duration, ease: 'power2.inOut', stagger: { amount: 0.5 } }, 0);
  if (pads.length) {
    tl.from(pads, { autoAlpha: 0, scale: 0.4, transformOrigin: '50% 50%', duration: 0.5, stagger: { amount: 0.4 } }, 0.45);
  }
  return tl;
}

import { gsap, hasFinePointer, prefersReducedMotion } from './motion';

const INTERACTIVE = 'a, button, input, [role="button"], [data-module]';

/** The inspection lamp: a ring that replaces the pointer and a pool of light under the page. */
export function initCursor() {
  const root = document.documentElement;
  const cursor = document.getElementById('cursor');
  const lamp = document.getElementById('lamp');
  if (!cursor || !lamp || !hasFinePointer()) return;

  const ring = cursor.querySelector<HTMLElement>('.cursor-ring')!;
  const dot = cursor.querySelector<HTMLElement>('.cursor-dot')!;
  const reduce = prefersReducedMotion();
  const lag = reduce ? 0 : 0.3;

  const dotX = gsap.quickSetter(dot, 'x', 'px');
  const dotY = gsap.quickSetter(dot, 'y', 'px');
  const ringX = gsap.quickTo(ring, 'x', { duration: lag, ease: 'power3' });
  const ringY = gsap.quickTo(ring, 'y', { duration: lag, ease: 'power3' });
  const lampX = gsap.quickTo(lamp, 'x', { duration: reduce ? 0 : 0.7, ease: 'power3' });
  const lampY = gsap.quickTo(lamp, 'y', { duration: reduce ? 0 : 0.7, ease: 'power3' });

  let magnet: HTMLElement | null = null;

  addEventListener('pointermove', (e) => {
    if (e.pointerType === 'touch') return;
    if (!root.classList.contains('has-cursor')) {
      root.classList.add('has-cursor');
      root.setAttribute('data-lamp', '');
    }
    dotX(e.clientX);
    dotY(e.clientY);
    ringX(e.clientX);
    ringY(e.clientY);
    lampX(e.clientX);
    lampY(e.clientY);
    if (reduce) return;

    const near = (e.target as Element).closest?.<HTMLElement>('[data-magnetic]') ?? null;
    if (magnet && magnet !== near) release(magnet);
    magnet = near;
    if (near) {
      const r = near.getBoundingClientRect();
      const x = Number(gsap.getProperty(near, 'x')) || 0;
      const y = Number(gsap.getProperty(near, 'y')) || 0;
      const dx = e.clientX - (r.left - x + r.width / 2);
      const dy = e.clientY - (r.top - y + r.height / 2);
      gsap.to(near, { x: dx * 0.24, y: dy * 0.3, duration: 0.5, ease: 'power3.out', overwrite: 'auto' });
    }
  }, { passive: true });

  function release(el: HTMLElement) {
    gsap.to(el, { x: 0, y: 0, duration: 0.7, ease: 'elastic.out(1, 0.45)', overwrite: 'auto' });
  }

  document.addEventListener('pointerover', (e) => {
    const hot = (e.target as Element).closest?.(INTERACTIVE);
    gsap.to(ring, { scale: hot ? 1.5 : 1, duration: 0.24, ease: 'power3.out', overwrite: 'auto' });
  });

  document.addEventListener('mouseleave', () => root.classList.remove('has-cursor'));
  addEventListener('pointerdown', () => gsap.to(ring, { scale: 0.85, duration: 0.12, overwrite: 'auto' }));
  addEventListener('pointerup', () => gsap.to(ring, { scale: 1, duration: 0.3, overwrite: 'auto' }));
}

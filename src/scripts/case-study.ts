import { startBoard } from './home';
import { drawTrace, gsap, prefersReducedMotion, ScrollTrigger, SplitText } from './motion';

export function initCaseStudy() {
  const reduce = prefersReducedMotion();
  const hero = document.querySelector<HTMLElement>('.case-hero')!;
  const name = hero.querySelector<HTMLElement>('.case-name')!;

  const ctx = gsap.context(() => {
    gsap.set(name.querySelector('.trace-art'), { visibility: 'visible' });
    if (!reduce) drawTrace(name, 1.1);
  });
  const stopBoard = startBoard(hero, () => undefined);

  /* Keep the index beside the text in step with the section being read. */
  const links = gsap.utils.toArray<HTMLAnchorElement>('[data-index-link]');
  const triggers = gsap.utils.toArray<HTMLElement>('[data-case-sec]').map((section, i) =>
    ScrollTrigger.create({
      trigger: section,
      start: 'top 45%',
      end: 'bottom 45%',
      onToggle: (self) => {
        if (self.isActive) links.forEach((link, n) => (n === i ? link.setAttribute('aria-current', 'true') : link.removeAttribute('aria-current')));
      },
    }),
  );

  const mm = gsap.matchMedia();
  mm.add('(prefers-reduced-motion: no-preference)', () => {
    gsap.to(hero.querySelector('.board-canvas'), { yPercent: 12, ease: 'none', scrollTrigger: { trigger: hero, start: 'top top', end: 'bottom top', scrub: true } });

    /* Section headings route themselves as they arrive. */
    gsap.utils.toArray<HTMLElement>('.case-h').forEach((heading) => {
      gsap.timeline({ scrollTrigger: { trigger: heading, start: 'top 84%', once: true } }).add(drawTrace(heading, 0.7));
    });

    /* Large statements arrive line by line. */
    const splits = gsap.utils.toArray<HTMLElement>('.case-big').map((text) =>
      SplitText.create(text, {
        type: 'lines',
        mask: 'lines',
        autoSplit: true,
        aria: 'none',
        onSplit: (self) => gsap.from(self.lines, { yPercent: 105, duration: 1, stagger: 0.09, scrollTrigger: { trigger: text, start: 'top 86%', once: true } }),
      }),
    );

    gsap.utils.toArray<HTMLElement>('.case-steps, .case-results, .bom').forEach((list) => {
      gsap.from(list.children, { autoAlpha: 0, y: 22, duration: 0.8, stagger: 0.09, scrollTrigger: { trigger: list, start: 'top 84%', once: true } });
    });

    gsap.utils.toArray<HTMLElement>('.dg-edge').forEach((edge) => {
      gsap.fromTo(edge, { drawSVG: '0%' }, { drawSVG: '100%', duration: 1, ease: 'power2.inOut', scrollTrigger: { trigger: edge.closest('.case-diagram'), start: 'top 78%', once: true } });
    });

    /* Figures open like a mask being lifted, and photos drift a little inside the frame. */
    gsap.utils.toArray<HTMLElement>('.layer .media-frame').forEach((frame) => {
      gsap.fromTo(frame, { clipPath: 'inset(0 0 100% 0)' }, { clipPath: 'inset(0 0 0% 0)', duration: 1.3, ease: 'expo.inOut', clearProps: 'clipPath', scrollTrigger: { trigger: frame, start: 'top 88%', once: true } });
      const photo = frame.querySelector('[data-parallax]');
      if (photo) {
        gsap.fromTo(photo, { yPercent: -6, scale: 1.14 }, { yPercent: 6, ease: 'none', scrollTrigger: { trigger: frame, start: 'top bottom', end: 'bottom top', scrub: true } });
      }
    });

    return () => splits.forEach((split) => split.revert());
  });

  return () => {
    stopBoard();
    triggers.forEach((trigger) => trigger.kill());
    mm.revert();
    ctx.revert();
  };
}

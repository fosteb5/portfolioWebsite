import { startBoard } from './home';
import { drawTrace, gsap, prefersReducedMotion, ScrollTrigger, SplitText } from './motion';
import { initSequence } from './sequence';

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
    /* Rendered scroll animations, set up first so nothing below can stop them. With reduced motion they stay as their finished still. */
    const sequences = gsap.utils.toArray<HTMLElement>('[data-seq]').map(initSequence);

    gsap.to(hero.querySelector('.board-canvas'), { yPercent: 12, ease: 'none', scrollTrigger: { trigger: hero, start: 'top top', end: 'bottom top', scrub: true } });

    /* Section headings route themselves as they arrive. */
    gsap.utils.toArray<HTMLElement>('.case-h').forEach((heading) => {
      gsap.timeline({ scrollTrigger: { trigger: heading, start: 'top 84%', toggleActions: 'play none none none' } }).add(drawTrace(heading, 0.7));
    });

    /*
     * Large statements arrive line by line. Each one gets a single trigger, made once, because autoSplit re-splits
     * when fonts load.
     *
     * Reveals play once with toggleActions rather than `once: true`. A `once` trigger kills itself when the page
     * is reloaded below it, and doing that while a newer trigger is still being set up crashed ScrollTrigger.
     */
    const splits = gsap.utils.toArray<HTMLElement>('.case-big').map((text) => {
      let reveal: gsap.core.Tween | undefined;
      let arrived = false;
      const split = SplitText.create(text, {
        type: 'lines',
        mask: 'lines',
        autoSplit: true,
        aria: 'none',
        onSplit: (self) => {
          reveal = gsap.from(self.lines, { yPercent: 105, duration: 1, stagger: 0.09, paused: true });
          if (arrived) reveal.progress(1);
          return reveal;
        },
      });
      ScrollTrigger.create({ trigger: text, start: 'top 86%', onEnter: () => { arrived = true; reveal?.play(); } });
      return split;
    });

    gsap.utils.toArray<HTMLElement>('.case-steps, .case-results, .bom').forEach((list) => {
      gsap.from(list.children, { autoAlpha: 0, y: 22, duration: 0.8, stagger: 0.09, scrollTrigger: { trigger: list, start: 'top 84%', toggleActions: 'play none none none' } });
    });

    gsap.utils.toArray<HTMLElement>('.dg-edge').forEach((edge) => {
      gsap.fromTo(edge, { drawSVG: '0%' }, { drawSVG: '100%', duration: 1, ease: 'power2.inOut', scrollTrigger: { trigger: edge.closest('.case-diagram'), start: 'top 78%', toggleActions: 'play none none none' } });
    });

    /* Figures open like a mask being lifted, and photos drift a little inside the frame. */
    gsap.utils.toArray<HTMLElement>('.layer .media-frame').forEach((frame) => {
      gsap.fromTo(frame, { clipPath: 'inset(0 0 100% 0)' }, { clipPath: 'inset(0 0 0% 0)', duration: 1.3, ease: 'expo.inOut', clearProps: 'clipPath', scrollTrigger: { trigger: frame, start: 'top 88%', toggleActions: 'play none none none' } });
      const photo = frame.querySelector('[data-parallax]');
      if (photo) {
        gsap.fromTo(photo, { yPercent: -6, scale: 1.14 }, { yPercent: 6, ease: 'none', scrollTrigger: { trigger: frame, start: 'top bottom', end: 'bottom top', scrub: true } });
      }
    });

    return () => {
      splits.forEach((split) => split.revert());
      sequences.forEach((stop) => stop());
    };
  });

  return () => {
    stopBoard();
    triggers.forEach((trigger) => trigger.kill());
    mm.revert();
    ctx.revert();
  };
}

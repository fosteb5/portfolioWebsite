import { drawTrace, gsap, prefersReducedMotion, ScrollTrigger, SplitText, whenIdle } from './motion';
import { collectNets, routeFan, routeNets } from './net';
import { getLenis } from './scroll';

const DESKTOP = '(min-width: 1024px)';

/**
 * Brings up the WebGL board once the name has finished routing, then crossfades from the SVG.
 * Waiting keeps the entrance smooth: nothing heavy runs while the letters draw.
 */
function startBoard(section: HTMLElement, onReady: (netX: number) => void) {
  const canvas = section.querySelector<HTMLCanvasElement>('canvas.board-canvas');
  const reduce = prefersReducedMotion();
  let destroyed = false;
  let handle: { destroy(): void } | null = null;
  let cancelIdle = () => undefined as void;
  const delay = window.setTimeout(() => {
    cancelIdle = whenIdle(async () => {
      const { mountBoard } = await import('../lib/board');
      if (destroyed || !canvas) return;
      await document.fonts.load('700 16px "B612 Mono"').catch(() => undefined);
      const board = await mountBoard(section, reduce, () => destroyed);
      if (!board) return;
      if (destroyed) {
        board.destroy();
        return;
      }
      handle = board;
      canvas.setAttribute('data-ready', '');
      gsap.to(section.querySelector('.hero-name .trace-art, .case-name .trace-art'), { autoAlpha: 0, duration: 0.9, delay: 0.35, ease: 'power1.inOut' });
      onReady(board.netX);
    });
  }, reduce ? 0 : 1500);
  return () => {
    destroyed = true;
    clearTimeout(delay);
    cancelIdle();
    handle?.destroy();
  };
}

export { startBoard };

/** `onSettled` fires once every section is set up and the page has its final height. */
export function initHome(onSettled: () => void) {
  const reduce = prefersReducedMotion();
  const hero = document.querySelector<HTMLElement>('.hero')!;
  const name = hero.querySelector<HTMLElement>('.hero-name')!;
  const nets = collectNets();
  const toolbox = document.querySelector<HTMLElement>('#toolbox');
  let netEntry = 0;

  const relayout = () => {
    routeNets(nets, netEntry);
    if (toolbox) routeFan(toolbox);
  };
  relayout();

  /* Hero: the name routes itself, then the board comes up under the lamp. */
  const ctx = gsap.context(() => {
    gsap.set(name.querySelector('.trace-art'), { visibility: 'visible' });
    if (!reduce) drawTrace(name, 1.2);
  });

  const stopBoard = startBoard(hero, (netX) => {
    netEntry = netX;
    relayout();
  });

  ScrollTrigger.addEventListener('refreshInit', relayout);

  /* Everything scroll-driven. matchMedia reverts it all when the breakpoint or preference changes. */
  const mm = gsap.matchMedia();
  mm.add({ desktop: DESKTOP, mobile: '(max-width: 1023px)', motion: '(prefers-reduced-motion: no-preference)' }, (context) => {
    const { desktop, motion } = context.conditions as { desktop: boolean; mobile: boolean; motion: boolean };
    if (!motion) {
      onSettled();
      return;
    }

    /* Set up one section at a time, in page order, so the first paint never waits on all of it. */
    const queue = [
      () => {
        gsap.to(hero.querySelector('.board-canvas'), { yPercent: 14, ease: 'none', scrollTrigger: { trigger: hero, start: 'top top', end: 'bottom top', scrub: true } });
        return about(desktop);
      },
      () => work(desktop),
      toolboxSection,
      experience,
      closing,
    ];
    let timer = 0;
    const next = () => {
      const task = queue.shift();
      if (!task) {
        document.fonts.ready.then(() => {
          ScrollTrigger.refresh();
          onSettled();
        });
        return;
      }
      context.add(task);
      timer = window.setTimeout(next, 0);
    };
    timer = window.setTimeout(next, 0);
    return () => clearTimeout(timer);
  });

  function about(desktop: boolean) {
    const section = document.querySelector<HTMLElement>('#about');
    if (!section) return;
    const statement = section.querySelector<HTMLElement>('[data-lit]')!;
    const split = SplitText.create(statement, { type: 'words', aria: 'none' });
    const net = nets.about?.querySelector('.net-live');
    const title = section.querySelector('.about-title')!;
    const side = section.querySelector('.about-side')!;

    const tl = gsap.timeline({
      defaults: { ease: 'none' },
      scrollTrigger: desktop
        ? { trigger: section, pin: true, start: 'top top', end: '+=140%', scrub: true }
        : { trigger: section, start: 'top 75%', end: 'bottom 70%', scrub: true },
    });
    if (net) tl.fromTo(net, { strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: 1 }, 0);
    tl.add(drawTrace(title, 0.5).timeScale(1.6), desktop ? 0.25 : 0);
    tl.fromTo(split.words, { opacity: 0.16 }, { opacity: 1, duration: 0.1, stagger: 0.02 }, 0.35);
    tl.from(side.children, { autoAlpha: 0, y: 28, duration: 0.3, stagger: 0.12, ease: 'power2.out' }, 0.5);
    return () => split.revert();
  }

  function work(desktop: boolean) {
    const section = document.querySelector<HTMLElement>('#work');
    if (!section) return;
    const view = section.querySelector<HTMLElement>('[data-rail-view]')!;
    const track = section.querySelector<HTMLElement>('[data-rail-track]')!;
    const modules = gsap.utils.toArray<HTMLElement>(section.querySelectorAll('[data-module]'));
    const intro = section.querySelector('.rail-title')!;

    gsap.timeline({ scrollTrigger: { trigger: section, start: 'top 72%', once: true } }).add(drawTrace(intro, 0.9));

    if (!desktop) return;

    view.classList.add('is-pinned');
    const distance = () => track.scrollWidth - document.documentElement.clientWidth;
    const slide = gsap.to(track, {
      x: () => -distance(),
      ease: 'none',
      scrollTrigger: {
        trigger: section,
        pin: true,
        start: 'top top',
        end: () => `+=${distance()}`,
        scrub: true,
        invalidateOnRefresh: true,
      },
    });

    modules.forEach((module) => {
      gsap.fromTo(module.querySelector('[data-module-art]'), { x: 26 }, {
        x: -26,
        ease: 'none',
        scrollTrigger: { trigger: module, containerAnimation: slide, start: 'left right', end: 'right left', scrub: true },
      });
      const name = module.querySelector('.module-name');
      if (name) {
        gsap.timeline({
          scrollTrigger: { trigger: module, containerAnimation: slide, start: 'left 78%', toggleActions: 'play none none none' },
        }).add(drawTrace(name, 0.8));
      }
    });

    /* Keyboard users land on a card the rail has moved off screen, so bring it into view. */
    section.addEventListener('focusin', (e) => {
      const target = e.target as Element;
      const module = target.closest<HTMLElement>('[data-module]');
      const st = slide.scrollTrigger;
      // Only keyboard focus moves the rail. A mouse press must never pull a link out from under the pointer.
      if (!module || !st || !target.matches(':focus-visible')) return;
      view.scrollLeft = 0;
      const span = distance();
      const left = module.offsetLeft - (document.documentElement.clientWidth - module.offsetWidth) / 2;
      const progress = gsap.utils.clamp(0, 1, left / span);
      getLenis()?.scrollTo(st.start + (st.end - st.start) * progress, { immediate: true, force: true });
    });

    return () => view.classList.remove('is-pinned');
  }

  function toolboxSection() {
    if (!toolbox) return;
    const fanPaths = toolbox.querySelectorAll('[data-fan] path');
    const groups = toolbox.querySelectorAll('[data-group]');
    const net = nets.toolbox?.querySelector('.net-live');
    const title = toolbox.querySelector('.tb-title')!;

    if (net) {
      gsap.fromTo(net, { strokeDashoffset: 1 }, { strokeDashoffset: 0, ease: 'none', scrollTrigger: { trigger: toolbox, start: 'top 90%', end: 'top 30%', scrub: true } });
    }
    gsap.timeline({ scrollTrigger: { trigger: toolbox, start: 'top 70%', once: true } }).add(drawTrace(title, 0.8));

    const tl = gsap.timeline({ scrollTrigger: { trigger: toolbox, start: 'top 45%', once: true } });
    if (fanPaths.length) tl.fromTo(fanPaths, { drawSVG: '0%' }, { drawSVG: '100%', duration: 1.1, ease: 'power2.inOut', stagger: 0.06 }, 0);
    tl.from(groups, { autoAlpha: 0, y: 26, duration: 0.8, stagger: 0.09 }, fanPaths.length ? 0.55 : 0);
  }

  function experience() {
    const section = document.querySelector<HTMLElement>('#experience');
    if (!section) return;
    const net = nets.experience?.querySelector('.net-live');
    if (net) {
      gsap.fromTo(net, { strokeDashoffset: 1 }, { strokeDashoffset: 0, ease: 'none', scrollTrigger: { trigger: section, start: 'top 80%', end: 'bottom 80%', scrub: true } });
    }
    const title = section.querySelector('.xp-title');
    if (title) gsap.timeline({ scrollTrigger: { trigger: section, start: 'top 72%', once: true } }).add(drawTrace(title, 0.8));

    /* Signals sweep left to right, like a logic analyzer capturing a trace. */
    gsap.utils.toArray<HTMLElement>(section.querySelectorAll('[data-sig]')).forEach((row) => {
      const wave = row.querySelector('[data-wave]');
      const text = row.querySelector('.sig-text');
      gsap.fromTo(wave, { clipPath: 'inset(-20% 100% -20% 0)' }, {
        clipPath: 'inset(-20% 0% -20% 0)',
        ease: 'none',
        scrollTrigger: { trigger: row, start: 'top 88%', end: 'top 48%', scrub: true },
      });
      gsap.from(text, { autoAlpha: 0, y: 18, duration: 0.8, scrollTrigger: { trigger: row, start: 'top 86%', once: true } });
    });
    gsap.fromTo(section.querySelector('[data-xp-now]'), { clipPath: 'inset(-30px -60px 100% -60px)' }, { clipPath: 'inset(-30px -60px 0% -60px)', ease: 'none', scrollTrigger: { trigger: '[data-xp]', start: 'top 70%', end: 'bottom 70%', scrub: true } });
  }

  function closing() {
    const resume = document.querySelector<HTMLElement>('#resume');
    const contact = document.querySelector<HTMLElement>('#contact');
    if (resume) {
      const net = nets.resume?.querySelector('.net-live');
      if (net) gsap.fromTo(net, { strokeDashoffset: 1 }, { strokeDashoffset: 0, ease: 'none', scrollTrigger: { trigger: resume, start: 'top 85%', end: 'bottom 75%', scrub: true } });
      gsap.timeline({ scrollTrigger: { trigger: resume, start: 'top 72%', once: true } }).add(drawTrace(resume.querySelector('.resume-title')!, 0.8));
      gsap.from(resume.querySelector('[data-test-point]'), { scale: 0.86, opacity: 0, duration: 1.1, ease: 'expo.out', scrollTrigger: { trigger: resume, start: 'top 45%', once: true } });
    }
    if (contact) {
      const net = nets.contact?.querySelector('.net-live');
      if (net) gsap.fromTo(net, { strokeDashoffset: 1 }, { strokeDashoffset: 0, ease: 'none', scrollTrigger: { trigger: contact, start: 'top 90%', end: 'bottom 100%', scrub: true } });
      gsap.timeline({ scrollTrigger: { trigger: contact, start: 'top 72%', once: true } }).add(drawTrace(contact.querySelector('.contact-title')!, 1));
      gsap.from(contact.querySelectorAll('.fingers li'), { yPercent: 34, opacity: 0, duration: 1, stagger: 0.08, scrollTrigger: { trigger: '.connector', start: 'top 92%', once: true } });
    }
  }

  return () => {
    stopBoard();
    ScrollTrigger.removeEventListener('refreshInit', relayout);
    mm.revert();
    ctx.revert();
  };
}

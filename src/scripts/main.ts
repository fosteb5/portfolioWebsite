import { initCaseStudy } from './case-study';
import { initCursor } from './cursor';
import { initHome } from './home';
import { gsap, ScrollTrigger } from './motion';
import { getLenis, goTo, initScroll } from './scroll';
import { initTransitions } from './transition';

initScroll();
initCursor();
initTransitions();

let teardown: (() => void)[] = [];

/** Mobile menu. A native dialog gives us the focus trap and Escape for free. */
function initMenu() {
  const menu = document.querySelector<HTMLDialogElement>('#menu');
  const open = document.querySelector('#menu-open');
  const close = document.querySelector('#menu-close');
  if (!menu || !open || !close) return;
  const shut = () => menu.close();
  open.addEventListener('click', () => {
    menu.showModal();
    getLenis()?.stop();
  });
  close.addEventListener('click', shut);
  menu.addEventListener('close', () => getLenis()?.start());
  menu.addEventListener('click', (e) => {
    if ((e.target as Element).closest('a')) shut();
  });
}

/** The nav steps aside while reading and returns the moment you scroll back up. */
function initNavVisibility() {
  const nav = document.querySelector<HTMLElement>('#site-nav');
  if (!nav) return;
  const trigger = ScrollTrigger.create({
    start: 0,
    end: 'max',
    onUpdate: (self) => nav.toggleAttribute('data-hidden', self.direction === 1 && self.scroll() > innerHeight * 0.7),
  });
  teardown.push(() => trigger.kill());
}

function boot() {
  const page = document.body.dataset.page;
  initMenu();
  initNavVisibility();

  // Pin spacers did not exist when the browser followed the link, so finish the jump once they do.
  let jumped = false;
  const finishHashJump = () => {
    const target = location.hash && document.getElementById(location.hash.slice(1));
    if (jumped || !target) return;
    jumped = true;
    requestAnimationFrame(() => goTo(target, true));
  };

  if (page === 'home') {
    teardown.push(initHome(finishHashJump));
    return;
  }
  if (page === 'case') teardown.push(initCaseStudy());

  // Fonts change text wrapping, so measure once they have settled.
  document.fonts.ready.then(() => {
    ScrollTrigger.refresh();
    finishHashJump();
  });
}

document.addEventListener('astro:page-load', boot);

document.addEventListener('astro:before-swap', () => {
  teardown.forEach((stop) => stop());
  teardown = [];
  ScrollTrigger.getAll().forEach((trigger) => trigger.kill());
  gsap.globalTimeline.getChildren(true, true, false).forEach((tween) => {
    if (tween.targets()[0] instanceof Element && !document.contains(tween.targets()[0] as Element)) tween.kill();
  });
});

import { ScrollTrigger } from './motion';

/**
 * Plays a rendered image sequence as the reader scrolls. The stage is CSS-sticky, so there is no pin:
 * progress runs from the moment it sticks to the moment it lets go, and picks the frame to draw.
 */
export function initSequence(root: HTMLElement) {
  const canvas = root.querySelector('canvas');
  const ctx = canvas?.getContext('2d');
  const track = root.querySelector<HTMLElement>('[data-seq-track]');
  const stage = root.querySelector<HTMLElement>('[data-seq-stage]');
  const count = Number(root.dataset.frames);
  if (!canvas || !ctx || !track || !stage || !count) return () => undefined;
  const steps = Array.from(root.querySelectorAll<HTMLElement>('[data-seq-step]'));

  root.classList.add('is-live');
  const width = canvas.clientWidth * devicePixelRatio > 760 ? 1280 : 720;
  canvas.width = width;
  canvas.height = Math.round((width * 9) / 16);

  const frames: HTMLImageElement[] = [];
  let shown = -1;
  let target = 0;

  /* Draws the nearest frame that has arrived, so a slow connection shows something close rather than nothing. */
  const draw = () => {
    for (let d = 0; d < count; d++) {
      for (const i of d ? [target - d, target + d] : [target]) {
        const img = frames[i];
        if (!img?.complete || !img.naturalWidth) continue;
        if (i !== shown) {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
          shown = i;
        }
        return;
      }
    }
  };

  const load = () => {
    if (frames.length) return;
    for (let i = 0; i < count; i++) {
      const img = new Image();
      img.decoding = 'async';
      img.onload = draw;
      img.src = `${root.dataset.src}${width}/${String(i + 1).padStart(3, '0')}.webp`;
      frames.push(img);
    }
  };

  const update = (progress: number) => {
    target = Math.round(progress * (count - 1));
    draw();
    for (const step of steps) {
      const from = Number(step.dataset.from);
      const to = Number(step.dataset.to);
      const t = Math.min(1, Math.max(0, (progress - from) / (to - from)));
      step.style.setProperty('--p', t.toFixed(3));
      step.dataset.state = t <= 0 ? 'queued' : t >= 1 ? 'done' : 'printing';
    }
  };

  const stickTop = () => parseFloat(getComputedStyle(stage).top) || 0;
  const scrub = ScrollTrigger.create({
    trigger: track,
    start: () => `top ${stickTop()}px`,
    end: () => `bottom ${stickTop() + stage.offsetHeight}px`,
    invalidateOnRefresh: true,
    onUpdate: (self) => update(self.progress),
    onRefresh: (self) => update(self.progress),
  });
  // Start fetching a little over a screen ahead, from either direction.
  const preload = ScrollTrigger.create({ trigger: root, start: 'top bottom+=120%', end: 'bottom top-=120%', onToggle: load });
  update(scrub.progress);

  return () => {
    scrub.kill();
    preload.kill();
    root.classList.remove('is-live');
  };
}

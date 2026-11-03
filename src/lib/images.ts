import type { ImageMetadata } from 'astro';

const images = import.meta.glob<{ default: ImageMetadata }>('/src/assets/projects/**/*.{jpg,jpeg,png,webp,avif}');

/** Loads a photo named in src/content.ts, such as 'projects/liftlabs/render.jpg'. Fails the build on a bad path. */
export async function projectImage(src: string): Promise<ImageMetadata> {
  const key = `/src/assets/${src}`;
  const loader = images[key];
  if (!loader) throw new Error(`Image not found: ${key}. Check the path in src/content.ts.`);
  return (await loader()).default;
}

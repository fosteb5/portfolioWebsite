import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import tailwindcss from '@tailwindcss/vite';

// The live address, used for search results, the sitemap and link previews.
// If the address changes, update it here or set SITE_URL in your host's build settings.
const PRODUCTION_URL = 'https://fosterbeard.ca';

const vercelUrl = process.env.VERCEL_PROJECT_PRODUCTION_URL;

export default defineConfig({
  site: process.env.SITE_URL ?? (vercelUrl ? `https://${vercelUrl}` : PRODUCTION_URL),
  // Astro 7 defaults to JSX whitespace rules, which join adjacent inline text.
  compressHTML: true,
  prefetch: { prefetchAll: true, defaultStrategy: 'hover' },
  integrations: [sitemap()],
  vite: { plugins: [tailwindcss()] },
});

# Foster Beard portfolio

Personal portfolio built with Astro, TypeScript, Tailwind CSS, GSAP and Lenis. The lit circuit boards are a small WebGL shader, so there is no 3D library to load.

## Edit the content

Everything you can read on the site is in **`src/content.ts`**. Open it, change the text, save. You should not need to touch a component.

Search that file for `TODO` to see what still needs your input.

| To change | Do this |
| --- | --- |
| Text, roles, dates, links | Edit `src/content.ts` |
| A project's numbers | Add them to its `metrics` list. The section appears once the list has entries |
| Photos | Put them in `src/assets/projects/<slug>/`, then set `src` on that media item, such as `'projects/liftlabs/first-flight.jpg'`. They are resized and compressed for you during the build |
| Your portrait | Same, using the `portrait` entry in the `about` section |
| Videos | Put MP4s in `public/video/`, then set `src`, such as `'/video/liftlabs-flight.mp4'`. Add a `poster` image too |
| Your résumé | Replace `public/resume/foster-beard-resume.pdf` |
| A project's board colour | Change its `board` value: `green`, `blue`, `black`, `red`, `purple`, `amber`, `white` or `berry` |

Words lettered in copper, such as `traceName`, use capitals, digits and `- ' .` only. The build tells you if a character is missing.

Placeholders for missing photos and any hidden metrics are safe to publish. The red TODO notes only appear while running locally.

## Run it locally

You need Node.js 22.23 or newer.

```bash
npm install
npm run dev
```

Then open http://localhost:4321. To check the production build:

```bash
npm run build
npm run preview
```

`npm run check` looks for type errors.

## Deployment

The site runs for free on Cloudflare Workers at https://fosterbeard.ca (also reachable at https://foster-beard.foster5beard.workers.dev). It is fully static, so it needs no server and no paid plan.

Every push to `main` builds and publishes the site automatically. Build status appears next to each commit on GitHub, and deployment settings are in `wrangler.jsonc`.

To use a custom domain, add the domain to Cloudflare first. Then open the `foster-beard` Worker in the [Cloudflare dashboard](https://dash.cloudflare.com), go to **Settings > Domains & Routes**, and select **Add > Custom Domain**. Update `PRODUCTION_URL` in `astro.config.mjs` to match and push. Search results and link previews read that address.

Security and cache headers are in `public/_headers`. Vercel works too, using `vercel.json`, but its free plan is for non-commercial personal use.

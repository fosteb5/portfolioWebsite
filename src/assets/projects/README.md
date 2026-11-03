Put project photos here, in a folder named after the project slug, for example:

    src/assets/projects/liftlabs/first-flight.jpg

Then point to the file from src/content.ts:

    { type: 'image', src: 'projects/liftlabs/first-flight.jpg', alt: '...', caption: '...' }

Astro resizes and compresses these images during the build, so large originals are fine.

The first photo in a project's `media` list is also the picture on its home page
card. Until a project has a photo, the card shows its system diagram instead.
Wide shots work best there: the card crops to roughly 5:2 on desktop and 16:10 on phones.

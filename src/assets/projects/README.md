Put project photos here, in a folder named after the project slug, for example:

    src/assets/projects/liftlabs/first-flight.jpg

Then point to the file from src/content.ts:

    { type: 'image', src: 'projects/liftlabs/first-flight.jpg', alt: '...', caption: '...' }

Astro resizes and compresses these images during the build, so large originals are fine.

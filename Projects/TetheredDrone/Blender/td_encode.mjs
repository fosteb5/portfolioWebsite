// Encodes rendered PNG frames into the site's scroll-animation frames, at 1280 and 720 wide.
// Run from the repository root, so sharp resolves from its node_modules:
//   node Projects/TetheredDrone/Blender/td_encode.mjs <frames dir> <public/sequences/name> [--alpha]
// --alpha keeps transparency (the studio breakdown); without it the frames are flattened (the washing scene).
import fs from 'node:fs';
import path from 'node:path';
import sharp from 'sharp';

const [src, dest, flag] = process.argv.slice(2);
const alpha = flag === '--alpha';
const frames = fs.readdirSync(src).filter((f) => /^\d{3}\.png$/.test(f)).sort();
if (!frames.length) throw new Error(`No NNN.png frames in ${src}`);

for (const width of [1280, 720]) {
  const out = path.join(dest, String(width));
  // Clear old frames file by file: OneDrive can lock the folder itself while it syncs.
  fs.mkdirSync(out, { recursive: true });
  for (const old of fs.readdirSync(out)) if (old.endsWith('.webp')) fs.rmSync(path.join(out, old), { force: true });
  for (const f of frames) {
    let img = sharp(path.join(src, f)).resize({ width, kernel: 'lanczos3' });
    if (!alpha) img = img.flatten({ background: '#000000' });
    await img.webp({ quality: 70, alphaQuality: 80, effort: 5, smartSubsample: true }).toFile(path.join(out, f.replace('.png', '.webp')));
  }
}
const size = (dir) => fs.readdirSync(dir).reduce((n, f) => n + fs.statSync(path.join(dir, f)).size, 0);
console.log(`${frames.length} frames -> ${dest}: 1280 ${(size(path.join(dest, '1280')) / 1e6).toFixed(1)} MB, 720 ${(size(path.join(dest, '720')) / 1e6).toFixed(1)} MB`);

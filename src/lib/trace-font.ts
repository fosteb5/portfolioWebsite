/**
 * The site's display lettering: a single-stroke alphabet routed like PCB traces.
 * Every stroke is 0, 45 or 90 degrees on a 4 x 6 grid, with a pad at each free end.
 * The same glyphs drive the SVG headings and the copper in the WebGL boards.
 */

export type Point = [number, number];

export interface Glyph {
  width: number;
  strokes: Point[][];
  pads?: Point[];
}

/** Letter height in grid units. */
export const CAP = 6;
/** Space between letters. */
export const TRACKING = 1.5;
/** Room around a word for pads that sit on its edges. */
export const MARGIN = 0.8;
/** Viewbox height of one word. É needs extra room above and is handled by callers. */
export const WORD_HEIGHT = CAP + MARGIN * 2;

const O: Point[] = [[1, 0], [3, 0], [4, 1], [4, 5], [3, 6], [1, 6], [0, 5], [0, 1], [1, 0]];

export const GLYPHS: Record<string, Glyph> = {
  A: { width: 4, strokes: [[[0, 6], [0, 1], [1, 0], [3, 0], [4, 1], [4, 6]], [[0, 4], [4, 4]]], pads: [[0, 6], [4, 6]] },
  B: { width: 4, strokes: [[[0, 3], [3, 3], [4, 2], [4, 1], [3, 0], [0, 0], [0, 6], [3, 6], [4, 5], [4, 4], [3, 3]]] },
  C: { width: 4, strokes: [[[4, 1], [3, 0], [1, 0], [0, 1], [0, 5], [1, 6], [3, 6], [4, 5]]], pads: [[4, 1], [4, 5]] },
  D: { width: 4, strokes: [[[0, 0], [3, 0], [4, 1], [4, 5], [3, 6], [0, 6], [0, 0]]] },
  E: { width: 4, strokes: [[[4, 0], [1, 0], [0, 1], [0, 5], [1, 6], [4, 6]], [[0, 3], [3, 3]]], pads: [[4, 0], [4, 6], [3, 3]] },
  F: { width: 4, strokes: [[[4, 0], [1, 0], [0, 1], [0, 6]], [[0, 3], [3, 3]]], pads: [[4, 0], [0, 6], [3, 3]] },
  G: { width: 4, strokes: [[[4, 1], [3, 0], [1, 0], [0, 1], [0, 5], [1, 6], [3, 6], [4, 5], [4, 3], [2, 3]]], pads: [[4, 1], [2, 3]] },
  H: { width: 4, strokes: [[[0, 0], [0, 6]], [[4, 0], [4, 6]], [[0, 3], [4, 3]]], pads: [[0, 0], [0, 6], [4, 0], [4, 6]] },
  I: { width: 0, strokes: [[[0, 0], [0, 6]]], pads: [[0, 0], [0, 6]] },
  J: { width: 4, strokes: [[[4, 0], [4, 5], [3, 6], [1, 6], [0, 5]]], pads: [[4, 0], [0, 5]] },
  K: { width: 4, strokes: [[[0, 0], [0, 6]], [[4, 0], [1, 3], [0, 3]], [[1, 3], [4, 6]]], pads: [[0, 0], [0, 6], [4, 0], [4, 6]] },
  L: { width: 4, strokes: [[[0, 0], [0, 5], [1, 6], [4, 6]]], pads: [[0, 0], [4, 6]] },
  M: { width: 5, strokes: [[[0, 6], [0, 0], [2.5, 2.5], [5, 0], [5, 6]]], pads: [[0, 6], [5, 6]] },
  N: { width: 4, strokes: [[[0, 6], [0, 0]], [[0, 1], [4, 5]], [[4, 0], [4, 6]]], pads: [[0, 6], [4, 0]] },
  O: { width: 4, strokes: [O] },
  P: { width: 4, strokes: [[[0, 6], [0, 0], [3, 0], [4, 1], [4, 3], [3, 4], [0, 4]]], pads: [[0, 6]] },
  Q: { width: 4, strokes: [O, [[2.5, 4.5], [4.4, 6.4]]], pads: [[4.4, 6.4]] },
  R: { width: 4, strokes: [[[0, 6], [0, 1], [1, 0], [3, 0], [4, 1], [4, 2], [3, 3], [0, 3]], [[2, 3], [4, 5], [4, 6]]], pads: [[0, 6], [4, 6]] },
  S: { width: 4, strokes: [[[4, 1], [3, 0], [1, 0], [0, 1], [0, 2], [1, 3], [3, 3], [4, 4], [4, 5], [3, 6], [1, 6], [0, 5]]], pads: [[4, 1], [0, 5]] },
  T: { width: 4, strokes: [[[0, 0], [4, 0]], [[2, 0], [2, 6]]], pads: [[0, 0], [4, 0], [2, 6]] },
  U: { width: 4, strokes: [[[0, 0], [0, 5], [1, 6], [3, 6], [4, 5], [4, 0]]], pads: [[0, 0], [4, 0]] },
  V: { width: 4, strokes: [[[0, 0], [0, 4], [2, 6], [4, 4], [4, 0]]], pads: [[0, 0], [4, 0]] },
  W: { width: 5, strokes: [[[0, 0], [0, 6], [2.5, 3.5], [5, 6], [5, 0]]], pads: [[0, 0], [5, 0]] },
  X: { width: 4, strokes: [[[0, 0], [0, 1], [4, 5], [4, 6]], [[4, 0], [4, 1], [0, 5], [0, 6]]], pads: [[0, 0], [4, 0], [0, 6], [4, 6]] },
  Y: { width: 4, strokes: [[[0, 0], [0, 1], [2, 3], [4, 1], [4, 0]], [[2, 3], [2, 6]]], pads: [[0, 0], [4, 0], [2, 6]] },
  Z: { width: 4, strokes: [[[0, 0], [4, 0], [4, 1], [0, 5], [0, 6], [4, 6]]], pads: [[0, 0], [4, 6]] },
  0: { width: 4, strokes: [O, [[1, 4], [3, 2]]] },
  1: { width: 2, strokes: [[[0, 1], [1, 0], [1, 6]]], pads: [[0, 1], [1, 6]] },
  2: { width: 4, strokes: [[[0, 1], [1, 0], [3, 0], [4, 1], [4, 2], [0, 6], [4, 6]]], pads: [[0, 1], [4, 6]] },
  3: { width: 4, strokes: [[[0, 1], [1, 0], [3, 0], [4, 1], [4, 2], [3, 3], [1, 3]], [[3, 3], [4, 4], [4, 5], [3, 6], [1, 6], [0, 5]]], pads: [[0, 1], [1, 3], [0, 5]] },
  4: { width: 4, strokes: [[[3, 6], [3, 0], [0, 3], [0, 4], [4, 4]]], pads: [[3, 6], [4, 4]] },
  5: { width: 4, strokes: [[[4, 0], [0, 0], [0, 3], [3, 3], [4, 4], [4, 5], [3, 6], [1, 6], [0, 5]]], pads: [[4, 0], [0, 5]] },
  6: { width: 4, strokes: [[[4, 1], [3, 0], [1, 0], [0, 1], [0, 5], [1, 6], [3, 6], [4, 5], [4, 4], [3, 3], [0, 3]]], pads: [[4, 1]] },
  7: { width: 4, strokes: [[[0, 0], [4, 0], [4, 1], [1, 4], [1, 6]]], pads: [[0, 0], [1, 6]] },
  8: { width: 4, strokes: [[[1, 3], [3, 3], [4, 2], [4, 1], [3, 0], [1, 0], [0, 1], [0, 2], [1, 3], [0, 4], [0, 5], [1, 6], [3, 6], [4, 5], [4, 4], [3, 3]]] },
  9: { width: 4, strokes: [[[0, 5], [1, 6], [3, 6], [4, 5], [4, 1], [3, 0], [1, 0], [0, 1], [0, 2], [1, 3], [4, 3]]], pads: [[0, 5], [4, 3]] },
  '-': { width: 3, strokes: [[[0, 3], [3, 3]]], pads: [[0, 3], [3, 3]] },
  "'": { width: 0, strokes: [[[0, 0], [0, 1.6]]] },
  '.': { width: 0, strokes: [], pads: [[0, 6]] },
};

// É is E with an accent that climbs into the margin above the cap line.
GLYPHS['É'] = { width: 4, strokes: [...GLYPHS.E.strokes, [[1.4, -0.9], [2.6, -2.1]]], pads: GLYPHS.E.pads };

export interface PlacedGlyph {
  char: string;
  strokes: Point[][];
  pads: Point[];
}

export interface WordLayout {
  text: string;
  width: number;
  glyphs: PlacedGlyph[];
  /** True when something rises above the cap line and the word needs headroom. */
  accent: boolean;
}

/** Places a word's glyphs left to right, with the origin at the top-left of the first letter. */
export function layoutWord(text: string): WordLayout {
  let x = 0;
  const glyphs: PlacedGlyph[] = [];
  let accent = false;
  for (const char of text) {
    const glyph = GLYPHS[char];
    if (!glyph) throw new Error(`The trace alphabet has no glyph for "${char}". Use capitals, digits, - ' or .`);
    if (char === 'É') accent = true;
    glyphs.push({
      char,
      strokes: glyph.strokes.map((stroke) => stroke.map(([a, b]): Point => [a + x, b])),
      pads: (glyph.pads ?? []).map(([a, b]): Point => [a + x, b]),
    });
    x += glyph.width + TRACKING;
  }
  return { text, width: Math.max(0, x - TRACKING), glyphs, accent };
}

/** Converts a stroke to SVG path data, rounded so the markup stays small. */
export function strokePath(stroke: Point[]): string {
  return stroke.map(([x, y], i) => `${i ? 'L' : 'M'}${+x.toFixed(2)} ${+y.toFixed(2)}`).join('');
}

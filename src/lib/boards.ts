import type { BoardColour } from '../content';

/**
 * Solder mask colours. Each project is a different fab order.
 * mask: the page ground. void: clearance around copper. cu: copper seen through the mask.
 * trace: lettering and links on this board. onTrace: text on a trace-coloured button.
 * silk: reading text. accent: this board's colour when used on the light reading layer.
 */
export interface Board {
  mask: string;
  void: string;
  cu: string;
  trace: string;
  onTrace: string;
  silk: string;
  silkDim: string;
  accent: string;
  /** How strongly the lamp lifts this board. Light masks need much less. */
  gain: number;
}

export const BOARDS: Record<BoardColour, Board> = {
  green: { mask: '#0C4A3A', void: '#04241C', cu: '#1C8267', trace: '#E2B65A', onTrace: '#08201A', silk: '#F3F5EE', silkDim: '#BFD3CA', accent: '#0C4A3A', gain: 1.25 },
  blue: { mask: '#0F3B78', void: '#061B3C', cu: '#2467B8', trace: '#E2B65A', onTrace: '#08201A', silk: '#F3F5EE', silkDim: '#C3D3E8', accent: '#0F3B78', gain: 1.25 },
  black: { mask: '#171B1E', void: '#07090A', cu: '#3A4248', trace: '#E2B65A', onTrace: '#08201A', silk: '#F3F5EE', silkDim: '#C2C8CB', accent: '#171B1E', gain: 1.5 },
  red: { mask: '#7A1A18', void: '#3A0A09', cu: '#B8372F', trace: '#F0C777', onTrace: '#08201A', silk: '#F7F2EC', silkDim: '#EBCFC8', accent: '#7A1A18', gain: 1.1 },
  purple: { mask: '#3A2670', void: '#190E36', cu: '#6547AE', trace: '#E8BE66', onTrace: '#08201A', silk: '#F3F1F8', silkDim: '#D1C9E6', accent: '#3A2670', gain: 1.25 },
  amber: { mask: '#5C390C', void: '#2A1903', cu: '#99641B', trace: '#F2CB7C', onTrace: '#08201A', silk: '#F8F3E8', silkDim: '#E6D5B7', accent: '#5C390C', gain: 1.2 },
  white: { mask: '#E8EAE4', void: '#D2D5CC', cu: '#7C8276', trace: '#6B4A0E', onTrace: '#F8F5EC', silk: '#14201C', silkDim: '#3D4A45', accent: '#6B4A0E', gain: 0.1 },
  berry: { mask: '#6A1850', void: '#300823', cu: '#A63280', trace: '#EEC36F', onTrace: '#08201A', silk: '#F8F0F5', silkDim: '#E8CCDD', accent: '#6A1850', gain: 1.15 },
};

/** Inline style that lets a section use its board's colours through CSS variables. */
export function boardStyle(colour: BoardColour): string {
  const b = BOARDS[colour];
  return `--mask:${b.mask};--void:${b.void};--cu:${b.cu};--trace:${b.trace};--on-trace:${b.onTrace};--silk:${b.silk};--silk-dim:${b.silkDim};--accent:${b.accent}`;
}

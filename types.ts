export interface CellState {
  id: string; // e.g., "cell-0-0"
  row: number;
  col: number;
  solutionValue: number; // The correct number for this cell in the generated solution
  displayValue: number | null; // Number to display if it's a clue, otherwise null
  userValue: string; // User's input, string to allow empty
  isClue: boolean; // True if this cell is a pre-filled clue
  isReadOnly: boolean; // True if the cell cannot be edited (i.e., it's a clue)
  isCorrect: boolean | null; // null: not checked, true: correct, false: incorrect (after checking)
}

export type GridState = CellState[][]; // Represents the 3x3 grid state

export type GamePhase = 'playing' | 'checking' | 'solved';

export interface Puzzle {
  grid: GridState;
  rowSums: number[];
  colSums: number[];
  diagSum: number; // Sum of the main diagonal (top-left to bottom-right)
  solution: number[][]; // The complete solution grid
}
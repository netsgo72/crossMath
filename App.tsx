
import React, { useState, useEffect, useCallback } from 'react';
import { GridState, CellState, GamePhase, Puzzle } from './types';
import GridCell from './components/GridCell';

const GRID_SIZE = 3;
const NUM_CLUES = 4; // Aim for this many clues, "up to 4" is satisfied
const MIN_NUM = 1;
const MAX_NUM = 9;

const generateNewPuzzle = (): Puzzle => {
  let solution: number[][] = [];
  let rowSums: number[] = [];
  let colSums: number[] = [];
  let diagSum = 0;
  let cluePositions: { row: number; col: number }[] = [];

  // Generate a full solution grid
  solution = Array(GRID_SIZE).fill(null).map(() =>
    Array(GRID_SIZE).fill(null).map(() =>
      Math.floor(Math.random() * (MAX_NUM - MIN_NUM + 1)) + MIN_NUM
    )
  );

  // Calculate row and column sums from the solution
  rowSums = solution.map(row => row.reduce((sum, val) => sum + val, 0));
  colSums = Array(GRID_SIZE).fill(0);
  for (let j = 0; j < GRID_SIZE; j++) {
    for (let i = 0; i < GRID_SIZE; i++) {
      colSums[j] += solution[i][j];
    }
  }

  // Calculate main diagonal sum (top-left to bottom-right)
  for (let i = 0; i < GRID_SIZE; i++) {
    diagSum += solution[i][i];
  }

  // Select clue positions randomly while respecting constraints
  const allCoords: { row: number; col: number }[] = [];
  for (let i = 0; i < GRID_SIZE; i++) {
    for (let j = 0; j < GRID_SIZE; j++) {
      allCoords.push({ row: i, col: j });
    }
  }

  // Shuffle coordinates for random selection order
  for (let i = allCoords.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [allCoords[i], allCoords[j]] = [allCoords[j], allCoords[i]];
  }

  const rowClueCounts = Array(GRID_SIZE).fill(0);
  const colClueCounts = Array(GRID_SIZE).fill(0);

  for (const coord of allCoords) {
    if (cluePositions.length >= NUM_CLUES) {
      break; // We have enough clues
    }

    if (rowClueCounts[coord.row] < 2 && colClueCounts[coord.col] < 2) {
      cluePositions.push(coord);
      rowClueCounts[coord.row]++;
      colClueCounts[coord.col]++;
    }
  }
  
  // If, after trying all shuffled coordinates, we have fewer than NUM_CLUES
  // (e.g. 3 clues instead of 4 due to random order and constraints),
  // this is acceptable as the requirement is "up to 4 clues".
  // For a 3x3 grid, NUM_CLUES=4, it's highly likely to get 4 clues.

  // Initialize grid state
  const initialGrid: GridState = Array(GRID_SIZE).fill(null).map((_, r) =>
    Array(GRID_SIZE).fill(null).map((_, c) => {
      const isClue = cluePositions.some(pos => pos.row === r && pos.col === c);
      const solutionValue = solution[r][c];
      return {
        id: `cell-${r}-${c}`,
        row: r,
        col: c,
        solutionValue: solutionValue,
        displayValue: isClue ? solutionValue : null,
        userValue: isClue ? String(solutionValue) : '',
        isClue: isClue,
        isReadOnly: isClue,
        isCorrect: isClue ? true : null, // Clues are inherently correct
      };
    })
  );

  return { grid: initialGrid, rowSums, colSums, diagSum, solution };
};


const App: React.FC = () => {
  const [puzzle, setPuzzle] = useState<Puzzle>(generateNewPuzzle());
  const [gamePhase, setGamePhase] = useState<GamePhase>('playing');
  const [feedbackMessage, setFeedbackMessage] = useState<string>('');

  const initializeNewGame = useCallback(() => {
    setPuzzle(generateNewPuzzle());
    setGamePhase('playing');
    setFeedbackMessage('');
  }, []);

  useEffect(() => {
    initializeNewGame();
  }, [initializeNewGame]);

  const handleUserValueChange = (id: string, value: string) => {
    if (gamePhase === 'solved') return;
    if (gamePhase === 'checking') setGamePhase('playing'); // Allow editing after checking

    const numericValue = value.trim();
    // Allow only single digit 1-9 or empty string
    if (!(/^[1-9]?$/.test(numericValue))) {
        return;
    }

    setPuzzle(prevPuzzle => ({
      ...prevPuzzle,
      grid: prevPuzzle.grid.map(row =>
        row.map(cell =>
          cell.id === id && !cell.isReadOnly
            ? { ...cell, userValue: numericValue, isCorrect: null } // Reset correctness on change
            : cell
        )
      ),
    }));
  };

  const checkPuzzle = () => {
    let allCorrect = true;
    let hasEmptyCells = false;

    const checkedGrid = puzzle.grid.map(row =>
      row.map(cell => {
        if (cell.isClue) {
          return cell;
        }
        if (cell.userValue === '') {
          hasEmptyCells = true;
          allCorrect = false; 
          return { ...cell, isCorrect: null }; 
        }
        const userNum = parseInt(cell.userValue, 10);
        const isCellCorrect = userNum === cell.solutionValue;
        if (!isCellCorrect) {
          allCorrect = false;
        }
        return { ...cell, isCorrect: isCellCorrect };
      })
    );
    
    setPuzzle(prevPuzzle => ({ ...prevPuzzle, grid: checkedGrid }));

    if (allCorrect && !hasEmptyCells) {
      setGamePhase('solved');
      setFeedbackMessage('🎉 퍼즐 완성! 🎉');
    } else if (hasEmptyCells) {
      setGamePhase('checking');
      setFeedbackMessage('빈 칸을 모두 채워주세요.');
    }
    else {
      setGamePhase('checking');
      setFeedbackMessage('오답이 있어요. 다시 시도해보세요.');
    }
  };

  return (
    <div className="bg-gradient-to-br from-sky-200 via-indigo-200 to-purple-300 text-slate-800 min-h-screen flex flex-col items-center justify-center p-4 selection:bg-indigo-500 selection:text-white">
      <div className="bg-white/90 backdrop-blur-md p-6 sm:p-10 rounded-xl shadow-2xl w-full max-w-md sm:max-w-lg">
        <header className="text-center mb-6 sm:mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-indigo-700">숫자 합계 퍼즐</h1>
        </header>

        <main className="mb-6 sm:mb-8">
          <div className={`grid grid-cols-[repeat(3,minmax(0,1fr))_auto] grid-rows-[repeat(3,minmax(0,1fr))_auto] gap-1 sm:gap-2 p-2 bg-slate-200 rounded-md`}>
            {puzzle.grid.map((row, rIndex) =>
              row.map((cell, cIndex) => (
                <GridCell
                  key={cell.id}
                  cell={cell}
                  onUserValueChange={handleUserValueChange}
                  gamePhase={gamePhase}
                />
              ))
            )}
            {/* Row Sums */}
            {puzzle.rowSums.map((sum, rIndex) => (
              <div key={`row-sum-${rIndex}`} className="sum-cell bg-sky-100 rounded text-lg sm:text-xl p-2" style={{gridRow: rIndex + 1, gridColumn: GRID_SIZE + 1}}>
                {sum}
              </div>
            ))}
            {/* Column Sums */}
            {puzzle.colSums.map((sum, cIndex) => (
              <div key={`col-sum-${cIndex}`} className="sum-cell bg-sky-100 rounded text-lg sm:text-xl p-2" style={{gridRow: GRID_SIZE + 1, gridColumn: cIndex + 1}}>
                {sum}
              </div>
            ))}
            {/* Diagonal Sum (top-left to bottom-right) */}
             <div 
                className="sum-cell bg-purple-100 rounded text-lg sm:text-xl p-2" 
                style={{gridRow: GRID_SIZE + 1, gridColumn: GRID_SIZE + 1}}
                aria-label="Diagonal sum from top-left to bottom-right"
              >
              {puzzle.diagSum}
            </div>
          </div>
        </main>
        
        {feedbackMessage && (
          <p className={`text-center my-4 text-xl font-semibold ${gamePhase === 'solved' ? 'text-green-600' : 'text-red-600'}`}>
            {feedbackMessage}
          </p>
        )}

        <footer className="flex flex-col sm:flex-row justify-center items-center space-y-3 sm:space-y-0 sm:space-x-4">
          {gamePhase !== 'solved' && (
            <button
              onClick={checkPuzzle}
              className="w-full sm:w-auto bg-green-500 hover:bg-green-600 text-white font-semibold px-8 py-3 rounded-lg shadow-md transition-all duration-150 ease-in-out transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-green-400 focus:ring-opacity-75"
            >
              확인하기
            </button>
          )}
          <button
            onClick={initializeNewGame}
            className="w-full sm:w-auto bg-indigo-500 hover:bg-indigo-600 text-white font-semibold px-8 py-3 rounded-lg shadow-md transition-all duration-150 ease-in-out transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:ring-opacity-75"
          >
            새 게임
          </button>
        </footer>
      </div>
       <p className="text-center mt-8 text-sm text-slate-600">
        Made with 🧠 by AI.
      </p>
    </div>
  );
};

export default App;

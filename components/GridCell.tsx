
import React from 'react';
import { CellState, GamePhase } from '../types';

interface GridCellProps {
  cell: CellState;
  onUserValueChange: (id: string, value: string) => void;
  gamePhase: GamePhase;
}

const GridCell: React.FC<GridCellProps> = ({ cell, onUserValueChange, gamePhase }) => {
  const { id, displayValue, userValue, isClue, isReadOnly, isCorrect } = cell;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onUserValueChange(id, e.target.value);
  };

  let cellBgColor = 'bg-white hover:bg-slate-50';
  let textColor = 'text-slate-800';
  let borderColor = 'border-slate-300 focus-within:border-indigo-500';

  if (isClue) {
    cellBgColor = 'bg-sky-50';
    textColor = 'text-indigo-700 font-semibold';
    borderColor = 'border-sky-200';
  } else if (gamePhase === 'checking' || gamePhase === 'solved') {
    if (isCorrect === true) {
      cellBgColor = 'bg-green-50';
      borderColor = 'border-green-500';
      textColor = 'text-green-700';
    } else if (isCorrect === false) {
      cellBgColor = 'bg-red-50';
      borderColor = 'border-red-500';
      textColor = 'text-red-700';
    } else { // isCorrect is null (e.g. empty cell during checking)
      cellBgColor = 'bg-yellow-50';
      borderColor = 'border-yellow-400';
    }
  }


  return (
    <div className={`aspect-square flex items-center justify-center p-1 rounded shadow-sm transition-colors duration-150 ${cellBgColor} ${borderColor} border-2`}>
      {isClue ? (
        <span className={`text-xl sm:text-2xl ${textColor}`}>
          {displayValue}
        </span>
      ) : (
        <input
          type="text"
          inputMode="numeric"
          pattern="[1-9]"
          value={userValue}
          onChange={handleChange}
          readOnly={isReadOnly || gamePhase === 'solved'}
          className={`w-full h-full text-center text-xl sm:text-2xl ${textColor} bg-transparent outline-none focus:ring-0 border-none p-0`}
          aria-label={`Cell at row ${cell.row + 1}, column ${cell.col + 1}. ${isClue ? `Clue value ${displayValue}` : 'Enter a number 1-9'}`}
          maxLength={1}
        />
      )}
    </div>
  );
};

export default GridCell;

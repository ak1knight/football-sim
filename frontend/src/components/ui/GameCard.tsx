import React from 'react';
import { Button } from './Button';

interface Team {
  id: string;
  city: string;
  name: string;
  abbreviation: string;
}

interface GameCardProps {
  gameId: string;
  homeTeam: Team;
  awayTeam: Team;
  homeScore?: number;
  awayScore?: number;
  status: 'scheduled' | 'completed';
  winner?: string;
  overtime?: boolean;
  onSimulate?: (gameId: string) => void;
  loading?: boolean;
  className?: string;
}

export const GameCard: React.FC<GameCardProps> = ({
  gameId,
  homeTeam,
  awayTeam,
  homeScore,
  awayScore,
  status,
  winner,
  overtime,
  onSimulate,
  loading = false,
  className = ''
}) => {
  return (
    <div className={`flex items-center justify-between p-4 bg-secondary-800 rounded-lg ${className}`}>
      <div className="flex-1">
        <div className="flex items-center space-x-4">
          <div className="text-center min-w-0 flex-1">
            <p className="text-sm text-secondary-400">Away</p>
            <p className="font-semibold text-white truncate">
              {awayTeam.city} {awayTeam.name}
            </p>
            {awayScore !== undefined && (
              <p className="text-lg font-bold text-white">{awayScore}</p>
            )}
          </div>
          <div className="text-secondary-400 font-medium">@</div>
          <div className="text-center min-w-0 flex-1">
            <p className="text-sm text-secondary-400">Home</p>
            <p className="font-semibold text-white truncate">
              {homeTeam.city} {homeTeam.name}
            </p>
            {homeScore !== undefined && (
              <p className="text-lg font-bold text-white">{homeScore}</p>
            )}
          </div>
        </div>
      </div>
      <div className="flex items-center space-x-3">
        {status === 'completed' ? (
          <div className="text-center">
            <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-green-900 text-green-300">
              Final{overtime && ' (OT)'}
            </span>
            {winner && (
              <p className="text-xs text-secondary-400 mt-1">
                Winner: {winner}
              </p>
            )}
          </div>
        ) : (
          onSimulate && (
            <Button
              variant="secondary"
              size="sm"
              onClick={() => onSimulate(gameId)}
              loading={loading}
            >
              Simulate
            </Button>
          )
        )}
      </div>
    </div>
  );
};
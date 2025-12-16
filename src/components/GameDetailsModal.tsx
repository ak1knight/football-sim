import React, { useState, useEffect } from 'react';
import { Button, Card, CardHeader, StatComparison, StatItem } from './ui';

interface GameDetailsModalProps {
  gameId: string;
  isOpen: boolean;
  onClose: () => void;
}

export const GameDetailsModal: React.FC<GameDetailsModalProps> = ({ gameId, isOpen, onClose }) => {
  const [gameDetails, setGameDetails] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedDrives, setExpandedDrives] = useState<Set<number>>(new Set());
  const [activeTab, setActiveTab] = useState<'stats' | 'drives' | 'plays'>('stats');

  useEffect(() => {
    if (isOpen && gameId) {
      loadGameDetails();
    }
  }, [isOpen, gameId]);

  const loadGameDetails = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await window.electronAPI.seasons.getGameDetails(gameId);
      if (response.success) {
        setGameDetails(response.data);
      } else {
        setError(response.error || 'Failed to load game details');
      }
    } catch (err) {
      setError('Error loading game details');
    } finally {
      setLoading(false);
    }
  };

  const toggleDrive = (driveNumber: number) => {
    const newExpanded = new Set(expandedDrives);
    if (newExpanded.has(driveNumber)) {
      newExpanded.delete(driveNumber);
    } else {
      newExpanded.add(driveNumber);
    }
    setExpandedDrives(newExpanded);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70" onClick={onClose}>
      <div 
        className="bg-secondary-900 rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-secondary-700">
          <h2 className="text-2xl font-bold text-white">Game Details</h2>
          <button
            onClick={onClose}
            className="text-secondary-400 hover:text-white transition-colors"
          >
            <span className="text-2xl">×</span>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading && (
            <div className="text-center py-12">
              <div className="text-primary-400 text-lg">Loading game details...</div>
            </div>
          )}

          {error && (
            <div className="bg-red-900/50 border border-red-500 rounded-lg p-4">
              <p className="text-red-200">{error}</p>
            </div>
          )}

          {gameDetails && (
            <div className="space-y-6">
              {/* Score Display */}
              <div className="bg-secondary-800 rounded-lg p-6">
                <div className="flex items-center justify-between text-center">
                  <div className="flex-1">
                    <div className="text-lg font-bold text-white">
                      {gameDetails.away_team.city} {gameDetails.away_team.name}
                    </div>
                    <div className="text-4xl font-bold text-primary-400 mt-3">
                      {gameDetails.away_score}
                    </div>
                  </div>
                  <div className="px-6">
                    <div className="text-secondary-400 font-medium text-lg">VS</div>
                  </div>
                  <div className="flex-1">
                    <div className="text-lg font-bold text-white">
                      {gameDetails.home_team.city} {gameDetails.home_team.name}
                    </div>
                    <div className="text-4xl font-bold text-primary-400 mt-3">
                      {gameDetails.home_score}
                    </div>
                  </div>
                </div>
                {gameDetails.weather && (
                  <div className="text-center mt-4 pt-4 border-t border-secondary-700">
                    <div className="text-secondary-400 text-sm">
                      Weather: {gameDetails.weather.condition} • {gameDetails.weather.temperature}°F • Wind {gameDetails.weather.wind_speed}mph {gameDetails.weather.wind_direction}
                    </div>
                  </div>
                )}
              </div>

              {/* Tabs */}
              <div className="flex space-x-2 border-b border-secondary-700">
                <button
                  onClick={() => setActiveTab('stats')}
                  className={`px-4 py-2 font-medium transition-colors ${
                    activeTab === 'stats'
                      ? 'text-primary-400 border-b-2 border-primary-400'
                      : 'text-secondary-400 hover:text-white'
                  }`}
                >
                  Statistics
                </button>
                <button
                  onClick={() => setActiveTab('drives')}
                  className={`px-4 py-2 font-medium transition-colors ${
                    activeTab === 'drives'
                      ? 'text-primary-400 border-b-2 border-primary-400'
                      : 'text-secondary-400 hover:text-white'
                  }`}
                >
                  Drive Summary
                </button>
                <button
                  onClick={() => setActiveTab('plays')}
                  className={`px-4 py-2 font-medium transition-colors ${
                    activeTab === 'plays'
                      ? 'text-primary-400 border-b-2 border-primary-400'
                      : 'text-secondary-400 hover:text-white'
                  }`}
                >
                  Key Plays
                </button>
              </div>

              {/* Tab Content */}
              {activeTab === 'stats' && gameDetails.detailed_stats && (
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h5 className="text-md font-medium text-white">Team Statistics</h5>
                    <div className="space-y-3">
                      <StatComparison
                        label="Total Yards"
                        awayValue={Math.round(gameDetails.detailed_stats.away.total_yards)}
                        homeValue={Math.round(gameDetails.detailed_stats.home.total_yards)}
                      />
                      <StatComparison
                        label="Passing Yards"
                        awayValue={Math.round(gameDetails.detailed_stats.away.passing_yards)}
                        homeValue={Math.round(gameDetails.detailed_stats.home.passing_yards)}
                      />
                      <StatComparison
                        label="Rushing Yards"
                        awayValue={Math.round(gameDetails.detailed_stats.away.rushing_yards)}
                        homeValue={Math.round(gameDetails.detailed_stats.home.rushing_yards)}
                      />
                      <StatComparison
                        label="Turnovers"
                        awayValue={gameDetails.detailed_stats.away.turnovers}
                        homeValue={gameDetails.detailed_stats.home.turnovers}
                        valueColor="text-red-400"
                      />
                      <StatComparison
                        label="Time of Possession"
                        awayValue={`${Math.floor(gameDetails.detailed_stats.away.time_of_possession / 60)}:${String(gameDetails.detailed_stats.away.time_of_possession % 60).padStart(2, '0')}`}
                        homeValue={`${Math.floor(gameDetails.detailed_stats.home.time_of_possession / 60)}:${String(gameDetails.detailed_stats.home.time_of_possession % 60).padStart(2, '0')}`}
                        valueColor="text-accent-400"
                      />
                    </div>
                  </div>
                  <div className="space-y-4">
                    <h5 className="text-md font-medium text-white">Play Breakdown</h5>
                    <div className="space-y-3">
                      <StatItem
                        label="Total Plays"
                        value={gameDetails.detailed_stats.total_plays}
                      />
                      <StatItem
                        label="Running Plays"
                        value={gameDetails.detailed_stats.play_type_counts?.run || 0}
                        valueColor="text-green-400"
                      />
                      <StatItem
                        label="Passing Plays"
                        value={gameDetails.detailed_stats.play_type_counts?.pass || 0}
                        valueColor="text-blue-400"
                      />
                      <StatItem
                        label="Total Drives"
                        value={gameDetails.detailed_stats.total_drives}
                      />
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'drives' && gameDetails.drives && (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-secondary-700">
                        <th className="text-left text-secondary-300 font-medium py-2 w-8"></th>
                        <th className="text-left text-secondary-300 font-medium py-2">#</th>
                        <th className="text-left text-secondary-300 font-medium py-2">Q</th>
                        <th className="text-left text-secondary-300 font-medium py-2">Team</th>
                        <th className="text-left text-secondary-300 font-medium py-2">Start</th>
                        <th className="text-left text-secondary-300 font-medium py-2">Result</th>
                        <th className="text-left text-secondary-300 font-medium py-2">Plays</th>
                        <th className="text-left text-secondary-300 font-medium py-2">Yards</th>
                        <th className="text-left text-secondary-300 font-medium py-2">Points</th>
                      </tr>
                    </thead>
                    <tbody>
                      {gameDetails.drives.map((drive: any, index: number) => (
                        <React.Fragment key={index}>
                          <tr 
                            className="border-b border-secondary-800 hover:bg-secondary-800/50 cursor-pointer transition-colors"
                            onClick={() => toggleDrive(drive.drive_number)}
                          >
                            <td className="py-2 text-secondary-400">
                              <span className="text-xs">
                                {expandedDrives.has(drive.drive_number) ? '▼' : '▶'}
                              </span>
                            </td>
                            <td className="py-2 text-white">{drive.drive_number}</td>
                            <td className="py-2 text-secondary-300">{drive.quarter}</td>
                            <td className="py-2 text-white">{drive.offense}</td>
                            <td className="py-2 text-secondary-300">{drive.starting_position}</td>
                            <td className="py-2">
                              <div>
                                <span className={`${
                                  drive.points > 0
                                    ? 'text-green-400'
                                    : drive.result.toLowerCase().includes('punt')
                                      ? 'text-secondary-300'
                                      : 'text-red-400'
                                }`}>
                                  {drive.result.replace('_', ' ')}
                                </span>
                                {drive.final_play_description && (
                                  <div className="text-xs text-secondary-400 mt-0.5">
                                    {drive.final_play_description}
                                  </div>
                                )}
                              </div>
                            </td>
                            <td className="py-2 text-secondary-300">{drive.total_plays}</td>
                            <td className="py-2 text-secondary-300">{drive.total_yards}</td>
                            <td className="py-2">
                              {drive.points > 0 ? (
                                <span className="text-green-400 font-medium">+{drive.points}</span>
                              ) : (
                                <span className="text-secondary-500">0</span>
                              )}
                            </td>
                          </tr>
                          {expandedDrives.has(drive.drive_number) && drive.play_log && (
                            <tr className="border-b border-secondary-800">
                              <td colSpan={9} className="py-3 px-4 bg-secondary-900/50">
                                <div className="space-y-1">
                                  <div className="text-xs font-medium text-secondary-400 mb-2">PLAY-BY-PLAY</div>
                                  {drive.play_log.map((play: any, playIndex: number) => (
                                    <div 
                                      key={playIndex} 
                                      className="flex items-center justify-between text-xs py-1.5 px-2 rounded hover:bg-secondary-800/50"
                                    >
                                      <div className="flex items-center space-x-3">
                                        <span className="text-secondary-500 w-12">{play.clock}</span>
                                        <span className="text-secondary-400 w-16">
                                          {play.down}{play.down === 1 ? 'st' : play.down === 2 ? 'nd' : play.down === 3 ? 'rd' : 'th'} & {play.yards_to_go}
                                        </span>
                                        <span className="text-secondary-400 w-12">at {play.start_field}</span>
                                        <span className={`font-medium ${
                                          play.play_type === 'run' ? 'text-green-400' : 
                                          play.play_type === 'pass' ? 'text-blue-400' : 
                                          play.play_type === 'turnover' ? 'text-red-400' : 
                                          'text-secondary-300'
                                        }`}>
                                          {play.play_type.toUpperCase()}
                                        </span>
                                      </div>
                                      <div className="flex items-center space-x-2">
                                        <span className={`font-medium ${
                                          play.yards_gained > 0 ? 'text-green-400' : 
                                          play.yards_gained < 0 ? 'text-red-400' : 
                                          'text-secondary-400'
                                        }`}>
                                          {play.yards_gained > 0 ? '+' : ''}{play.yards_gained} yds
                                        </span>
                                        <span className="text-secondary-500">→ {play.end_field}</span>
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </td>
                            </tr>
                          )}
                        </React.Fragment>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {activeTab === 'plays' && gameDetails.key_plays && (
                <div className="space-y-3">
                  {gameDetails.key_plays.slice(0, 15).map((play: any, index: number) => (
                    <div 
                      key={index}
                      className={`p-3 rounded-md border-l-4 ${
                        play.scoring_play 
                          ? 'bg-green-900/20 border-green-500' 
                          : 'bg-secondary-800 border-primary-500'
                      }`}
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="text-white font-medium">{play.description}</div>
                          <div className="text-secondary-400 text-sm mt-1">
                            Q{play.quarter} {play.time}
                            {play.yards && play.yards !== 0 && (
                              <span className="ml-2">• {play.yards > 0 ? '+' : ''}{play.yards} yards</span>
                            )}
                          </div>
                        </div>
                        {play.scoring_play && play.points && (
                          <div className="text-green-400 font-bold text-lg ml-4">
                            +{play.points}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end p-6 border-t border-secondary-700">
          <Button onClick={onClose} variant="secondary">
            Close
          </Button>
        </div>
      </div>
    </div>
  );
};

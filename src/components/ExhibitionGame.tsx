import React, { useEffect, useState } from 'react';
import { observer } from 'mobx-react-lite';
import { exhibitionStore } from '../stores';
import type { Team } from '../stores';
import { PageHeader, ErrorMessage, Button, Card, CardHeader, StatComparison, StatItem, LoadingMessage } from './ui';

const TeamSelector: React.FC<{
  label: string;
  teams: Team[];
  selectedTeam: Team | null;
  onSelect: (team: Team | null) => void;
  placeholder: string;
}> = ({ label, teams, selectedTeam, onSelect, placeholder }) => {
  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-white">{label}</label>
      <select
        value={selectedTeam?.id || ''}
        onChange={(e) => {
          const team = teams.find(t => t.id === e.target.value) || null;
          onSelect(team);
        }}
        className="w-full bg-secondary-700 border border-secondary-600 rounded-md px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
      >
        <option value="">{placeholder}</option>
        {teams.map((team) => (
          <option key={team.id} value={team.id}>
            {team.city} {team.name} ({team.abbreviation})
          </option>
        ))}
      </select>
    </div>
  );
};

const GameResult: React.FC = observer(() => {
  const { gameResult } = exhibitionStore;
  const [showDetailedStats, setShowDetailedStats] = useState(true);
  const [showKeyPlays, setShowKeyPlays] = useState(true);
  const [showDriveDetails, setShowDriveDetails] = useState(false);
  const [expandedDrives, setExpandedDrives] = useState<Set<number>>(new Set());

  if (!gameResult) return null;

  const toggleDrive = (driveNumber: number) => {
    const newExpanded = new Set(expandedDrives);
    if (newExpanded.has(driveNumber)) {
      newExpanded.delete(driveNumber);
    } else {
      newExpanded.add(driveNumber);
    }
    setExpandedDrives(newExpanded);
  };

  return (
    <div className="space-y-6">
      {/* Main Score Display */}
      <Card>
        <CardHeader title="Game Result" />
        
        <div className="bg-secondary-900 rounded-lg p-6">
          <div className="flex items-center justify-between text-center">
            {/* Away Team */}
            <div className="flex-1">
              <div className="text-lg font-bold text-white">
                {gameResult.awayTeam.city} {gameResult.awayTeam.name}
              </div>
              <div className="text-4xl font-bold text-primary-400 mt-3">
                {gameResult.awayScore}
              </div>
            </div>
            
            {/* VS */}
            <div className="px-6">
              <div className="text-secondary-400 font-medium text-lg">VS</div>
            </div>
            
            {/* Home Team */}
            <div className="flex-1">
              <div className="text-lg font-bold text-white">
                {gameResult.homeTeam.city} {gameResult.homeTeam.name}
              </div>
              <div className="text-4xl font-bold text-primary-400 mt-3">
                {gameResult.homeScore}
              </div>
            </div>
          </div>
          
          {/* Winner Display */}
          {gameResult.winner && (
            <div className="text-center mt-6 pt-4 border-t border-secondary-700">
              {gameResult.winner.tie ? (
                <div className="text-accent-400 font-medium">TIE GAME</div>
              ) : gameResult.winner.team ? (
                <div className="text-green-400 font-medium">
                  🏆 {gameResult.winner.team.city} {gameResult.winner.team.name} wins by {gameResult.winner.margin}
                </div>
              ) : null}
            </div>
          )}
          
          {/* Weather Conditions */}
          {gameResult.weather && (
            <div className="text-center mt-4 pt-4 border-t border-secondary-700">
              <div className="text-secondary-400 text-sm">
                Weather: {gameResult.weather.condition} • {gameResult.weather.temperature}°F • Wind {gameResult.weather.wind_speed}mph {gameResult.weather.wind_direction}
              </div>
            </div>
          )}
        </div>
     </Card>

      {/* Detailed Statistics */}
      {gameResult.detailedStats && (
        <Card>
          <CardHeader
            title="Game Statistics"
            actions={
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setShowDetailedStats(!showDetailedStats)}
              >
                {showDetailedStats ? '📊 Hide Stats' : '📊 Show Stats'}
              </Button>
            }
          />
          
          {showDetailedStats && (
            <div className="grid md:grid-cols-2 gap-6">
              {/* Team Stats Comparison */}
              <div className="space-y-4">
                <h5 className="text-md font-medium text-white">Team Statistics</h5>
                
                <div className="space-y-3">
                  <StatComparison
                    label="Total Yards"
                    awayValue={Math.round(gameResult.detailedStats.yards_gained.away)}
                    homeValue={Math.round(gameResult.detailedStats.yards_gained.home)}
                  />
                  
                  <StatComparison
                    label="Avg Yards/Play"
                    awayValue={gameResult.detailedStats.average_yards_per_play.away.toFixed(1)}
                    homeValue={gameResult.detailedStats.average_yards_per_play.home.toFixed(1)}
                  />
                  
                  <StatComparison
                    label="Turnovers"
                    awayValue={gameResult.detailedStats.turnovers.away}
                    homeValue={gameResult.detailedStats.turnovers.home}
                    valueColor="text-red-400"
                  />
                  
                  <StatComparison
                    label="Time of Possession"
                    awayValue={`${Math.floor(gameResult.detailedStats.time_of_possession.away / 60)}:${String(gameResult.detailedStats.time_of_possession.away % 60).padStart(2, '0')}`}
                    homeValue={`${Math.floor(gameResult.detailedStats.time_of_possession.home / 60)}:${String(gameResult.detailedStats.time_of_possession.home % 60).padStart(2, '0')}`}
                    valueColor="text-accent-400"
                  />
                </div>
              </div>
              
              {/* Play Type Breakdown */}
              <div className="space-y-4">
                <h5 className="text-md font-medium text-white">Play Breakdown</h5>
                
                <div className="space-y-3">
                  <StatItem
                    label="Total Plays"
                    value={gameResult.detailedStats.total_plays}
                  />
                  
                  <StatItem
                    label="Running Plays"
                    value={gameResult.detailedStats.plays_by_type.run}
                    valueColor="text-green-400"
                  />
                  
                  <StatItem
                    label="Passing Plays"
                    value={gameResult.detailedStats.plays_by_type.pass}
                    valueColor="text-blue-400"
                  />
                  
                  <StatItem
                    label="Total Drives"
                    value={gameResult.detailedStats.total_drives}
                  />
                </div>
              </div>
            </div>
          )}
        </Card>
      )}

      {/* Key Plays */}
      {gameResult.keyPlays && gameResult.keyPlays.length > 0 && (
        <Card>
          <CardHeader
            title="Key Plays"
            actions={
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setShowKeyPlays(!showKeyPlays)}
              >
                {showKeyPlays ? '⚡ Hide Plays' : '⚡ Show Plays'}
              </Button>
            }
          />
          
          {showKeyPlays && (
            <div className="space-y-3">
              {gameResult.keyPlays.slice(0, 8).map((play, index) => (
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
        </Card>
      )}

      {/* Drive Summary */}
      {gameResult.driveSummary && gameResult.driveSummary.length > 0 && (
        <Card>
          <CardHeader
            title="Drive Summary"
            actions={
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setShowDriveDetails(!showDriveDetails)}
              >
                {showDriveDetails ? '🚗 Hide Drives' : '🚗 Show Drives'}
              </Button>
            }
          />
          
          {showDriveDetails && (
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
                  {gameResult.driveSummary.map((drive, index) => (
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
                              {drive.play_log.map((play, playIndex) => (
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
        </Card>
      )}

      {/* New Game Button */}
      <div className="text-center">
        <Button
          onClick={() => exhibitionStore.resetGame()}
          size="lg"
        >
          🏈 Start New Game
        </Button>
      </div>
    </div>
  );
});

export const ExhibitionGame: React.FC = observer(() => {
  useEffect(() => {
    if (exhibitionStore.teams.length === 0) {
      exhibitionStore.loadTeams();
    }
  }, []);

  const handleSimulate = () => {
    exhibitionStore.simulateGame();
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Exhibition Game"
        description="Select two teams and simulate a detailed exhibition game with comprehensive statistics"
      />

      <Card>
        <CardHeader title="Team Selection" />
        
        {exhibitionStore.isLoadingTeams ? (
          <LoadingMessage message="Loading teams..." />
        ) : (
          <div className="grid md:grid-cols-2 gap-6">
            <TeamSelector
              label="Home Team"
              teams={exhibitionStore.availableHomeTeams}
              selectedTeam={exhibitionStore.selectedHomeTeam}
              onSelect={(team) => exhibitionStore.setSelectedHomeTeam(team)}
              placeholder="Select Home Team"
            />
            
            <TeamSelector
              label="Away Team"
              teams={exhibitionStore.availableAwayTeams}
              selectedTeam={exhibitionStore.selectedAwayTeam}
              onSelect={(team) => exhibitionStore.setSelectedAwayTeam(team)}
              placeholder="Select Away Team"
            />
          </div>
        )}

        <ErrorMessage message={exhibitionStore.error} />

        <div className="flex justify-center">
          <Button
            onClick={handleSimulate}
            disabled={!exhibitionStore.canSimulate}
            loading={exhibitionStore.isSimulating}
            size="lg"
          >
            🏈 Simulate Game
          </Button>
        </div>
      </Card>

      {exhibitionStore.gameResult && <GameResult />}
    </div>
  );
});
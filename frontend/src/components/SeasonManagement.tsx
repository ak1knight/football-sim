import React, { useEffect, useState } from 'react';
import { observer } from 'mobx-react-lite';
import { Input } from './ui/Input';
import { useContext } from 'react';
import { StoresContext } from '../stores';
import { PageHeader, ErrorMessage, Button, Card, CardHeader, LoadingMessage, GameCard } from './ui';

// Sub-components for each tab
const SeasonSetup: React.FC = observer(() => {
  const { appStore, seasonStore } = useContext(StoresContext);
  const [seasonName, setSeasonName] = useState(`NFL 2024 Season`);
  const { currentSeason, loading, error, teams, organizedTeams, isSeasonComplete } = seasonStore;

  const handleCreateSeason = async () => {
    const result = await seasonStore.createSeason(2024, undefined, seasonName);
    if (result.success) {
      appStore.setCurrentTab('Schedule');
    }
  };

  const handleStartNewSeason = async () => {
    const newYear = currentSeason ? currentSeason.season_year + 1 : new Date().getFullYear();
    const result = await seasonStore.startNewSeason(newYear);
    if (result.success) {
      appStore.setCurrentTab('Setup');
    }
  };

  return (
    <div className="space-y-6">
      {/* Season Status */}
      {currentSeason ? (
        <div className="space-y-4">
          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-white mb-2">
                  {currentSeason.season_year} Season
                </h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-secondary-400">Week:</span>
                    <span className="text-white ml-2">{currentSeason.current_week}</span>
                  </div>
                  <div>
                    <span className="text-secondary-400">Phase:</span>
                    <span className="text-white ml-2 capitalize">
                      {currentSeason.current_phase ? currentSeason.current_phase.replace('_', ' ') : ''}
                    </span>
                  </div>
                  <div>
                    <span className="text-secondary-400">Games:</span>
                    <span className="text-white ml-2">{currentSeason.completed_games}/{currentSeason.total_games}</span>
                  </div>
                  <div>
                    <span className="text-secondary-400">Progress:</span>
                    <span className="text-white ml-2">{currentSeason.completion_percentage}%</span>
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className="w-16 h-16 relative">
                  <div className="w-full h-full rounded-full border-4 border-secondary-600 flex items-center justify-center">
                    <span className="text-xs text-white font-semibold">
                      {currentSeason.completion_percentage}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* New Season Button - Show when season is complete */}
          {isSeasonComplete && (
            <div className="card p-6 text-center">
              <div className="text-4xl mb-4">🏆</div>
              <h3 className="text-lg font-semibold text-white mb-2">Season Complete!</h3>
              <p className="text-secondary-400 mb-4">
                Ready to start the {currentSeason.season_year + 1} season?
              </p>
              <Button
                onClick={handleStartNewSeason}
                loading={loading}
              >
                Start {currentSeason.season_year + 1} Season
              </Button>
            </div>
          )}
        </div>
      ) : (
        <div className="card p-8 text-center">
          <div className="text-6xl mb-4">🏈</div>
          <h2 className="text-xl font-semibold text-white mb-2">Create New Season</h2>
          <p className="text-secondary-400 mb-6">
            Start a new NFL season with automated scheduling and comprehensive simulation.
          </p>
          <div className="mb-4">
            <Input
              type="text"
              value={seasonName}
              onChange={e => setSeasonName(e.target.value)}
              placeholder="Season Name"
              disabled={loading}
              label="Season Name"
            />
          </div>
          <Button
            onClick={handleCreateSeason}
            loading={loading}
          >
            Create 2024 Season
          </Button>
        </div>
      )}

      {/* Teams Overview */}
      {Object.keys(organizedTeams).length > 0 && (
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-white mb-4">League Structure</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {Object.entries(organizedTeams).map(([conference, divisions]) => (
              <div key={conference} className="space-y-3">
                <h4 className="text-md font-semibold text-primary-400">{conference}</h4>
                {Object.entries(divisions).map(([division, divTeams]) => (
                  <div key={division} className="ml-4">
                    <h5 className="text-sm font-medium text-secondary-300 mb-1">{division}</h5>
                    <div className="ml-4 space-y-1">
                      {divTeams.map((team) => (
                        <div key={team.abbreviation} className="text-sm text-secondary-400">
                          {team.city} {team.name} ({team.abbreviation})
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      )}

      <ErrorMessage message={error} />
    </div>
  );
});

const SeasonSchedule: React.FC = observer(() => {
  const { seasonStore } = useContext(StoresContext);
  const {
    currentSeason, nextGames, currentWeekGames, selectedWeek,
    loading, error, scheduledGamesCount
  } = seasonStore;

  useEffect(() => {
    if (currentSeason) {
      seasonStore.loadNextGames();
      seasonStore.loadWeekGames(currentSeason.current_week);
    }
  }, [currentSeason]);

  const handleSimulateGame = async (gameId: string) => {
    await seasonStore.simulateGame(gameId);
    // Refresh current week games after simulation
    if (currentSeason) {
      await seasonStore.loadWeekGames(currentSeason.current_week);
    }
  };

  const handleSimulateWeek = async () => {
    if (!currentSeason) return;
    await seasonStore.simulateWeek(currentSeason.current_week);
    // Reload the current week after simulation
    await seasonStore.loadWeekGames(currentSeason.current_week);
  };

  const handleLoadWeek = async (week: number) => {
    await seasonStore.loadWeekGames(week);
  };

  const canSimulateWeek = (week: number) => {
    if (!currentSeason) return false;
    // Can only simulate current week or previous weeks that aren't complete
    return week <= currentSeason.current_week;
  };

  if (!currentSeason) {
    return (
      <div className="card p-8 text-center">
        <div className="text-6xl mb-4">📅</div>
        <h2 className="text-xl font-semibold text-white mb-2">No Active Season</h2>
        <p className="text-secondary-400">Create a season first to view the schedule.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Quick Actions */}
      <Card>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-semibold text-white mb-1">Week {currentSeason.current_week}</h2>
            <p className="text-secondary-400">
              {scheduledGamesCount} games remaining to simulate
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Button
              onClick={handleSimulateWeek}
              disabled={loading || scheduledGamesCount === 0}
              loading={loading}
            >
              Simulate Week {currentSeason.current_week}
            </Button>
            <Button
              variant="secondary"
              onClick={async () => {
                await seasonStore.simulateToWeek(Math.min(currentSeason.current_week + 2, 18));
                if (currentSeason) {
                  await seasonStore.loadWeekGames(seasonStore.currentSeason?.current_week || currentSeason.current_week);
                }
              }}
              disabled={loading || scheduledGamesCount === 0 || currentSeason.current_week >= 18}
            >
              Simulate 3 Weeks
            </Button>
            <Button
              variant="accent"
              onClick={async () => {
                await seasonStore.simulateFullSeason();
                if (seasonStore.currentSeason) {
                  await seasonStore.loadWeekGames(seasonStore.currentSeason.current_week);
                }
              }}
              disabled={loading || currentSeason.current_phase !== 'regular_season' || scheduledGamesCount === 0}
            >
              Simulate Rest of Season
            </Button>
          </div>
        </div>
      </Card>

      {/* Week Selector */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Browse Schedule</h3>
        <div className="flex flex-wrap gap-2 mb-4">
          {Array.from({ length: 18 }, (_, i) => i + 1).map((week) => {
            const isCurrentWeek = week === currentSeason.current_week;
            const isPastWeek = week < currentSeason.current_week;
            const isFutureWeek = week > currentSeason.current_week;
            
            return (
              <button
                key={week}
                onClick={() => handleLoadWeek(week)}
                className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                  selectedWeek === week
                    ? 'bg-primary-600 text-white'
                    : isPastWeek
                    ? 'bg-green-900 text-green-300 hover:bg-green-800'
                    : isCurrentWeek
                    ? 'bg-yellow-900 text-yellow-300 hover:bg-yellow-800'
                    : 'bg-secondary-700 text-secondary-300 hover:bg-secondary-600'
                }`}
                title={
                  isPastWeek ? 'Completed week' :
                  isCurrentWeek ? 'Current week' :
                  'Future week'
                }
              >
                Week {week}
                {isPastWeek && ' ✓'}
                {isCurrentWeek && ' ⭐'}
              </button>
            );
          })}
        </div>
      </div>

      {/* Games List */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-white mb-4">
          Week {selectedWeek} Games ({currentWeekGames.length})
        </h3>
        {currentWeekGames.length > 0 ? (
          <div className="space-y-3">
            {currentWeekGames.map((game) => (
              <div
                key={game.game_id}
                className="flex items-center justify-between p-4 bg-secondary-800 rounded-lg"
              >
                <div className="flex-1">
                  <div className="flex items-center space-x-4">
                    <div className="text-center min-w-0 flex-1">
                      <p className="text-sm text-secondary-400">Away</p>
                      <p className="font-semibold text-white truncate">
                        {game.away_team.city} {game.away_team.name}
                      </p>
                      {game.away_score !== undefined && (
                        <p className="text-lg font-bold text-white">{game.away_score}</p>
                      )}
                    </div>
                    <div className="text-secondary-400 font-medium">@</div>
                    <div className="text-center min-w-0 flex-1">
                      <p className="text-sm text-secondary-400">Home</p>
                      <p className="font-semibold text-white truncate">
                        {game.home_team.city} {game.home_team.name}
                      </p>
                      {game.home_score !== undefined && (
                        <p className="text-lg font-bold text-white">{game.home_score}</p>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  {game.status === 'completed' ? (
                    <div className="text-center">
                      <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-green-900 text-green-300">
                        Final{game.overtime && ' (OT)'}
                      </span>
                      {game.winner && (
                        <p className="text-xs text-secondary-400 mt-1">
                          Winner: {game.winner}
                        </p>
                      )}
                    </div>
                  ) : (
                    <button
                      onClick={() => handleSimulateGame(game.game_id)}
                      disabled={loading}
                      className="btn-secondary text-sm"
                    >
                      Simulate
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-secondary-400 text-center py-8">No games scheduled for this week.</p>
        )}
      </div>

      {error && (
        <div className="bg-red-900/50 border border-red-500 rounded-lg p-4">
          <p className="text-red-200">{error}</p>
        </div>
      )}
    </div>
  );
});

const SeasonStandings: React.FC = observer(() => {
  const { seasonStore } = useContext(StoresContext);
  const { standings, standingsByDivision, loading, error } = seasonStore;

  useEffect(() => {
    seasonStore.loadStandings(true);
  }, []);

  const toggleStandingsView = async () => {
    const newView = !standingsByDivision;
    await seasonStore.loadStandings(newView);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card p-6">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-white">League Standings</h2>
          <button
            onClick={toggleStandingsView}
            className="btn-secondary"
          >
            View by {standingsByDivision ? 'Conference' : 'Division'}
          </button>
        </div>
      </div>

      {/* Standings */}
      {Object.keys(standings).length > 0 ? (
        <div className="space-y-6">
          {Object.entries(standings).map(([divisionOrConf, teams]) => (
            <div key={divisionOrConf} className="card p-6">
              <h3 className="text-lg font-semibold text-white mb-4">{divisionOrConf}</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-secondary-600">
                      <th className="text-left py-2 text-secondary-400">Team</th>
                      <th className="text-center py-2 text-secondary-400">W</th>
                      <th className="text-center py-2 text-secondary-400">L</th>
                      <th className="text-center py-2 text-secondary-400">T</th>
                      <th className="text-center py-2 text-secondary-400">PCT</th>
                      <th className="text-center py-2 text-secondary-400">PF</th>
                      <th className="text-center py-2 text-secondary-400">PA</th>
                      <th className="text-center py-2 text-secondary-400">DIFF</th>
                      <th className="text-center py-2 text-secondary-400">DIV</th>
                      <th className="text-center py-2 text-secondary-400">CONF</th>
                    </tr>
                  </thead>
                  <tbody>
                    {teams.map((team, index) => (
                      <tr key={team.team.abbreviation} className="border-b border-secondary-700/50">
                        <td className="py-2">
                          <div className="flex items-center">
                            <span className="w-6 text-secondary-400 text-xs">{index + 1}</span>
                            <span className="font-medium text-white">
                              {team.team.city} {team.team.name}
                            </span>
                            <span className="ml-2 text-secondary-400">({team.team.abbreviation})</span>
                          </div>
                        </td>
                        <td className="text-center py-2 text-white font-medium">{team.wins}</td>
                        <td className="text-center py-2 text-white font-medium">{team.losses}</td>
                        <td className="text-center py-2 text-white font-medium">{team.ties}</td>
                        <td className="text-center py-2 text-white font-medium">{team.win_percentage}</td>
                        <td className="text-center py-2 text-secondary-300">{team.points_for}</td>
                        <td className="text-center py-2 text-secondary-300">{team.points_against}</td>
                        <td className={`text-center py-2 font-medium ${
                          team.point_differential > 0 
                            ? 'text-green-400' 
                            : team.point_differential < 0 
                            ? 'text-red-400' 
                            : 'text-secondary-300'
                        }`}>
                          {team.point_differential > 0 ? '+' : ''}{team.point_differential}
                        </td>
                        <td className="text-center py-2 text-secondary-300">{team.division_record}</td>
                        <td className="text-center py-2 text-secondary-300">{team.conference_record}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="card p-8 text-center">
          <div className="text-6xl mb-4">📊</div>
          <h2 className="text-xl font-semibold text-white mb-2">No Standings Available</h2>
          <p className="text-secondary-400">Create and simulate some games to see standings.</p>
        </div>
      )}

      {error && (
        <div className="bg-red-900/50 border border-red-500 rounded-lg p-4">
          <p className="text-red-200">{error}</p>
        </div>
      )}
    </div>
  );
});

const SeasonPlayoffs: React.FC = observer(() => {
  const { appStore, seasonStore } = useContext(StoresContext);
  const {
    currentSeason, playoffBracket, nextPlayoffGames, playoffSimulationResults,
    loading, error, isInPlayoffs
  } = seasonStore;

  useEffect(() => {
    if (isInPlayoffs) {
      seasonStore.loadPlayoffBracket();
      seasonStore.loadNextPlayoffGames();
    }
  }, [isInPlayoffs]);

  // Get current round games from the bracket
  const getCurrentRoundGames = () => {
    if (!playoffBracket) return [];
    
    const currentRound = playoffBracket.current_round;
    switch (currentRound) {
      case 'wild_card':
        return playoffBracket.wild_card_games || [];
      case 'divisional':
        return playoffBracket.divisional_games || [];
      case 'conference_championship':
        return playoffBracket.conference_championship_games || [];
      case 'super_bowl':
        return playoffBracket.super_bowl ? [playoffBracket.super_bowl] : [];
      default:
        return [];
    }
  };

  const currentRoundGames = getCurrentRoundGames();

  const handleSimulatePlayoffGame = async (gameId: string) => {
    await seasonStore.simulatePlayoffGame(gameId);
  };

  const getRoundName = (round: string) => {
    switch (round) {
      case 'wild_card': return 'Wild Card';
      case 'divisional': return 'Divisional';
      case 'conference_championship': return 'Conference Championship';
      case 'super_bowl': return 'Super Bowl';
      default: return round.replace('_', ' ');
    }
  };

  const getRoundColor = (round: string) => {
    switch (round) {
      case 'wild_card': return 'bg-blue-900 text-blue-300';
      case 'divisional': return 'bg-green-900 text-green-300';
      case 'conference_championship': return 'bg-purple-900 text-purple-300';
      case 'super_bowl': return 'bg-gold-900 text-gold-300';
      default: return 'bg-secondary-700 text-secondary-300';
    }
  };

  if (!currentSeason) {
    return (
      <div className="card p-8 text-center">
        <div className="text-6xl mb-4">🏆</div>
        <h2 className="text-xl font-semibold text-white mb-2">No Active Season</h2>
        <p className="text-secondary-400">Create a season first to view playoffs.</p>
      </div>
    );
  }

  if (!isInPlayoffs) {
    return (
      <div className="space-y-6">
        <div className="card p-8 text-center">
          <div className="text-6xl mb-4">🏆</div>
          <h2 className="text-xl font-semibold text-white mb-2">Playoff Preview</h2>
          <p className="text-secondary-400 mb-6">
            Complete the regular season to generate the playoff bracket and begin postseason simulation.
          </p>
          <div className="space-y-3 text-left max-w-md mx-auto">
            <div className="flex items-center text-secondary-300">
              <span className="w-2 h-2 bg-primary-500 rounded-full mr-3"></span>
              Automatic playoff seeding (7 teams per conference)
            </div>
            <div className="flex items-center text-secondary-300">
              <span className="w-2 h-2 bg-primary-500 rounded-full mr-3"></span>
              Wild Card, Divisional, and Championship rounds
            </div>
            <div className="flex items-center text-secondary-300">
              <span className="w-2 h-2 bg-primary-500 rounded-full mr-3"></span>
              Super Bowl championship simulation
            </div>
            <div className="flex items-center text-secondary-300">
              <span className="w-2 h-2 bg-primary-500 rounded-full mr-3"></span>
              Home field advantage based on seeding
            </div>
          </div>
          <div className="mt-8">
            <p className="text-sm text-secondary-400">
              Current Phase: <span className="capitalize text-white">
                {currentSeason.current_phase ? currentSeason.current_phase.replace('_', ' ') : ''}
              </span>
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Playoff Header */}
      <div className="card p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-white mb-1">
              {currentSeason.season_year} NFL Playoffs
            </h2>
            <p className="text-secondary-400">
              Current Round: <span className="capitalize text-white">
                {getRoundName(playoffBracket?.current_round || '')}
              </span>
            </p>
          </div>
          <div className="text-right">
            <div className="text-lg font-semibold text-white">
              {nextPlayoffGames.length} Games Remaining
            </div>
            {playoffBracket?.is_complete && (
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gold-900 text-gold-300">
                Playoffs Complete
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Current Round Games */}
      {currentRoundGames.length > 0 && (
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-white mb-4">
            {getRoundName(playoffBracket?.current_round || '')} Games
          </h3>
          <div className="space-y-3">
            {currentRoundGames.map((game) => (
              <div
                key={game.game_id}
                className="flex items-center justify-between p-4 bg-secondary-800 rounded-lg"
              >
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getRoundColor(game.round)}`}>
                      {getRoundName(game.round)} - {game.conference}
                    </span>
                    <span className="text-xs text-secondary-400">
                      {game.scheduled_date && new Date(game.scheduled_date).toLocaleDateString()}
                    </span>
                  </div>
                  
                  {game.is_ready_to_play && game.home_team && game.away_team ? (
                    <div className="flex items-center space-x-4">
                      <div className="text-center flex-1">
                        <p className="text-xs text-secondary-400">
                          ({game.higher_seed?.seed}) Away
                        </p>
                        <p className="font-semibold text-white">
                          {game.away_team.city} {game.away_team.name}
                        </p>
                        {game.away_score !== undefined && (
                          <p className="text-lg font-bold text-white">{game.away_score}</p>
                        )}
                      </div>
                      <div className="text-secondary-400 font-medium">@</div>
                      <div className="text-center flex-1">
                        <p className="text-xs text-secondary-400">
                          ({game.lower_seed?.seed}) Home
                        </p>
                        <p className="font-semibold text-white">
                          {game.home_team.city} {game.home_team.name}
                        </p>
                        {game.home_score !== undefined && (
                          <p className="text-lg font-bold text-white">{game.home_score}</p>
                        )}
                      </div>
                    </div>
                  ) : (
                    <div className="text-center text-secondary-400">
                      {game.matchup_description}
                    </div>
                  )}
                </div>
                
                <div className="flex items-center space-x-3">
                  {game.completed ? (
                    <div className="text-center">
                      <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-green-900 text-green-300">
                        Final{game.overtime && ' (OT)'}
                      </span>
                      {game.winner && (
                        <p className="text-xs text-secondary-400 mt-1">
                          Winner: {game.winner}
                        </p>
                      )}
                    </div>
                  ) : game.is_ready_to_play ? (
                    <button
                      onClick={() => handleSimulatePlayoffGame(game.game_id)}
                      disabled={loading}
                      className="btn-primary text-sm"
                    >
                      {loading ? 'Simulating...' : 'Simulate'}
                    </button>
                  ) : (
                    <span className="text-xs text-secondary-400 px-3 py-1 bg-secondary-700 rounded">
                      Waiting for previous round
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Playoff Bracket Overview */}
      {playoffBracket && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* AFC Teams */}
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-white mb-4">AFC Playoff Teams</h3>
            <div className="space-y-2">
              {playoffBracket.afc_teams.map((team) => (
                <div key={team.team.abbreviation} className="flex items-center justify-between p-3 bg-secondary-800 rounded">
                  <div className="flex items-center space-x-3">
                    <span className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center text-sm font-bold text-white">
                      {team.seed}
                    </span>
                    <div>
                      <p className="font-semibold text-white">
                        {team.team.city} {team.team.name}
                      </p>
                      <p className="text-xs text-secondary-400">
                        {team.division_winner ? 'Division Winner' : 'Wild Card'} • {team.record}
                      </p>
                    </div>
                  </div>
                  <div className="text-right text-sm text-secondary-300">
                    <p>{team.points_for} PF</p>
                    <p className={team.point_differential >= 0 ? 'text-green-400' : 'text-red-400'}>
                      {team.point_differential > 0 ? '+' : ''}{team.point_differential}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* NFC Teams */}
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-white mb-4">NFC Playoff Teams</h3>
            <div className="space-y-2">
              {playoffBracket.nfc_teams.map((team) => (
                <div key={team.team.abbreviation} className="flex items-center justify-between p-3 bg-secondary-800 rounded">
                  <div className="flex items-center space-x-3">
                    <span className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center text-sm font-bold text-white">
                      {team.seed}
                    </span>
                    <div>
                      <p className="font-semibold text-white">
                        {team.team.city} {team.team.name}
                      </p>
                      <p className="text-xs text-secondary-400">
                        {team.division_winner ? 'Division Winner' : 'Wild Card'} • {team.record}
                      </p>
                    </div>
                  </div>
                  <div className="text-right text-sm text-secondary-300">
                    <p>{team.points_for} PF</p>
                    <p className={team.point_differential >= 0 ? 'text-green-400' : 'text-red-400'}>
                      {team.point_differential > 0 ? '+' : ''}{team.point_differential}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Championship Results */}
      {(playoffBracket?.afc_champion || playoffBracket?.nfc_champion || playoffBracket?.super_bowl_champion) && (
        <div className="space-y-4">
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Championship Results</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {playoffBracket.afc_champion && (
                <div className="text-center">
                  <p className="text-sm text-secondary-400 mb-1">AFC Champion</p>
                  <p className="font-semibold text-white">
                    ({playoffBracket.afc_champion.seed}) {playoffBracket.afc_champion.team.city} {playoffBracket.afc_champion.team.name}
                  </p>
                </div>
              )}
              {playoffBracket.nfc_champion && (
                <div className="text-center">
                  <p className="text-sm text-secondary-400 mb-1">NFC Champion</p>
                  <p className="font-semibold text-white">
                    ({playoffBracket.nfc_champion.seed}) {playoffBracket.nfc_champion.team.city} {playoffBracket.nfc_champion.team.name}
                  </p>
                </div>
              )}
              {playoffBracket.super_bowl_champion && (
                <div className="text-center">
                  <p className="text-sm text-gold-400 mb-1">🏆 Super Bowl Champion</p>
                  <p className="font-bold text-gold-300 text-lg">
                    ({playoffBracket.super_bowl_champion.seed}) {playoffBracket.super_bowl_champion.team.city} {playoffBracket.super_bowl_champion.team.name}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* New Season Button - Show when playoffs are complete */}
          {playoffBracket?.is_complete && (
            <div className="card p-6 text-center">
              <div className="text-6xl mb-4">🎉</div>
              <h3 className="text-xl font-semibold text-white mb-2">Congratulations!</h3>
              <p className="text-secondary-400 mb-4">
                The {currentSeason?.season_year} season is complete. Ready for next year?
              </p>
              <button
                onClick={async () => {
                  const newYear = currentSeason ? currentSeason.season_year + 1 : new Date().getFullYear();
                  const result = await seasonStore.startNewSeason(newYear);
                  if (result.success) {
                    appStore.setCurrentTab('Setup');
                  }
                }}
                disabled={loading}
                className="btn-primary text-lg px-8 py-3"
              >
                {loading ? 'Creating New Season...' : `Start ${currentSeason ? currentSeason.season_year + 1 : new Date().getFullYear()} Season`}
              </button>
            </div>
          )}
        </div>
      )}

      {error && (
        <div className="bg-red-900/50 border border-red-500 rounded-lg p-4">
          <p className="text-red-200">{error}</p>
        </div>
      )}
    </div>
  );
});

// Main component
export const SeasonManagement: React.FC = observer(() => {
  const { appStore, seasonStore } = useContext(StoresContext);
  const { currentSection } = appStore;
  const activeTab = appStore.currentTab || 'Setup';

  // Load all seasons and select the most recent on mount/section change
  useEffect(() => {
    if (currentSection === 'season') {
      const loadInitialData = async () => {
        await seasonStore.fetchAllSeasons();
        if (seasonStore.selectedSeasonId) {
          await seasonStore.loadSeasonStatus(seasonStore.selectedSeasonId);
        }
        await seasonStore.loadTeams();
      };
      loadInitialData();
    }
  }, [currentSection, seasonStore]);

  // Update current season when selectedSeasonId changes
  useEffect(() => {
    if (seasonStore.selectedSeasonId) {
      seasonStore.loadSeasonStatus(seasonStore.selectedSeasonId);
      seasonStore.loadNextGames();
      if (seasonStore.currentSeason) {
        seasonStore.loadWeekGames(seasonStore.currentSeason.current_week);
        seasonStore.loadStandings(true);
      }
    }
  }, [seasonStore.selectedSeasonId]);

  // Force component re-render when switching to season section
  useEffect(() => {
    if (currentSection === 'season') {
      // Clear any errors and reset state when entering season section
      seasonStore.setError(null);
    }
  }, [currentSection, seasonStore]);

  // Ensure games are loaded when switching to the Schedule tab
  useEffect(() => {
    if (activeTab === 'Schedule' && seasonStore.currentSeason) {
      seasonStore.loadNextGames();
      seasonStore.loadWeekGames(seasonStore.currentSeason.current_week);
    }
  }, [activeTab, seasonStore]);

  const tabs = appStore.sectionTabs;

  const renderContent = () => {
    switch (activeTab) {
      case 'Setup':
        return <SeasonSetup />;
      case 'Schedule':
        return <SeasonSchedule />;
      case 'Standings':
        return <SeasonStandings />;
      case 'Playoffs':
        return <SeasonPlayoffs />;
      default:
        return <SeasonSetup />;
    }
  };

  // Season selector UI
  const handleSeasonChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    seasonStore.setSelectedSeason(e.target.value);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Season Simulation"
        description="Manage and simulate complete NFL seasons with comprehensive statistics"
      />

      {/* Season Selector */}
      <div className="flex items-center gap-4">
        <label htmlFor="season-select" className="text-secondary-300 font-medium">
          Select Season:
        </label>
        <select
          id="season-select"
          value={seasonStore.selectedSeasonId || ''}
          onChange={handleSeasonChange}
          className="bg-secondary-800 text-white rounded px-3 py-2"
          disabled={seasonStore.allSeasons.length === 0}
        >
          {seasonStore.allSeasons.length === 0 ? (
            <option value="">No seasons available</option>
          ) : (
            seasonStore.allSeasons.map(season => (
              <option key={season.id} value={season.id}>
                {season.season_year} ({season.schedule_type})
              </option>
            ))
          )}
        </select>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 bg-secondary-800 p-1 rounded-lg">
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => appStore.setCurrentTab(tab)}
            className={`flex-1 py-2 px-4 text-sm font-medium rounded-md transition-colors ${
              activeTab === tab
                ? 'bg-primary-600 text-white'
                : 'text-secondary-300 hover:text-white hover:bg-secondary-700'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {seasonStore.allSeasons.length === 0 ? (
        <div className="card p-8 text-center">
          <div className="text-6xl mb-4">🏈</div>
          <h2 className="text-xl font-semibold text-white mb-2">No Seasons Found</h2>
          <p className="text-secondary-400 mb-6">
            Create a new season to get started.
          </p>
        </div>
      ) : (
        renderContent()
      )}
    </div>
  );
});
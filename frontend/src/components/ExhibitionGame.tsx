/**
 * Exhibition Game component - allows users to simulate games between any two teams.
 */

import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import type { Team, Weather, GameResult } from '../types/api';
import './ExhibitionGame.css';

const ExhibitionGame: React.FC = () => {
  const [teams, setTeams] = useState<Team[]>([]);
  const [homeTeam, setHomeTeam] = useState<string>('');
  const [awayTeam, setAwayTeam] = useState<string>('');
  const [weather, setWeather] = useState<Weather>({
    condition: 'clear',
    temperature: 72,
    wind_speed: 5,
    wind_direction: 'N'
  });
  const [gameResult, setGameResult] = useState<GameResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showDetailedStats, setShowDetailedStats] = useState(true);

  // Load teams on component mount
  useEffect(() => {
    const loadTeams = async () => {
      try {
        const response = await apiService.getTeams();
        if (response.success) {
          setTeams(response.teams);
        } else {
          setError(response.error || 'Failed to load teams');
        }
      } catch (err) {
        setError('Failed to connect to server');
        console.error('Error loading teams:', err);
      }
    };

    loadTeams();
  }, []);

  const handleSimulateGame = async () => {
    if (!homeTeam || !awayTeam) {
      setError('Please select both teams');
      return;
    }

    if (homeTeam === awayTeam) {
      setError('Teams must be different');
      return;
    }

    setIsLoading(true);
    setError(null);
    setGameResult(null);

    try {
      const response = await apiService.simulateExhibitionGame({
        home_team: homeTeam,
        away_team: awayTeam,
        weather,
        game_settings: {
          overtime: true,
          detailed_stats: showDetailedStats
        }
      });

      if (response.success && response.game_result) {
        setGameResult(response.game_result);
      } else {
        setError(response.error || 'Failed to simulate game');
      }
    } catch (err) {
      setError('Failed to simulate game');
      console.error('Error simulating game:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const getTeamDisplayName = (abbr: string): string => {
    const team = teams.find(t => t.abbreviation === abbr);
    return team ? `${team.city} ${team.name}` : abbr;
  };

  return (
    <div className="exhibition-game">
      <h1>🏈 Exhibition Game Simulator</h1>
      <p>Pick any two teams and simulate a game with custom weather conditions!</p>

      {error && (
        <div className="error-message">
          ❌ {error}
        </div>
      )}

      <div className="game-setup">
        <div className="team-selection">
          <h2>Team Selection</h2>
          
          <div className="team-selectors">
            <div className="team-selector">
              <label htmlFor="away-team">Away Team:</label>
              <select
                id="away-team"
                value={awayTeam}
                onChange={(e) => setAwayTeam(e.target.value)}
                disabled={isLoading}
              >
                <option value="">Select Away Team</option>
                {teams.map(team => (
                  <option key={team.abbreviation} value={team.abbreviation}>
                    {team.city} {team.name} ({team.abbreviation})
                  </option>
                ))}
              </select>
            </div>

            <div className="vs-display">@</div>

            <div className="team-selector">
              <label htmlFor="home-team">Home Team:</label>
              <select
                id="home-team"
                value={homeTeam}
                onChange={(e) => setHomeTeam(e.target.value)}
                disabled={isLoading}
              >
                <option value="">Select Home Team</option>
                {teams.map(team => (
                  <option key={team.abbreviation} value={team.abbreviation}>
                    {team.city} {team.name} ({team.abbreviation})
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        <div className="weather-settings">
          <h2>Weather Conditions</h2>
          
          <div className="weather-controls">
            <div className="weather-control">
              <label htmlFor="condition">Condition:</label>
              <select
                id="condition"
                value={weather.condition}
                onChange={(e) => setWeather({
                  ...weather,
                  condition: e.target.value as Weather['condition']
                })}
                disabled={isLoading}
              >
                <option value="clear">☀️ Clear</option>
                <option value="cloudy">☁️ Cloudy</option>
                <option value="rain">🌧️ Rainy</option>
                <option value="snow">❄️ Snowy</option>
                <option value="windy">💨 Windy</option>
              </select>
            </div>

            <div className="weather-control">
              <label htmlFor="temperature">Temperature (°F):</label>
              <input
                id="temperature"
                type="number"
                min="0"
                max="120"
                value={weather.temperature}
                onChange={(e) => setWeather({
                  ...weather,
                  temperature: parseInt(e.target.value) || 72
                })}
                disabled={isLoading}
              />
            </div>

            <div className="weather-control">
              <label htmlFor="wind-speed">Wind Speed (mph):</label>
              <input
                id="wind-speed"
                type="number"
                min="0"
                max="50"
                value={weather.wind_speed}
                onChange={(e) => setWeather({
                  ...weather,
                  wind_speed: parseInt(e.target.value) || 0
                })}
                disabled={isLoading}
              />
            </div>

            <div className="weather-control">
              <label htmlFor="wind-direction">Wind Direction:</label>
              <select
                id="wind-direction"
                value={weather.wind_direction}
                onChange={(e) => setWeather({
                  ...weather,
                  wind_direction: e.target.value
                })}
                disabled={isLoading}
              >
                <option value="N">North</option>
                <option value="NE">Northeast</option>
                <option value="E">East</option>
                <option value="SE">Southeast</option>
                <option value="S">South</option>
                <option value="SW">Southwest</option>
                <option value="W">West</option>
                <option value="NW">Northwest</option>
              </select>
            </div>
          </div>
        </div>

        <div className="game-options">
          <label>
            <input
              type="checkbox"
              checked={showDetailedStats}
              onChange={(e) => setShowDetailedStats(e.target.checked)}
              disabled={isLoading}
            />
            Show detailed statistics
          </label>
        </div>

        <button
          className="simulate-button"
          onClick={handleSimulateGame}
          disabled={isLoading || !homeTeam || !awayTeam}
        >
          {isLoading ? '🎮 Simulating...' : '🏈 Simulate Game'}
        </button>
      </div>

      {gameResult && (
        <div className="game-result">
          <h2>Game Result</h2>
          
          <div className="score-display">
            <div className="team-score">
              <h3>{getTeamDisplayName(gameResult.away_team.abbreviation)}</h3>
              <div className="score">{gameResult.away_team.score}</div>
            </div>
            
            <div className="vs">Final</div>
            
            <div className="team-score">
              <h3>{getTeamDisplayName(gameResult.home_team.abbreviation)}</h3>
              <div className="score">{gameResult.home_team.score}</div>
            </div>
          </div>

          <div className="game-info">
            {gameResult.winner.tie ? (
              <p>🤝 The game ended in a tie!</p>
            ) : (
              <p>
                🏆 <strong>{getTeamDisplayName(gameResult.winner.team!.abbreviation)}</strong> wins by {gameResult.winner.margin} points!
              </p>
            )}
            
            {gameResult.overtime && <p>⏰ Game went to overtime</p>}
            <p>🕐 Game duration: {gameResult.game_duration} minutes</p>
            <p>
              🌤️ Weather: {gameResult.weather.condition} | {gameResult.weather.temperature}°F | 
              Wind: {gameResult.weather.wind_speed} mph {gameResult.weather.wind_direction}
            </p>
          </div>

          {gameResult.detailed_stats && (
            <div className="detailed-stats">
              <h3>📊 Detailed Statistics</h3>
              
              {/* Game Overview Stats */}
              <div className="stats-section">
                <h4>Game Overview</h4>
                <div className="stats-grid">
                  <div className="stat">
                    <span>Total Plays:</span>
                    <span>{gameResult.detailed_stats.total_plays}</span>
                  </div>
                  <div className="stat">
                    <span>Total Drives:</span>
                    <span>{gameResult.detailed_stats.total_drives}</span>
                  </div>
                  <div className="stat">
                    <span>Turnovers:</span>
                    <span>{gameResult.detailed_stats.turnovers.away} - {gameResult.detailed_stats.turnovers.home}</span>
                  </div>
                  <div className="stat">
                    <span>Time of Possession:</span>
                    <span>{gameResult.detailed_stats.time_of_possession.away}m - {gameResult.detailed_stats.time_of_possession.home}m</span>
                  </div>
                </div>
              </div>

              {/* Offensive Stats */}
              <div className="stats-section">
                <h4>Offensive Statistics</h4>
                <div className="stats-grid">
                  <div className="stat">
                    <span>Total Yards:</span>
                    <span>{gameResult.detailed_stats.yards_gained.away} - {gameResult.detailed_stats.yards_gained.home}</span>
                  </div>
                  <div className="stat">
                    <span>Avg Yards/Play:</span>
                    <span>{gameResult.detailed_stats.average_yards_per_play.away} - {gameResult.detailed_stats.average_yards_per_play.home}</span>
                  </div>
                  <div className="stat">
                    <span>Running Plays:</span>
                    <span>{gameResult.detailed_stats.plays_by_type.run}</span>
                  </div>
                  <div className="stat">
                    <span>Passing Plays:</span>
                    <span>{gameResult.detailed_stats.plays_by_type.pass}</span>
                  </div>
                </div>
              </div>

              {/* Drive Summary */}
              {gameResult.drive_summary && gameResult.drive_summary.length > 0 && (
                <div className="stats-section">
                  <h4>Drive Summary</h4>
                  <div className="drive-summary">
                    {gameResult.drive_summary.map((drive, index) => (
                      <div key={index} className={`drive ${drive.points > 0 ? 'scoring-drive' : ''}`}>
                        <div className="drive-header">
                          <strong>Q{drive.quarter} - Drive {drive.drive_number}: {drive.offense}</strong>
                          <span className="drive-result">
                            {drive.result.replace('_', ' ').toUpperCase()}
                            {drive.points > 0 && ` (+${drive.points})`}
                          </span>
                        </div>
                        <div className="drive-details">
                          {drive.total_plays} plays, {drive.total_yards} yards from {drive.starting_position}-yard line
                        </div>
                        
                        {/* Show plays for scoring drives */}
                        {drive.points > 0 && drive.plays.length > 0 && (
                          <div className="drive-plays">
                            {drive.plays.slice(-3).map((play, playIndex) => (
                              <div key={playIndex} className="play-detail">
                                {play.description}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {gameResult.key_plays && gameResult.key_plays.length > 0 && (
            <div className="key-plays">
              <h3>Key Plays</h3>
              <ul>
                {gameResult.key_plays.map((play, index) => (
                  <li key={index} className={play.scoring_play ? 'scoring-play' : ''}>
                    Q{play.quarter} {play.time}: {play.description}
                    {play.scoring_play && ' 🏈'}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ExhibitionGame;

import { BaseService } from './base-service';
import { GameEngine, GameResult } from './game-engine';
import { Weather } from './weather';
import { NFLScheduleGenerator } from './schedule-generator';

export class SimulationService extends BaseService {
  private createEngine(options: SimulationOptions = {}): GameEngine {
    const { seed, weather } = options;
    return new GameEngine({ seed, weather });
  }

  async simulateGame(gameId: string, options: SimulationOptions = {}): Promise<any> {
    try {
      this.validateId(gameId, 'game');
      
      const game = this.daoManager.games.getById(gameId);
      if (!game) {
        throw new Error('Game not found');
      }

      const homeTeam = this.daoManager.teams.getById(game.home_team_id);
      const awayTeam = this.daoManager.teams.getById(game.away_team_id);
      
      if (!homeTeam || !awayTeam) {
        throw new Error('Team data not found');
      }

      const engine = this.createEngine(options);
      const result = engine.simulateGame(homeTeam, awayTeam);
      const resultWithId: GameResult = { ...result, gameId };
      
      this.daoManager.games.completeGame(gameId, result.homeScore, result.awayScore, this.buildGameData(resultWithId));

      return this.formatGameResult(resultWithId);
    } catch (error) {
      this.handleError(error, 'Simulate game');
    }
  }

  async simulateExhibitionGame(homeTeamId: string, awayTeamId: string, options: SimulationOptions = {}): Promise<any> {
    try {
      this.validateId(homeTeamId, 'home team');
      this.validateId(awayTeamId, 'away team');
      
      const homeTeam = this.daoManager.teams.getById(homeTeamId);
      const awayTeam = this.daoManager.teams.getById(awayTeamId);
      
      if (!homeTeam || !awayTeam) {
        throw new Error('Team not found');
      }

      const engine = this.createEngine(options);
      const result = engine.simulateGame(homeTeam, awayTeam);
      return this.formatGameResult(result);
    } catch (error) {
      this.handleError(error, 'Simulate exhibition game');
    }
  }

  async simulateWeek(seasonId: string, week: number, options: SimulationOptions = {}): Promise<any> {
    try {
      this.validateId(seasonId, 'season');
      this.validateRequired(week, 'week');
      
      const games = this.daoManager.games.getWeekGames(seasonId, week)
        .filter(game => game.status === 'scheduled');
      
      const results = [];
      
      for (const game of games) {
        const result = await this.simulateGame(game.id, options);
        results.push(result);
      }
      
      return {
        season_id: seasonId,
        week,
        games_simulated: results.length,
        results
      };
    } catch (error) {
      this.handleError(error, 'Simulate week');
    }
  }

  async simulateToWeek(seasonId: string, targetWeek: number, options: SimulationOptions = {}): Promise<any> {
    try {
      this.validateId(seasonId, 'season');
      this.validateRequired(targetWeek, 'target week');
      
      const season = this.daoManager.seasons.getById(seasonId);
      if (!season) {
        throw new Error('Season not found');
      }
      
      const results = [];
      
      for (let week = season.current_week; week <= targetWeek; week++) {
        const weekResult = await this.simulateWeek(seasonId, week, options);
        results.push(weekResult);
        
        // Update season week
        this.daoManager.seasons.setCurrentWeek(seasonId, week + 1);
      }
      
      return {
        season_id: seasonId,
        target_week: targetWeek,
        weeks_simulated: results.length,
        results
      };
    } catch (error) {
      this.handleError(error, 'Simulate to week');
    }
  }

  async simulateSeason(seasonId: string, options: SimulationOptions = {}): Promise<any> {
    try {
      this.validateId(seasonId, 'season');
      
      // Simulate all remaining regular season games (weeks 1-17)
      const generator = new NFLScheduleGenerator();
      return this.simulateToWeek(seasonId, generator.getTotalWeeks(), options);
    } catch (error) {
      this.handleError(error, 'Simulate season');
    }
  }

  async simulatePlayoffGame(gameId: string, options: SimulationOptions = {}): Promise<any> {
    try {
      // For now, same as regular game simulation
      return this.simulateGame(gameId, options);
    } catch (error) {
      this.handleError(error, 'Simulate playoff game');
    }
  }

  private buildGameData(result: GameResult) {
    return {
      winner_id: result.winnerId,
      weather: result.weather,
      stats: result.teamStats,
      play_by_play: result.playByPlay,
      drives: result.drives,
      detailed_stats: {
        summary: result.summary,
        overtime: result.overtime,
        duration: result.duration,
      },
    };
  }

  private formatGameResult(result: GameResult) {
    return {
      game_id: result.gameId || `${result.homeTeam.id}-${result.awayTeam.id}-${result.duration}`,
      home_team: {
        id: result.homeTeam.id,
        name: `${result.homeTeam.city} ${result.homeTeam.name}`,
        abbreviation: result.homeTeam.abbreviation,
        score: result.homeScore,
      },
      away_team: {
        id: result.awayTeam.id,
        name: `${result.awayTeam.city} ${result.awayTeam.name}`,
        abbreviation: result.awayTeam.abbreviation,
        score: result.awayScore,
      },
      winner: result.winnerId ? (result.winnerId === result.homeTeam.id ? 'home' : 'away') : 'tie',
      weather: result.weather,
      summary: result.summary,
      detailed_stats: result.teamStats,
      play_by_play: result.playByPlay,
      drives: result.drives,
      overtime: result.overtime,
      duration: result.duration,
    };
  }
}

export interface SimulationOptions {
  seed?: number;
  weather?: Weather;
}

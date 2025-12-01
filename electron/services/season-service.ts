import { BaseService } from './base-service';
import { Season } from '../database/dao/season-dao';
import { NFLScheduleGenerator } from './schedule-generator';
import { GameStatus, SeasonEngine, SeasonPhase, ScheduledGame, TeamRecord } from './season-engine';

export class SeasonService extends BaseService {

  async createSeason(seasonData: { name: string; year: number }): Promise<string> {
    try {
      this.validateRequired(seasonData.name, 'season name');
      this.validateRequired(seasonData.year, 'season year');

      return this.daoManager.transaction((dao) => {
        // Create season
        const seasonId = dao.seasons.create({
          name: seasonData.name,
          year: seasonData.year,
          status: 'setup',
          current_week: 1
        });

        // Generate schedule for all teams
        const teams = dao.teams.getAll();
        const generator = new NFLScheduleGenerator();
        const weeklySchedule = generator.generateSchedule(teams, seasonData.year);
        
        // Create games
        const gamesToCreate = Object.entries(weeklySchedule).flatMap(([week, games]) =>
          games.map(game => ({
            season_id: seasonId,
            week: parseInt(week, 10),
            home_team_id: game.home.id,
            away_team_id: game.away.id,
            status: 'scheduled' as const
          }))
        );
        dao.games.createGames(gamesToCreate);

        // Update season to active
        dao.seasons.updateStatus(seasonId, 'active');
        
        return seasonId;
      });
    } catch (error) {
      this.handleError(error, 'Create season');
    }
  }

  async getSeasonStatus(seasonId: string): Promise<any> {
    try {
      this.validateId(seasonId, 'season');
      
      const season = this.daoManager.seasons.getById(seasonId);
      if (!season) {
        throw new Error('Season not found');
      }

      const seasonStats = this.daoManager.seasons.getSeasonStats(seasonId);
      const gameStats = this.daoManager.games.getGameStats(seasonId);
      const upcomingGames = this.daoManager.games.getUpcomingGames(seasonId, 8);

      return {
        season: seasonStats.season,
        statistics: {
          ...seasonStats.games,
          ...gameStats
        },
        upcoming_games: upcomingGames
      };
    } catch (error) {
      this.handleError(error, 'Get season status');
    }
  }

  async getStandings(seasonId: string): Promise<any> {
    try {
      this.validateId(seasonId, 'season');
      return this.daoManager.getLeagueStandings(seasonId);
    } catch (error) {
      this.handleError(error, 'Get standings');
    }
  }

  async getNextGames(seasonId: string, limit?: number): Promise<any[]> {
    try {
      this.validateId(seasonId, 'season');
      const games = this.daoManager.games.getNextGames(seasonId, limit || 16);
      
      return games.map(game => this.formatGameSummary(game));
    } catch (error) {
      this.handleError(error, 'Get next games');
    }
  }

  async getWeekGames(seasonId: string, week: number): Promise<any[]> {
    try {
      this.validateId(seasonId, 'season');
      this.validateRequired(week, 'week');
      
      if (week < 1 || week > 21) {
        throw new Error('Week must be between 1 and 21');
      }

      const games = this.daoManager.games.getWeekGames(seasonId, week);
      return games.map(game => this.formatGameSummary(game));
    } catch (error) {
      this.handleError(error, 'Get week games');
    }
  }

  async getTeamSchedule(seasonId: string, teamId: string): Promise<any[]> {
    try {
      this.validateId(seasonId, 'season');
      this.validateId(teamId, 'team');
      
      return this.daoManager.games.getTeamSchedule(seasonId, teamId);
    } catch (error) {
      this.handleError(error, 'Get team schedule');
    }
  }

  async getPlayoffBracket(seasonId: string): Promise<any> {
    try {
      this.validateId(seasonId, 'season');
      const engine = this.buildSeasonEngine(seasonId);
      const bracket = engine.getPlayoffBracket();
      const picture = engine.getPlayoffPicture();
      return {
        season_id: seasonId,
        bracket,
        playoff_picture: picture
      };
    } catch (error) {
      this.handleError(error, 'Get playoff bracket');
    }
  }

  async getAllSeasons(): Promise<Season[]> {
    try {
      return this.daoManager.seasons.getAll();
    } catch (error) {
      this.handleError(error, 'Get all seasons');
    }
  }

  async getActiveSeason(): Promise<Season | null> {
    try {
      const season = this.daoManager.seasons.getActiveSeason();
      return season || null;
    } catch (error) {
      this.handleError(error, 'Get active season');
    }
  }

  async updateSeasonStatus(seasonId: string, status: Season['status']): Promise<boolean> {
    try {
      this.validateId(seasonId, 'season');
      this.validateRequired(status, 'status');
      
      return this.daoManager.seasons.updateStatus(seasonId, status);
    } catch (error) {
      this.handleError(error, 'Update season status');
    }
  }

  async advanceWeek(seasonId: string): Promise<boolean> {
    try {
      this.validateId(seasonId, 'season');
      return this.daoManager.seasons.advanceWeek(seasonId);
    } catch (error) {
      this.handleError(error, 'Advance week');
    }
  }

  private formatGameSummary(game: any) {
    const homeTeam = this.daoManager.teams.getById(game.home_team_id);
    const awayTeam = this.daoManager.teams.getById(game.away_team_id);
    
    return {
      id: game.id,
      week: game.week,
      status: game.status,
      home_team: homeTeam ? {
        id: homeTeam.id,
        name: homeTeam.abbreviation,
        city: homeTeam.city
      } : null,
      away_team: awayTeam ? {
        id: awayTeam.id,
        name: awayTeam.abbreviation,
        city: awayTeam.city
      } : null,
      home_score: game.home_score,
      away_score: game.away_score
    };
  }

  private buildSeasonEngine(seasonId: string): SeasonEngine {
    const season = this.daoManager.seasons.getById(seasonId);
    if (!season) {
      throw new Error('Season not found');
    }

    const teams = this.daoManager.teams.getAll();
    const teamMap = new Map(teams.map(team => [team.id, team]));

    const schedule: ScheduledGame[] = this.daoManager.games.getSeasonGames(seasonId)
      .map(game => {
        const homeTeam = teamMap.get(game.home_team_id);
        const awayTeam = teamMap.get(game.away_team_id);
        if (!homeTeam || !awayTeam) return null;

        const status = this.mapStatus(game.status);
        return {
          game_id: game.id,
          home_team: homeTeam,
          away_team: awayTeam,
          week: game.week,
          status,
          home_score: game.home_score ?? undefined,
          away_score: game.away_score ?? undefined,
          overtime: game.game_data?.overtime ?? false,
          game_duration: game.game_data?.duration
        } as ScheduledGame;
      })
      .filter((g): g is ScheduledGame => g !== null);

    const records: Record<string, TeamRecord> = {};
    for (const team of teams) {
      records[team.id] = new TeamRecord(team);
    }

    const currentPhase = season.status === 'playoffs' ? SeasonPhase.PLAYOFFS : SeasonPhase.REGULAR_SEASON;

    return new SeasonEngine({
      teams,
      seasonYear: season.year,
      currentWeek: season.current_week,
      currentPhase,
      schedule,
      records
    });
  }

  private mapStatus(status: string): GameStatus {
    if (status === 'completed' || status === 'simulated') return GameStatus.COMPLETED;
    if (status === 'in_progress') return GameStatus.IN_PROGRESS;
    if (status === 'postponed') return GameStatus.POSTPONED;
    return GameStatus.SCHEDULED;
  }
}

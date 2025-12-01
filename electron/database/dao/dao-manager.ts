import Database from 'better-sqlite3';
import { TeamDAO } from './team-dao';
import { SeasonDAO } from './season-dao';
import { GameDAO } from './game-dao';

export class DAOManager {
  public teams: TeamDAO;
  public seasons: SeasonDAO;
  public games: GameDAO;

  constructor(private db: Database.Database) {
    this.teams = new TeamDAO(db);
    this.seasons = new SeasonDAO(db);
    this.games = new GameDAO(db);
  }

  // Transaction wrapper for complex operations
  transaction<T>(callback: (daos: DAOManager) => T): T {
    const transactionFn = this.db.transaction(callback);
    return transactionFn(this);
  }

  // Get the underlying database instance
  getDatabase(): Database.Database {
    return this.db;
  }

  // Complex operations that involve multiple DAOs

  // Create season with initial schedule
  createSeasonWithSchedule(seasonData: any, scheduleGames: any[]): string {
    return this.transaction((dao) => {
      // Create season
      const seasonId = dao.seasons.create(seasonData);
      
      // Create all games in the season
      dao.games.createGames(scheduleGames.map(gameData => ({ 
        ...gameData, 
        season_id: seasonId,
        status: 'scheduled' as const
      })));
      
      return seasonId;
    });
  }

  // Delete season and all related data
  deleteSeasonCompletely(seasonId: string): boolean {
    return this.transaction((dao) => {
      // Delete all games first (due to foreign key constraints)
      dao.games.deleteSeasonGames(seasonId);
      
      // Delete the season
      return dao.seasons.delete(seasonId);
    });
  }

  // Get comprehensive season data
  getSeasonOverview(seasonId: string): any {
    const season = this.seasons.getById(seasonId);
    if (!season) return null;

    const seasonStats = this.seasons.getSeasonStats(seasonId);
    const gameStats = this.games.getGameStats(seasonId);
    const upcomingGames = this.games.getUpcomingGames(seasonId, 5);

    return {
      season: seasonStats.season,
      statistics: {
        ...seasonStats.games,
        ...gameStats
      },
      upcoming_games: upcomingGames
    };
  }

  // Get team performance across all seasons
  getTeamPerformanceHistory(teamId: string): any {
    const team = this.teams.getById(teamId);
    if (!team) return null;

    const allSeasons = this.seasons.getAll();
    const performance = [];

    for (const season of allSeasons) {
      const record = this.games.getTeamRecord(season.id, teamId);
      const games = this.games.getTeamGames(season.id, teamId);
      
      performance.push({
        season: {
          id: season.id,
          name: season.name,
          year: season.year
        },
        record,
        games_played: games.filter(g => g.status === 'completed').length,
        total_games: games.length
      });
    }

    return {
      team: this.teams.getTeamSummary(teamId),
      seasons: performance
    };
  }

  // Get league standings for a season
  getLeagueStandings(seasonId: string): any {
    const season = this.seasons.getById(seasonId);
    if (!season) return null;

    const allTeams = this.teams.getAll();
    const standings: any = {
      AFC: { North: [], South: [], East: [], West: [] },
      NFC: { North: [], South: [], East: [], West: [] }
    };

    for (const team of allTeams) {
      const record = this.games.getTeamRecord(seasonId, team.id);
      const games = this.games.getTeamGames(seasonId, team.id);
      
      // Calculate points for and against
      let pointsFor = 0;
      let pointsAgainst = 0;
      
      for (const game of games.filter(g => g.status === 'completed')) {
        if (game.home_team_id === team.id) {
          pointsFor += game.home_score || 0;
          pointsAgainst += game.away_score || 0;
        } else {
          pointsFor += game.away_score || 0;
          pointsAgainst += game.home_score || 0;
        }
      }

      const teamStanding = {
        team: {
          id: team.id,
          name: `${team.city} ${team.name}`,
          abbreviation: team.abbreviation
        },
        record,
        points_for: pointsFor,
        points_against: pointsAgainst,
        point_differential: pointsFor - pointsAgainst,
        games_played: games.filter(g => g.status === 'completed').length,
        win_percentage: record.wins + record.losses + record.ties > 0 
          ? record.wins / (record.wins + record.losses + record.ties)
          : 0
      };

      standings[team.conference][team.division].push(teamStanding);
    }

    // Sort divisions by win percentage
    for (const conference of Object.values(standings)) {
      for (const division of Object.values(conference as any)) {
        (division as any[]).sort((a, b) => {
          // Sort by win percentage, then by point differential
          if (b.win_percentage !== a.win_percentage) {
            return b.win_percentage - a.win_percentage;
          }
          return b.point_differential - a.point_differential;
        });
      }
    }

    return {
      season: {
        id: season.id,
        name: season.name,
        year: season.year,
        current_week: season.current_week
      },
      standings
    };
  }

  // Get game summary with team information
  getGameSummary(gameId: string): any {
    const game = this.games.getById(gameId);
    if (!game) return null;

    const homeTeam = this.teams.getTeamSummary(game.home_team_id);
    const awayTeam = this.teams.getTeamSummary(game.away_team_id);

    return {
      game: {
        id: game.id,
        week: game.week,
        status: game.status,
        home_score: game.home_score,
        away_score: game.away_score,
        simulated_at: game.simulated_at
      },
      home_team: homeTeam,
      away_team: awayTeam,
      game_data: game.game_data
    };
  }

  // Search across all entities
  globalSearch(query: string): any {
    const teams = this.teams.searchTeams(query);
    const seasons = this.seasons.searchSeasons(query);
    
    return {
      teams: teams.map(team => this.teams.getTeamSummary(team.id)),
      seasons: seasons.map(season => this.seasons.getSeasonSummary(season.id))
    };
  }

  // Get database statistics
  getDatabaseStats(): any {
    const teamCount = this.teams.count();
    const seasonCount = this.seasons.count();
    const gameCount = this.games.count();
    const completedGameCount = this.games.count('status = ?', ['completed']);

    return {
      teams: teamCount,
      seasons: seasonCount,
      games: {
        total: gameCount,
        completed: completedGameCount,
        remaining: gameCount - completedGameCount
      }
    };
  }

  // Backup/Export utilities
  exportSeasonData(seasonId: string): any {
    const season = this.seasons.getById(seasonId);
    if (!season) return null;

    const games = this.games.getSeasonGames(seasonId);
    
    return {
      season,
      games,
      exported_at: new Date().toISOString()
    };
  }

  // Health check - verify database integrity
  performHealthCheck(): any {
    const issues = [];
    
    try {
      // Check if all teams exist
      const teamCount = this.teams.count();
      if (teamCount !== 32) {
        issues.push(`Expected 32 NFL teams, found ${teamCount}`);
      }

      // Check for orphaned games
      const orphanedGames = this.games.executeQuery(`
        SELECT COUNT(*) as count 
        FROM season_games sg 
        LEFT JOIN seasons s ON sg.season_id = s.id 
        WHERE s.id IS NULL
      `)[0];

      if (orphanedGames.count > 0) {
        issues.push(`Found ${orphanedGames.count} orphaned games`);
      }

      // Check for games with invalid teams
      const invalidTeamGames = this.games.executeQuery(`
        SELECT COUNT(*) as count 
        FROM season_games sg 
        LEFT JOIN teams ht ON sg.home_team_id = ht.id 
        LEFT JOIN teams at ON sg.away_team_id = at.id 
        WHERE ht.id IS NULL OR at.id IS NULL
      `)[0];

      if (invalidTeamGames.count > 0) {
        issues.push(`Found ${invalidTeamGames.count} games with invalid teams`);
      }

      return {
        status: issues.length === 0 ? 'healthy' : 'issues_found',
        issues,
        checked_at: new Date().toISOString()
      };

    } catch (error) {
      return {
        status: 'error',
        error: error instanceof Error ? error.message : 'Unknown error',
        checked_at: new Date().toISOString()
      };
    }
  }
}
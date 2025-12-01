import Database from 'better-sqlite3';
import { BaseDAO } from './base-dao';

export interface GameData {
  winner_id?: string;
  weather?: any;
  stats?: any;
  play_by_play?: any[];
  drives?: any[];
  detailed_stats?: any;
}

export interface Game {
  id: string;
  season_id: string;
  week: number;
  home_team_id: string;
  away_team_id: string;
  home_score?: number;
  away_score?: number;
  status: 'scheduled' | 'completed' | 'simulated';
  game_data?: GameData;
  simulated_at?: string;
}

export class GameDAO extends BaseDAO<Game> {
  constructor(database: Database.Database) {
    super(database, 'season_games');
  }

  // Create a new game
  create(gameData: Omit<Game, 'id'>): string {
    const id = this.generateId('game');
    
    const insertData = {
      id,
      season_id: gameData.season_id,
      week: gameData.week,
      home_team_id: gameData.home_team_id,
      away_team_id: gameData.away_team_id,
      home_score: gameData.home_score || null,
      away_score: gameData.away_score || null,
      status: gameData.status || 'scheduled',
      game_data: gameData.game_data ? this.stringifyJsonField(gameData.game_data) : null,
      simulated_at: gameData.simulated_at || null
    };

    this.insert(insertData);
    return id;
  }

  // Get game by ID
  getById(gameId: string): Game | undefined {
    return this.findById(gameId);
  }

  // Get all games for a season
  getSeasonGames(seasonId: string, week?: number): Game[] {
    if (week !== undefined) {
      return this.findWhere('season_id = ? AND week = ?', [seasonId, week], undefined);
    }
    return this.findWhere('season_id = ?', [seasonId], undefined);
  }

  // Get games by week
  getWeekGames(seasonId: string, week: number): Game[] {
    return this.findWhere('season_id = ? AND week = ?', [seasonId, week]);
  }

  // Get next games (scheduled games)
  getNextGames(seasonId: string, limit: number = 16): Game[] {
    return this.findWhere(
      'season_id = ? AND status = ?', 
      [seasonId, 'scheduled'], 
      limit
    );
  }

  // Get completed games
  getCompletedGames(seasonId: string): Game[] {
    return this.findWhere('season_id = ? AND status IN (?, ?)', [seasonId, 'completed', 'simulated']);
  }

  // Get team games (home or away)
  getTeamGames(seasonId: string, teamId: string): Game[] {
    return this.findWhere(
      'season_id = ? AND (home_team_id = ? OR away_team_id = ?)',
      [seasonId, teamId, teamId]
    );
  }

  // Get team's next game
  getTeamNextGame(seasonId: string, teamId: string): Game | undefined {
    const games = this.findWhere(
      'season_id = ? AND (home_team_id = ? OR away_team_id = ?) AND status = ?',
      [seasonId, teamId, teamId, 'scheduled'],
      1
    );
    return games.length > 0 ? games[0] : undefined;
  }

  // Complete a game with results
  completeGame(gameId: string, homeScore: number, awayScore: number, gameData?: GameData): boolean {
    const updateData: any = {
      home_score: homeScore,
      away_score: awayScore,
      status: 'completed',
      simulated_at: new Date().toISOString()
    };

    if (gameData) {
      // Ensure winner_id is set
      const game = this.getById(gameId);
      if (game) {
        gameData.winner_id = homeScore > awayScore 
          ? game.home_team_id 
          : awayScore > homeScore 
            ? game.away_team_id 
            : undefined; // tie
      }
      
      updateData.game_data = this.stringifyJsonField(gameData);
    }

    return this.update(gameId, updateData);
  }

  // Update game status
  updateStatus(gameId: string, status: Game['status']): boolean {
    const updateData: any = { status };
    
    if (status === 'completed' || status === 'simulated') {
      updateData.simulated_at = new Date().toISOString();
    }

    return this.update(gameId, updateData);
  }

  // Get games by status
  getGamesByStatus(seasonId: string, status: Game['status']): Game[] {
    return this.findWhere('season_id = ? AND status = ?', [seasonId, status]);
  }

  // Get season schedule summary
  getSeasonSchedule(seasonId: string): any {
    const weeks: { [key: number]: Game[] } = {};
    const games = this.getSeasonGames(seasonId);

    for (const game of games) {
      if (!weeks[game.week]) {
        weeks[game.week] = [];
      }
      weeks[game.week].push(game);
    }

    return {
      season_id: seasonId,
      total_games: games.length,
      weeks: Object.keys(weeks).map(weekNum => ({
        week: parseInt(weekNum),
        games: weeks[parseInt(weekNum)].length,
        completed: weeks[parseInt(weekNum)].filter(g => g.status === 'completed').length,
        game_list: weeks[parseInt(weekNum)]
      })).sort((a, b) => a.week - b.week)
    };
  }

  // Get team schedule
  getTeamSchedule(seasonId: string, teamId: string): any[] {
    const games = this.getTeamGames(seasonId, teamId);
    
    return games.map(game => ({
      game_id: game.id,
      week: game.week,
      opponent_id: game.home_team_id === teamId ? game.away_team_id : game.home_team_id,
      is_home: game.home_team_id === teamId,
      status: game.status,
      home_score: game.home_score,
      away_score: game.away_score,
      result: this.getGameResult(game, teamId)
    })).sort((a, b) => a.week - b.week);
  }

  // Get team record
  getTeamRecord(seasonId: string, teamId: string): { wins: number; losses: number; ties: number } {
    const games = this.getTeamGames(seasonId, teamId)
      .filter(game => game.status === 'completed');

    let wins = 0;
    let losses = 0;
    let ties = 0;

    for (const game of games) {
      const result = this.getGameResult(game, teamId);
      if (result === 'win') wins++;
      else if (result === 'loss') losses++;
      else if (result === 'tie') ties++;
    }

    return { wins, losses, ties };
  }

  // Get game result for a specific team
  private getGameResult(game: Game, teamId: string): 'win' | 'loss' | 'tie' | 'pending' {
    if (game.status !== 'completed' || game.home_score === undefined || game.away_score === undefined) {
      return 'pending';
    }

    const isHome = game.home_team_id === teamId;
    const teamScore = isHome ? game.home_score : game.away_score;
    const opponentScore = isHome ? game.away_score : game.home_score;

    if (teamScore > opponentScore) return 'win';
    if (teamScore < opponentScore) return 'loss';
    return 'tie';
  }

  // Create multiple games (for schedule generation)
  createGames(games: Array<Omit<Game, 'id'>>): number {
    if (games.length === 0) return 0;

    return this.transaction(() => {
      let created = 0;
      for (const game of games) {
        this.create(game);
        created++;
      }
      return created;
    });
  }

  // Delete all games for a season
  deleteSeasonGames(seasonId: string): number {
    return this.deleteWhere('season_id = ?', [seasonId]);
  }

  // Get game statistics
  getGameStats(seasonId: string): any {
    const stats = this.executeQuery(`
      SELECT 
        COUNT(*) as total_games,
        COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_games,
        COUNT(CASE WHEN status = 'scheduled' THEN 1 END) as scheduled_games,
        AVG(CASE WHEN status = 'completed' THEN home_score + away_score END) as avg_total_score,
        MAX(CASE WHEN status = 'completed' THEN home_score + away_score END) as highest_scoring,
        MIN(CASE WHEN status = 'completed' THEN home_score + away_score END) as lowest_scoring
      FROM season_games 
      WHERE season_id = ?
    `, [seasonId])[0];

    return {
      total_games: stats.total_games || 0,
      completed_games: stats.completed_games || 0,
      scheduled_games: stats.scheduled_games || 0,
      avg_total_score: stats.avg_total_score ? Math.round(stats.avg_total_score * 10) / 10 : 0,
      highest_scoring: stats.highest_scoring || 0,
      lowest_scoring: stats.lowest_scoring || 0
    };
  }

  // Get upcoming games for UI display
  getUpcomingGames(seasonId: string, limit: number = 8): any[] {
    const games = this.getNextGames(seasonId, limit);
    
    return games.map(game => ({
      id: game.id,
      week: game.week,
      home_team_id: game.home_team_id,
      away_team_id: game.away_team_id,
      status: game.status
    }));
  }

  // Search games
  searchGames(seasonId: string, query: string): Game[] {
    // For now, search by week number
    const weekNum = parseInt(query);
    if (!isNaN(weekNum)) {
      return this.getWeekGames(seasonId, weekNum);
    }
    return [];
  }

  // Map database row to Game entity
  protected mapRowToEntity(row: any): Game {
    return {
      id: row.id,
      season_id: row.season_id,
      week: row.week,
      home_team_id: row.home_team_id,
      away_team_id: row.away_team_id,
      home_score: row.home_score,
      away_score: row.away_score,
      status: row.status,
      game_data: row.game_data ? this.parseJsonField(row.game_data) : undefined,
      simulated_at: row.simulated_at
    };
  }
}
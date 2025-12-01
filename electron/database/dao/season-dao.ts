import Database from 'better-sqlite3';
import { BaseDAO } from './base-dao';

export interface Season {
  id: string;
  name: string;
  year: number;
  status: 'setup' | 'active' | 'completed' | 'playoffs';
  current_week: number;
  created_at: string;
  updated_at: string;
}

export class SeasonDAO extends BaseDAO<Season> {
  constructor(database: Database.Database) {
    super(database, 'seasons');
  }

  // Create a new season
  create(seasonData: Omit<Season, 'id' | 'created_at' | 'updated_at'>): string {
    const id = this.generateId('season');
    const now = new Date().toISOString();
    
    const insertData = {
      id,
      name: seasonData.name,
      year: seasonData.year,
      status: seasonData.status || 'setup',
      current_week: seasonData.current_week || 1,
      created_at: now,
      updated_at: now
    };

    this.insert(insertData);
    return id;
  }

  // Get season by ID
  getById(seasonId: string): Season | undefined {
    return this.findById(seasonId);
  }

  // Get all seasons
  getAll(): Season[] {
    return this.findAll(undefined, 'created_at DESC');
  }

  // Get seasons by status
  getByStatus(status: Season['status']): Season[] {
    return this.findWhere('status = ?', [status]);
  }

  // Get active season
  getActiveSeason(): Season | undefined {
    return this.findOneWhere('status = ?', ['active']);
  }

  // Get most recent season
  getMostRecentSeason(): Season | undefined {
    const seasons = this.findAll(1, 'created_at DESC');
    return seasons.length > 0 ? seasons[0] : undefined;
  }

  // Get seasons by year
  getByYear(year: number): Season[] {
    return this.findWhere('year = ?', [year]);
  }

  // Update season status
  updateStatus(seasonId: string, status: Season['status']): boolean {
    return this.update(seasonId, {
      status,
      updated_at: new Date().toISOString()
    });
  }

  // Advance to next week
  advanceWeek(seasonId: string): boolean {
    const season = this.getById(seasonId);
    if (!season) return false;

    return this.update(seasonId, {
      current_week: season.current_week + 1,
      updated_at: new Date().toISOString()
    });
  }

  // Set current week
  setCurrentWeek(seasonId: string, week: number): boolean {
    if (week < 1 || week > 21) { // Regular season (1-17) + playoffs (18-21)
      throw new Error('Week must be between 1 and 21');
    }

    return this.update(seasonId, {
      current_week: week,
      updated_at: new Date().toISOString()
    });
  }

  // Update season name
  updateName(seasonId: string, name: string): boolean {
    return this.update(seasonId, {
      name,
      updated_at: new Date().toISOString()
    });
  }

  // Complete season
  completeSeason(seasonId: string): boolean {
    return this.updateStatus(seasonId, 'completed');
  }

  // Activate season (and deactivate others)
  activateSeason(seasonId: string): boolean {
    return this.transaction(() => {
      // Deactivate all other seasons
      this.updateWhere('status = ?', { status: 'setup' }, ['active']);
      
      // Activate the specified season
      return this.updateStatus(seasonId, 'active');
    });
  }

  // Get season statistics
  getSeasonStats(seasonId: string): any {
    const season = this.getById(seasonId);
    if (!season) return null;

    // Get related game statistics
    const gameStats = this.executeQuery(`
      SELECT 
        COUNT(*) as total_games,
        COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_games,
        COUNT(CASE WHEN status = 'scheduled' THEN 1 END) as remaining_games,
        MAX(week) as max_week
      FROM season_games 
      WHERE season_id = ?
    `, [seasonId])[0];

    const completionPercentage = gameStats.total_games > 0 
      ? (gameStats.completed_games / gameStats.total_games) * 100 
      : 0;

    return {
      season: {
        id: season.id,
        name: season.name,
        year: season.year,
        status: season.status,
        current_week: season.current_week,
        created_at: season.created_at,
        updated_at: season.updated_at
      },
      games: {
        total: gameStats.total_games || 0,
        completed: gameStats.completed_games || 0,
        remaining: gameStats.remaining_games || 0,
        max_week: gameStats.max_week || 0,
        completion_percentage: Math.round(completionPercentage)
      }
    };
  }

  // Delete season and all related data
  deleteSeason(seasonId: string): boolean {
    return this.transaction(() => {
      // Delete related games first (due to foreign key constraints)
      this.executeUpdate('DELETE FROM season_games WHERE season_id = ?', [seasonId]);
      
      // Delete the season
      return this.delete(seasonId);
    });
  }

  // Search seasons
  searchSeasons(query: string): Season[] {
    const searchTerm = `%${query.toLowerCase()}%`;
    return this.findWhere(
      'LOWER(name) LIKE ? OR year = ?',
      [searchTerm, isNaN(parseInt(query)) ? -1 : parseInt(query)]
    );
  }

  // Get season summary for UI
  getSeasonSummary(seasonId: string): any {
    const stats = this.getSeasonStats(seasonId);
    if (!stats) return null;

    return {
      ...stats.season,
      games_completed: stats.games.completed,
      games_total: stats.games.total,
      completion_percentage: stats.games.completion_percentage,
      is_active: stats.season.status === 'active',
      is_completed: stats.season.status === 'completed'
    };
  }

  // Get season progress
  getSeasonProgress(seasonId: string): any {
    const season = this.getById(seasonId);
    if (!season) return null;

    // Calculate progress based on weeks
    const regularSeasonWeeks = 17;
    const playoffWeeks = 4;
    const totalWeeks = regularSeasonWeeks + playoffWeeks;

    let phase = 'setup';
    let progress = 0;

    if (season.status === 'active') {
      if (season.current_week <= regularSeasonWeeks) {
        phase = 'regular_season';
        progress = (season.current_week / regularSeasonWeeks) * 100;
      } else {
        phase = 'playoffs';
        const playoffProgress = (season.current_week - regularSeasonWeeks) / playoffWeeks;
        progress = 100; // Regular season complete, show playoff progress separately
      }
    } else if (season.status === 'completed') {
      phase = 'completed';
      progress = 100;
    }

    return {
      season_id: seasonId,
      phase,
      current_week: season.current_week,
      progress_percentage: Math.round(progress),
      weeks: {
        regular_season_weeks: regularSeasonWeeks,
        playoff_weeks: playoffWeeks,
        total_weeks: totalWeeks,
        is_playoffs: season.current_week > regularSeasonWeeks
      }
    };
  }

  // Clone season (create new season with same settings)
  cloneSeason(seasonId: string, newName: string, newYear: number): string {
    const originalSeason = this.getById(seasonId);
    if (!originalSeason) {
      throw new Error('Original season not found');
    }

    return this.create({
      name: newName,
      year: newYear,
      status: 'setup',
      current_week: 1
    });
  }

  // Get recent seasons for quick access
  getRecentSeasons(limit: number = 5): Season[] {
    return this.findAll(limit, 'updated_at DESC');
  }

  // Map database row to Season entity
  protected mapRowToEntity(row: any): Season {
    return {
      id: row.id,
      name: row.name,
      year: row.year,
      status: row.status,
      current_week: row.current_week,
      created_at: row.created_at,
      updated_at: row.updated_at
    };
  }
}
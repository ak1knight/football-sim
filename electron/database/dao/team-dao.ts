import Database from 'better-sqlite3';
import { BaseDAO } from './base-dao';

export interface TeamStats {
  offensive_rating: number;
  defensive_rating: number;
  special_teams_rating: number;
  coaching_rating: number;
  home_field_advantage: number;
}

export interface Team {
  id: string;
  name: string;
  city: string;
  abbreviation: string;
  conference: 'AFC' | 'NFC';
  division: 'North' | 'South' | 'East' | 'West';
  stats: TeamStats;
  created_at: string;
}

export class TeamDAO extends BaseDAO<Team> {
  constructor(database: Database.Database) {
    super(database, 'teams');
  }

  // Get all teams
  getAll(): Team[] {
    return this.findAll(undefined, 'conference, division, name');
  }

  // Get team by ID
  getById(teamId: string): Team | undefined {
    return this.findById(teamId);
  }

  // Get team by abbreviation
  getByAbbreviation(abbreviation: string): Team | undefined {
    return this.findOneWhere('abbreviation = ?', [abbreviation]);
  }

  // Get teams by conference
  getByConference(conference: 'AFC' | 'NFC'): Team[] {
    return this.findWhere('conference = ?', [conference]);
  }

  // Get teams by division
  getByDivision(conference: 'AFC' | 'NFC', division: string): Team[] {
    return this.findWhere('conference = ? AND division = ?', [conference, division]);
  }

  // Get all divisions for a conference
  getDivisions(conference: 'AFC' | 'NFC'): { division: string; teams: Team[] }[] {
    const teams = this.getByConference(conference);
    const divisions: { [key: string]: Team[] } = {};

    for (const team of teams) {
      if (!divisions[team.division]) {
        divisions[team.division] = [];
      }
      divisions[team.division].push(team);
    }

    return Object.entries(divisions).map(([division, teams]) => ({
      division,
      teams: teams.sort((a, b) => a.name.localeCompare(b.name))
    }));
  }

  // Update team statistics
  updateStats(teamId: string, stats: Partial<TeamStats>): boolean {
    const team = this.getById(teamId);
    if (!team) return false;

    const updatedStats = { ...team.stats, ...stats };
    return this.update(teamId, {
      stats: this.stringifyJsonField(updatedStats) as any,
      updated_at: new Date().toISOString()
    });
  }

  // Create a new team
  createTeam(teamData: Omit<Team, 'id' | 'created_at'>): string {
    const id = this.generateId('team');
    const now = new Date().toISOString();
    
    const insertData: any = {
      id,
      name: teamData.name,
      city: teamData.city,
      abbreviation: teamData.abbreviation,
      conference: teamData.conference,
      division: teamData.division,
      stats: this.stringifyJsonField(teamData.stats),
      created_at: now
    };

    this.insert(insertData);
    return id;
  }

  // Get team rankings by overall rating
  getTeamRankings(): Array<Team & { overall_rating: number; rank: number }> {
    const teams = this.getAll();
    
    const teamsWithRating = teams.map(team => ({
      ...team,
      overall_rating: this.calculateOverallRating(team.stats)
    }));

    // Sort by overall rating descending
    teamsWithRating.sort((a, b) => b.overall_rating - a.overall_rating);
    
    // Add rank
    return teamsWithRating.map((team, index) => ({
      ...team,
      rank: index + 1
    }));
  }

  // Calculate overall team rating
  private calculateOverallRating(stats: TeamStats): number {
    return Math.round(
      (stats.offensive_rating + 
       stats.defensive_rating + 
       stats.special_teams_rating + 
       stats.coaching_rating) / 4
    );
  }

  // Get strongest and weakest teams
  getTeamExtremes(): { strongest: Team[]; weakest: Team[] } {
    const rankings = this.getTeamRankings();
    
    return {
      strongest: rankings.slice(0, 5),
      weakest: rankings.slice(-5)
    };
  }

  // Search teams by name or city
  searchTeams(query: string): Team[] {
    const searchTerm = `%${query.toLowerCase()}%`;
    return this.findWhere(
      'LOWER(name) LIKE ? OR LOWER(city) LIKE ? OR LOWER(abbreviation) LIKE ?',
      [searchTerm, searchTerm, searchTerm]
    );
  }

  // Get team statistics comparison
  compareTeams(team1Id: string, team2Id: string): any {
    const team1 = this.getById(team1Id);
    const team2 = this.getById(team2Id);

    if (!team1 || !team2) {
      throw new Error('One or both teams not found');
    }

    return {
      team1: {
        id: team1.id,
        name: `${team1.city} ${team1.name}`,
        abbreviation: team1.abbreviation,
        stats: team1.stats,
        overall_rating: this.calculateOverallRating(team1.stats)
      },
      team2: {
        id: team2.id,
        name: `${team2.city} ${team2.name}`,
        abbreviation: team2.abbreviation,
        stats: team2.stats,
        overall_rating: this.calculateOverallRating(team2.stats)
      },
      comparison: {
        offensive_advantage: team1.stats.offensive_rating - team2.stats.offensive_rating,
        defensive_advantage: team1.stats.defensive_rating - team2.stats.defensive_rating,
        special_teams_advantage: team1.stats.special_teams_rating - team2.stats.special_teams_rating,
        coaching_advantage: team1.stats.coaching_rating - team2.stats.coaching_rating,
        overall_advantage: this.calculateOverallRating(team1.stats) - this.calculateOverallRating(team2.stats),
        home_field_advantage: team1.stats.home_field_advantage - team2.stats.home_field_advantage
      }
    };
  }

  // Get conference standings format
  getConferenceStandings(): { AFC: any; NFC: any } {
    const afcTeams = this.getByConference('AFC');
    const nfcTeams = this.getByConference('NFC');

    return {
      AFC: this.formatConferenceData(afcTeams),
      NFC: this.formatConferenceData(nfcTeams)
    };
  }

  private formatConferenceData(teams: Team[]): any {
    const divisions = ['North', 'South', 'East', 'West'];
    const result: any = {};

    for (const division of divisions) {
      result[division] = teams
        .filter(team => team.division === division)
        .map(team => ({
          id: team.id,
          name: team.name,
          city: team.city,
          abbreviation: team.abbreviation,
          overall_rating: this.calculateOverallRating(team.stats)
        }))
        .sort((a, b) => b.overall_rating - a.overall_rating);
    }

    return result;
  }

  // Map database row to Team entity
  protected mapRowToEntity(row: any): Team {
    return {
      id: row.id,
      name: row.name,
      city: row.city,
      abbreviation: row.abbreviation,
      conference: row.conference,
      division: row.division,
      stats: this.parseJsonField(row.stats),
      created_at: row.created_at
    };
  }

  // Get team summary for UI display
  getTeamSummary(teamId: string): any {
    const team = this.getById(teamId);
    if (!team) return null;

    return {
      id: team.id,
      name: `${team.city} ${team.name}`,
      abbreviation: team.abbreviation,
      conference: team.conference,
      division: team.division,
      overall_rating: this.calculateOverallRating(team.stats),
      stats: team.stats
    };
  }

  // Bulk update team ratings (useful for season adjustments)
  updateMultipleTeamRatings(updates: Array<{ teamId: string; stats: Partial<TeamStats> }>): number {
    let updatedCount = 0;
    
    this.transaction(() => {
      for (const update of updates) {
        if (this.updateStats(update.teamId, update.stats)) {
          updatedCount++;
        }
      }
    });

    return updatedCount;
  }
}
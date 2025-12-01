import { BaseService } from './base-service';
import { Team, TeamStats } from '../database/dao/team-dao';

export class TeamService extends BaseService {
  
  async getAllTeams(): Promise<Team[]> {
    try {
      return this.daoManager.teams.getAll();
    } catch (error) {
      this.handleError(error, 'Get all teams');
    }
  }

  async getTeamById(teamId: string): Promise<Team | null> {
    try {
      this.validateId(teamId, 'team');
      const team = this.daoManager.teams.getById(teamId);
      return team || null;
    } catch (error) {
      this.handleError(error, 'Get team by ID');
    }
  }

  async getTeamsByConference(conference: 'AFC' | 'NFC'): Promise<Team[]> {
    try {
      this.validateRequired(conference, 'conference');
      return this.daoManager.teams.getByConference(conference);
    } catch (error) {
      this.handleError(error, 'Get teams by conference');
    }
  }

  async getTeamsByDivision(conference: 'AFC' | 'NFC', division: string): Promise<Team[]> {
    try {
      this.validateRequired(conference, 'conference');
      this.validateRequired(division, 'division');
      return this.daoManager.teams.getByDivision(conference, division);
    } catch (error) {
      this.handleError(error, 'Get teams by division');
    }
  }

  async compareTeams(team1Id: string, team2Id: string): Promise<any> {
    try {
      this.validateId(team1Id, 'team1');
      this.validateId(team2Id, 'team2');
      
      const team1 = this.daoManager.teams.getById(team1Id);
      const team2 = this.daoManager.teams.getById(team2Id);
      
      if (!team1 || !team2) {
        throw new Error('One or both teams not found');
      }

      return this.formatTeamComparison(team1, team2);
    } catch (error) {
      this.handleError(error, 'Compare teams');
    }
  }

  async getTeamRankings(): Promise<any[]> {
    try {
      return this.daoManager.teams.getTeamRankings();
    } catch (error) {
      this.handleError(error, 'Get team rankings');
    }
  }

  async searchTeams(query: string): Promise<Team[]> {
    try {
      this.validateRequired(query, 'search query');
      return this.daoManager.teams.searchTeams(query);
    } catch (error) {
      this.handleError(error, 'Search teams');
    }
  }

  async getConferenceStandings(): Promise<any> {
    try {
      return this.daoManager.teams.getConferenceStandings();
    } catch (error) {
      this.handleError(error, 'Get conference standings');
    }
  }

  async updateTeamStats(teamId: string, stats: Partial<TeamStats>): Promise<boolean> {
    try {
      this.validateId(teamId, 'team');
      this.validateRequired(stats, 'stats');
      return this.daoManager.teams.updateStats(teamId, stats);
    } catch (error) {
      this.handleError(error, 'Update team stats');
    }
  }

  private formatTeamComparison(team1: Team, team2: Team) {
    const team1Rating = this.calculateOverallRating(team1.stats);
    const team2Rating = this.calculateOverallRating(team2.stats);

    return {
      team1: {
        id: team1.id,
        name: `${team1.city} ${team1.name}`,
        abbreviation: team1.abbreviation,
        stats: team1.stats,
        overall_rating: team1Rating
      },
      team2: {
        id: team2.id,
        name: `${team2.city} ${team2.name}`,
        abbreviation: team2.abbreviation,
        stats: team2.stats,
        overall_rating: team2Rating
      },
      comparison: {
        offensive_advantage: team1.stats.offensive_rating - team2.stats.offensive_rating,
        defensive_advantage: team1.stats.defensive_rating - team2.stats.defensive_rating,
        special_teams_advantage: team1.stats.special_teams_rating - team2.stats.special_teams_rating,
        coaching_advantage: team1.stats.coaching_rating - team2.stats.coaching_rating,
        overall_advantage: team1Rating - team2Rating,
        home_field_advantage: team1.stats.home_field_advantage - team2.stats.home_field_advantage
      }
    };
  }

  private calculateOverallRating(stats: TeamStats): number {
    return Math.round(
      (stats.offensive_rating + 
       stats.defensive_rating + 
       stats.special_teams_rating + 
       stats.coaching_rating) / 4
    );
  }
}
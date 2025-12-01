import { makeAutoObservable, runInAction } from 'mobx';
import { apiFetch } from '../api';

// Hardcoded default user ID for backend API compatibility
const DEFAULT_USER_ID = 'test-user-uuid';

export interface Team {
  name: string;
  city: string;
  abbreviation: string;
  conference: string;
  division: string;
}

export interface OrganizedTeams {
  [conference: string]: {
    [division: string]: Team[];
  };
}

export interface GameResult {
  game_id: string;
  home_team: {
    name: string;
    city: string;
    abbreviation: string;
  };
  away_team: {
    name: string;
    city: string;
    abbreviation: string;
  };
  week: number;
  status: string;
  scheduled_date?: string;
  home_score?: number;
  away_score?: number;
  overtime: boolean;
  winner?: string;
}

export interface TeamRecord {
  team: {
    name: string;
    city: string;
    abbreviation: string;
    conference: string;
    division: string;
  };
  wins: number;
  losses: number;
  ties: number;
  win_percentage: number;
  points_for: number;
  points_against: number;
  point_differential: number;
  division_record: string;
  conference_record: string;
  games_played: number;
}

export interface SeasonStatus {
  id: string;
  season_year: number;
  current_week: number;
  current_phase: string;
  total_games: number;
  completed_games: number;
  completion_percentage: number;
  next_games_count: number;
  weeks_remaining: number;
  schedule_type: string;
}

export interface Standings {
  [divisionOrConference: string]: TeamRecord[];
}

export interface SimulationResult {
  success: boolean;
  message: string;
  simulated_games: any[];
  season_status: SeasonStatus;
}

export interface PlayoffTeam {
  team: {
    name: string;
    city: string;
    abbreviation: string;
    conference: string;
    division: string;
  };
  seed: number;
  division_winner: boolean;
  wild_card: boolean;
  record: string;
  win_percentage: number;
  points_for: number;
  points_against: number;
  point_differential: number;
}

export interface PlayoffGame {
  game_id: string;
  round: string;
  conference: string;
  game_number: number;
  higher_seed?: PlayoffTeam;
  lower_seed?: PlayoffTeam;
  home_team?: {
    name: string;
    city: string;
    abbreviation: string;
  };
  away_team?: {
    name: string;
    city: string;
    abbreviation: string;
  };
  scheduled_date?: string;
  home_score?: number;
  away_score?: number;
  winner?: string;
  overtime: boolean;
  completed: boolean;
  matchup_description: string;
  is_ready_to_play: boolean;
}

export interface PlayoffBracket {
  season_year: number;
  current_round: string;
  afc_teams: PlayoffTeam[];
  nfc_teams: PlayoffTeam[];
  wild_card_games: PlayoffGame[];
  divisional_games: PlayoffGame[];
  conference_championship_games: PlayoffGame[];
  super_bowl?: PlayoffGame;
  afc_champion?: PlayoffTeam;
  nfc_champion?: PlayoffTeam;
  super_bowl_champion?: PlayoffTeam;
  next_games: PlayoffGame[];
  is_complete: boolean;
}

export class SeasonStore {
  // Season state
  currentSeason: SeasonStatus | null = null;
  allSeasons: SeasonStatus[] = [];
  selectedSeasonId: string | null = null;
  teams: Team[] = [];
  organizedTeams: OrganizedTeams = {};
  
  // Games and schedule
  nextGames: GameResult[] = [];
  currentWeekGames: GameResult[] = [];
  selectedWeek: number = 1;
  
  // Standings
  standings: Standings = {};
  standingsByDivision: boolean = true;
  
  // Simulation state
  isSimulating: boolean = false;
  simulationResults: any[] = [];
  lastSimulationMessage: string = '';
  
  // Playoff state
  playoffBracket: PlayoffBracket | null = null;
  nextPlayoffGames: PlayoffGame[] = [];
  currentRoundGames: PlayoffGame[] = [];
  playoffSimulationResults: any[] = [];
  
  // UI state
  activeTab: string = 'setup';
  error: string | null = null;
  loading: boolean = false;

  constructor() {
    makeAutoObservable(this);
  }

  setSelectedSeason(id: string | null) {
    this.selectedSeasonId = id;
    // Update currentSeason to match selected
    if (id) {
      const found = this.allSeasons.find(s => s.id === id);
      if (found) this.currentSeason = found;
    }
  }

  async fetchAllSeasons() {
    this.setLoading(true);
    this.setError(null);
    try {
      const response = await apiFetch('/api/seasons/all', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      const result = await response.json();
      if (result.success) {
        runInAction(() => {
          console.log('Fetched seasons:', result.seasons);
          this.allSeasons = result.seasons || [];
          // If no selectedSeasonId, pick most recent
          if (!this.selectedSeasonId && this.allSeasons.length > 0) {
            this.selectedSeasonId = this.allSeasons[0].id;
            this.currentSeason = this.allSeasons[0];
          }
          // If selectedSeasonId exists, update currentSeason
          if (this.selectedSeasonId) {
            const found = this.allSeasons.find(s => s.id === this.selectedSeasonId);
            if (found) this.currentSeason = found;
          }
        });
      }
      return result;
    } catch (error) {
      this.setError(`Network error: ${error}`);
      return { success: false, error: `Network error: ${error}` };
    } finally {
      this.setLoading(false);
    }
  }

  setActiveTab(tab: string) {
    this.activeTab = tab;
  }

  setError(error: string | null) {
    this.error = error;
  }

  setLoading(loading: boolean) {
    this.loading = loading;
  }

  // Season Management
  async createSeason(seasonYear: number = 2024, seed?: number, seasonName?: string) {
    this.setLoading(true);
    this.setError(null);

    try {
      const response = await apiFetch('/api/seasons/create', {
        method: 'POST',
        body: JSON.stringify({
          season_year: seasonYear,
          seed,
          season_name: seasonName || `NFL ${seasonYear} Season`
        })
      });

      const result = await response.json();

      if (result.success && result.data) {
        runInAction(() => {
          this.currentSeason = result.data.seasonId ? { 
            id: result.data.seasonId,
            season_year: seasonYear,
            season_name: seasonName || `NFL ${seasonYear} Season`,
            current_week: 1,
            current_phase: 'regular_season',
            completed_games: 0,
            total_games: 272, // 32 teams * 17 games / 2
            completion_percentage: 0
          } : null;
          this.selectedSeasonId = result.data.seasonId;
        });

        // Load additional data after creating season
        await this.loadTeams();
        
        // Load season status with the new season ID
        if (result.data.seasonId) {
          await this.loadSeasonStatus(result.data.seasonId);
          await this.loadNextGames();
        }

        return result;
      } else {
        this.setError(result.error || 'Failed to create season');
        return result;
      }
    } catch (error) {
      this.setError(`Network error: ${error}`);
      return { success: false, error: `Network error: ${error}` };
    } finally {
      this.setLoading(false);
    }
  }

  async loadSeasonStatus(seasonId?: string) {
    try {
// Debug: Log user and season info before status request
      const id = seasonId || this.selectedSeasonId;
      const paramsObj: Record<string, string> = {};
      if (id) paramsObj.season_id = id;
      const params = new URLSearchParams(paramsObj);
      const response = await apiFetch(`/api/seasons/status/${seasonId}`, {
        method: 'GET'
      });
      const result = await response.json();
      
      if (result.success) {
        console.log('Season status loaded:', result);
        runInAction(() => {
          this.currentSeason = result.season;
        });
      }
      
      return result;
    } catch (error) {
      console.error('Error loading season status:', error);
      return { success: false, error: `Network error: ${error}` };
    }
  }

  // No /api/season/teams endpoint in backend; consider removing or replacing this method.
  async loadTeams() {
    try {
      const response = await apiFetch('/api/teams/all');
      const result = await response.json();
      
      if (result.success && result.data) {
        runInAction(() => {
          this.teams = result.data;
        });
        return { success: true };
      } else {
        this.setError(result.error || 'Failed to load teams');
        return { success: false, error: result.error || 'Failed to load teams' };
      }
    } catch (error) {
      this.setError(`Network error: ${error}`);
      return { success: false, error: `Network error: ${error}` };
    }
  }

  async loadNextGames(limit: number = 16) {
    try {
      const seasonId = this.selectedSeasonId || this.currentSeason?.id;
      if (!seasonId) {
        return { success: false, error: 'No current season ID' };
      }
      const params = new URLSearchParams({ season_id: seasonId, user_id: DEFAULT_USER_ID, limit: limit.toString() });
      const response = await apiFetch(`/api/seasons/next-games/${this.selectedSeasonId}?${params.toString()}`, {
        method: 'GET',
      });
      const result = await response.json();
      
      if (result.success) {
        runInAction(() => {
          this.nextGames = result.games;
        });
      }
      
      return result;
    } catch (error) {
      console.error('Error loading next games:', error);
      return { success: false, error: `Network error: ${error}` };
    }
  }

  async loadWeekGames(week: number) {
    try {
      const seasonId = this.selectedSeasonId || this.currentSeason?.id;
      if (!seasonId) {
        return { success: false, error: 'No current season ID' };
      }
      const params = new URLSearchParams({ season_id: seasonId, user_id: DEFAULT_USER_ID });
      const response = await apiFetch(`/api/seasons/week-games/${this.selectedSeasonId}/${week}`, {
        method: 'GET',
      });
      const result = await response.json();
      
      if (result.success) {
        console.log('Week games loaded successfully:', result.games);
        runInAction(() => {
          this.currentWeekGames = result.games;
          this.selectedWeek = week;
        });
      }
      
      return result;
    } catch (error) {
      console.error('Error loading week games:', error);
      return { success: false, error: `Network error: ${error}` };
    }
  }

  async loadStandings(byDivision: boolean = true) {
    try {
      const seasonId = this.selectedSeasonId || this.currentSeason?.id;
      if (!seasonId) {
        return { success: false, error: 'No current season ID' };
      }
      const params = new URLSearchParams({ season_id: seasonId, user_id: DEFAULT_USER_ID, by_division: String(byDivision) });
      const response = await apiFetch(`/api/seasons/standings/${this.selectedSeasonId}`, {
        method: 'GET',
      });
      const result = await response.json();
      
      if (result.success) {
        runInAction(() => {
          this.standings = result.standings;
          this.standingsByDivision = byDivision;
        });
      }
      
      return result;
    } catch (error) {
      console.error('Error loading standings:', error);
      return { success: false, error: `Network error: ${error}` };
    }
  }

  // Simulation methods
  async simulateGame(gameId: string, seed?: number) {
    this.setLoading(true);
    this.setError(null);
    
    try {
      const response = await apiFetch('/api/seasons/simulate-game', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ game_id: gameId, seed })
      });
      
      const result = await response.json();
      
      if (result.success) {
        runInAction(() => {
          this.currentSeason = result.season;
          this.lastSimulationMessage = result.message;
          if (result.simulation_details) {
            this.simulationResults.unshift(result.simulation_details);
          }
        });
        
        // Refresh relevant data
        await this.loadNextGames();
        await this.loadStandings(this.standingsByDivision);
        
        return result;
      } else {
        this.setError(result.error || 'Failed to simulate game');
        return result;
      }
    } catch (error) {
      this.setError(`Network error: ${error}`);
      return { success: false, error: `Network error: ${error}` };
    } finally {
      this.setLoading(false);
    }
  }

  async simulateWeek(week?: number, seed?: number) {
    this.setLoading(true);
    this.setError(null);
    
    try {
      const response = await apiFetch('/api/seasons/simulate-week', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ week, seed })
      });
      
      const result = await response.json();
      
      if (result.success) {
        runInAction(() => {
          this.currentSeason = result.season;
          this.lastSimulationMessage = result.message;
          this.simulationResults.unshift(...result.simulated_games);
        });
        
        // Refresh all relevant data after week simulation
        await Promise.all([
          this.loadNextGames(),
          this.loadStandings(this.standingsByDivision),
          this.loadSeasonStatus() // Force refresh season status
        ]);
        
        // If we're viewing the current week, reload it to show updated status
        if (this.currentSeason) {
          await this.loadWeekGames(this.currentSeason.current_week);
        }
        
        return result;
      } else {
        this.setError(result.error || 'Failed to simulate week');
        return result;
      }
    } catch (error) {
      this.setError(`Network error: ${error}`);
      return { success: false, error: `Network error: ${error}` };
    } finally {
      this.setLoading(false);
    }
  }

  async simulateToWeek(targetWeek: number, seed?: number) {
    this.setLoading(true);
    this.setError(null);
    
    try {
      const response = await apiFetch('/api/seasons/simulate-to-week', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target_week: targetWeek, seed })
      });
      
      const result = await response.json();
      
      if (result.success) {
        runInAction(() => {
          this.currentSeason = result.season;
          this.lastSimulationMessage = result.message;
          this.simulationResults.unshift(...result.simulated_games);
        });
        
        // Refresh all relevant data after multi-week simulation
        await Promise.all([
          this.loadNextGames(),
          this.loadStandings(this.standingsByDivision),
          this.loadSeasonStatus() // Force refresh season status
        ]);
        
        // If we're viewing the current week, reload it to show updated status
        if (this.currentSeason) {
          await this.loadWeekGames(this.currentSeason.current_week);
        }
        
        return result;
      } else {
        this.setError(result.error || 'Failed to simulate to week');
        return result;
      }
    } catch (error) {
      this.setError(`Network error: ${error}`);
      return { success: false, error: `Network error: ${error}` };
    } finally {
      this.setLoading(false);
    }
  }

  async simulateFullSeason(seed?: number) {
    this.setLoading(true);
    this.setError(null);
    
    try {
      const response = await apiFetch('/api/seasons/simulate-season', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ seed })
      });
      
      const result = await response.json();
      
      if (result.success) {
        runInAction(() => {
          this.currentSeason = result.season;
          this.lastSimulationMessage = result.message;
          this.simulationResults.unshift(...result.simulated_games);
        });
        
        // Refresh all relevant data after full season simulation
        await Promise.all([
          this.loadNextGames(),
          this.loadStandings(this.standingsByDivision),
          this.loadSeasonStatus() // Force refresh season status
        ]);
        
        // If we're viewing the current week, reload it to show updated status
        if (this.currentSeason) {
          await this.loadWeekGames(this.currentSeason.current_week);
        }
        
        return result;
      } else {
        this.setError(result.error || 'Failed to simulate full season');
        return result;
      }
    } catch (error) {
      this.setError(`Network error: ${error}`);
      return { success: false, error: `Network error: ${error}` };
    } finally {
      this.setLoading(false);
    }
  }

  // Playoff methods
  async loadPlayoffBracket() {
    try {
      const response = await apiFetch(`/api/seasons/playoff-bracket/${this.selectedSeasonId}`);
      const result = await response.json();
      
      if (result.success) {
        runInAction(() => {
          this.playoffBracket = result.bracket;
        });
      }
      
      return result;
    } catch (error) {
      console.error('Error loading playoff bracket:', error);
      return { success: false, error: `Network error: ${error}` };
    }
  }

  async loadNextPlayoffGames() {
    try {
      const response = await apiFetch(`/api/seasons/next-games/${this.selectedSeasonId}`);
      const result = await response.json();
      
      if (result.success) {
        runInAction(() => {
          this.nextPlayoffGames = result.games;
        });
      }
      
      return result;
    } catch (error) {
      console.error('Error loading next playoff games:', error);
      return { success: false, error: `Network error: ${error}` };
    }
  }

  async simulatePlayoffGame(gameId: string, seed?: number) {
    this.setLoading(true);
    this.setError(null);
    
    try {
      const response = await apiFetch(`/api/seasons/simulate-playoff-game/${gameId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ game_id: gameId, seed })
      });
      
      const result = await response.json();
      
      if (result.success) {
        runInAction(() => {
          this.lastSimulationMessage = result.message;
          if (result.simulation_details) {
            this.playoffSimulationResults.unshift(result.simulation_details);
          }
          if (result.bracket_status) {
            this.playoffBracket = result.bracket_status;
          }
        });
        
        // Refresh playoff data
        await Promise.all([
          this.loadNextPlayoffGames(),
          this.loadSeasonStatus()
        ]);
        
        return result;
      } else {
        this.setError(result.error || 'Failed to simulate playoff game');
        return result;
      }
    } catch (error) {
      this.setError(`Network error: ${error}`);
      return { success: false, error: `Network error: ${error}` };
    } finally {
      this.setLoading(false);
    }
  }

  // Computed getters
  get hasActiveSeason() {
    return this.currentSeason !== null;
  }

  get seasonProgress() {
    if (!this.currentSeason) return 0;
    return this.currentSeason.completion_percentage;
  }

  get currentWeek() {
    return this.currentSeason?.current_week || 1;
  }

  get isSeasonComplete() {
    return this.currentSeason?.current_phase === 'offseason' ||
           (this.playoffBracket?.is_complete && this.currentSeason?.current_phase === 'playoffs');
  }

  get isInPlayoffs() {
    return this.currentSeason?.current_phase === 'playoffs';
  }

  get playoffGamesCount() {
    return this.nextPlayoffGames.length;
  }

  get nextGameCount() {
    return this.nextGames.length;
  }

  get scheduledGamesCount() {
    return this.nextGames.filter(game => game.status === 'scheduled').length;
  }

  clearSimulationResults() {
    this.simulationResults = [];
    this.playoffSimulationResults = [];
    this.lastSimulationMessage = '';
  }

  async startNewSeason(seasonYear?: number, seed?: number) {
    this.setLoading(true);
    this.setError(null);
    
    try {
      // Reset all state
      runInAction(() => {
        this.currentSeason = null;
        this.nextGames = [];
        this.currentWeekGames = [];
        this.selectedWeek = 1;
        this.standings = {};
        this.simulationResults = [];
        this.lastSimulationMessage = '';
        this.playoffBracket = null;
        this.nextPlayoffGames = [];
        this.currentRoundGames = [];
        this.playoffSimulationResults = [];
      });
      
      // Create new season
      const newSeasonYear = seasonYear || (new Date().getFullYear());
      const result = await this.createSeason(newSeasonYear, seed);
      
      if (result.success) {
        // Switch to Setup tab to show the new season
        this.setActiveTab('Setup');
      }
      
      return result;
    } catch (error) {
      this.setError(`Error starting new season: ${error}`);
      return { success: false, error: `Error starting new season: ${error}` };
    } finally {
      this.setLoading(false);
    }
  }
}

export const seasonStore = new SeasonStore();
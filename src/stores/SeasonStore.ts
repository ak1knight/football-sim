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
  record: {
    wins: number;
    losses: number;
    ties: number;
  };
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
  year: number;
  name: string;
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
  [conference: string]: { [division: string]: TeamRecord[] };
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
  selectedSeasonId: string | undefined = undefined;
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
    // Load teams on initialization
    this.loadTeams();
  }

  async loadTeams() {
    try {
      const response = await apiFetch('/api/teams/all', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      const result = await response.json();
      if (result.success && result.data) {
        runInAction(() => {
          this.teams = result.data;
          this.organizeTeams();
        });
      }
    } catch (error) {
      console.error('Failed to load teams:', error);
    }
  }

  organizeTeams() {
    const organized: OrganizedTeams = {};
    this.teams.forEach(team => {
      if (!organized[team.conference]) {
        organized[team.conference] = {};
      }
      if (!organized[team.conference][team.division]) {
        organized[team.conference][team.division] = [];
      }
      organized[team.conference][team.division].push(team);
    });
    this.organizedTeams = organized;
  }

  setSelectedSeason(id: string | undefined) {
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
          console.log('Fetched seasons:', result.data);
          this.allSeasons = result.data || [];
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
          year: seasonYear,
          seed,
          name: seasonName || `NFL ${seasonYear} Season`
        })
      });

      const result = await response.json();

      if (result.success && result.data) {
        runInAction(() => {
          this.currentSeason = result.data.seasonId ? { 
            id: result.data.seasonId,
            year: seasonYear,
            name: seasonName || `NFL ${seasonYear} Season`,
            current_week: 1,
            current_phase: 'regular_season',
            completed_games: 0,
            total_games: 272, // 32 teams * 17 games / 2
            completion_percentage: 0,
            next_games_count: 0,
            weeks_remaining: 17,
            schedule_type: 'balanced'
          } : null;
          this.selectedSeasonId = result.data.seasonId;
        });

        // Load additional data after creating season
        await this.loadTeams();
        
        // Load season status with the new season ID
        if (result.data.seasonId) {
          await this.loadSeasonStatus(result.data.seasonId);
          await this.loadNextGames();
          await this.loadWeekGames(1); // Load games for week 1
          await this.fetchAllSeasons();
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
      
      // If no season ID is available, skip the request
      if (!id) {
        console.log('🏈 [DEBUG] No season ID available, skipping season status load');
        return { success: false, error: 'No season ID provided' };
      }
      
      console.log(`🏈 [DEBUG] loadSeasonStatus called with ID: "${id}"`);
      console.log(`🏈 [DEBUG] selectedSeasonId: "${this.selectedSeasonId}"`);
      console.log(`🏈 [DEBUG] currentSeason?.id: "${this.currentSeason?.id}"`);
      
      const paramsObj: Record<string, string> = {};
      if (id) paramsObj.season_id = id;
      const params = new URLSearchParams(paramsObj);
      const response = await apiFetch(`/api/seasons/status/${id}`, {
        method: 'GET'
      });
      const result = await response.json();
      
      console.log(`🏈 [DEBUG] Season status response:`, result);
      
      if (result.success) {
        console.log('🏈 [DEBUG] Season status loaded successfully, updating current season');
        runInAction(() => {
          this.currentSeason = result.data;
          this.selectedSeasonId = id; // Ensure this is set correctly
        });
      } else {
        console.error('❌ [DEBUG] Failed to load season status:', result.error || result.message);
      }
      
      return result;
    } catch (error) {
      console.error('❌ [DEBUG] Error loading season status:', error);
      return { success: false, error: `Network error: ${error}` };
    }
  }

  // Removed duplicate loadTeams method - using the first implementation above

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
          this.nextGames = result.data;
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
        console.log('No season ID available for loading week games');
        return { success: false, error: 'No current season ID' };
      }
      
      console.log(`🏈 [DEBUG] Loading week ${week} games for season ID: "${seasonId}"`);
      console.log(`🏈 [DEBUG] Season ID length: ${seasonId.length}, type: ${typeof seasonId}`);
      
      const response = await apiFetch(`/api/seasons/week-games/${seasonId}/${week}`, {
        method: 'GET',
      });
      const result = await response.json();
      
      console.log(`🏈 [DEBUG] Week games API response:`, result);
      
      if (result.success) {
        console.log(`🏈 [DEBUG] Week games loaded successfully! Games count: ${result.data?.length || 0}`);
        if (result.data && result.data.length > 0) {
          console.log(`🏈 [DEBUG] First game:`, result.data[0]);
        }
        runInAction(() => {
          this.currentWeekGames = result.data;
          this.selectedWeek = week;
        });
      } else {
        console.error('❌ [DEBUG] Failed to load week games:', result.error || result.message);
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
        console.log('No season ID available for loading standings');
        return { success: false, error: 'No current season ID' };
      }
      
      console.log(`Loading standings for season ${seasonId}, byDivision: ${byDivision}`);
      const response = await apiFetch(`/api/seasons/standings/${seasonId}`, {
        method: 'GET',
      });
      const result = await response.json();
      
      if (result.success) {
        console.log('Standings loaded successfully:', result.data);
        runInAction(() => {
          this.standings = result.data.standings || {};
          this.standingsByDivision = byDivision;
        });
      } else {
        console.error('Failed to load standings:', result.error || result.message);
        runInAction(() => {
          this.standings = {};
        });
      }
      
      return result;
    } catch (error) {
      console.error('Error loading standings:', error);
      runInAction(() => {
        this.standings = {};
      });
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
          if (result.data.season_status) {
            this.currentSeason = result.data.season_status;
          }
          this.lastSimulationMessage = result.data.message || 'Game simulated successfully';
          if (result.data.simulation_details) {
            this.simulationResults.unshift(result.data.simulation_details);
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
    if (!this.selectedSeasonId) {
      console.error('No season selected for simulation');
      return { success: false, error: 'No season selected' };
    }
    
    this.setLoading(true);
    this.setError(null);

    console.log(`Simulating week ${week} for season ID: "${this.selectedSeasonId}"`);    
    try {
      const response = await apiFetch('/api/seasons/simulate-week', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          seasonId: this.selectedSeasonId || this.currentSeason?.id, // Added missing seasonId
          week, 
          seed 
        })
      });
      
      const result = await response.json();
      
      if (result.success) {
        runInAction(() => {
          if (result.data.season_status) {
            this.currentSeason = result.data.season_status;
          }
          this.lastSimulationMessage = result.data.message || 'Week simulated successfully';
          if (result.data.simulated_games) {
            this.simulationResults.unshift(...result.data.simulated_games);
          }
        });
        
        // Refresh all relevant data after simulation
        await Promise.all([
          this.loadNextGames(),
          this.loadStandings(this.standingsByDivision),
          this.loadSeasonStatus(this.selectedSeasonId) // Force refresh season status
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
        body: JSON.stringify({seasonId: this.selectedSeasonId || this.currentSeason?.id, targetWeek: targetWeek, seed })
      });
      
      const result = await response.json();
      
      if (result.success) {
        runInAction(() => {
          if (result.data.season_status) {
            this.currentSeason = result.data.season_status;
          }
          this.lastSimulationMessage = result.data.message || 'Simulation to week completed';
          if (result.data.simulated_games) {
            this.simulationResults.unshift(...result.data.simulated_games);
          }
        });
        
        // Refresh all relevant data after multi-week simulation
        await Promise.all([
          this.loadNextGames(),
          this.loadStandings(this.standingsByDivision),
          this.loadSeasonStatus(this.selectedSeasonId) // Force refresh season status
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
          if (result.data.season_status) {
            this.currentSeason = result.data.season_status;
          }
          this.lastSimulationMessage = result.data.message || 'Full season simulated successfully';
          if (result.data.simulated_games) {
            this.simulationResults.unshift(...result.data.simulated_games);
          }
        });
        
        // Refresh all relevant data after full season simulation
        await Promise.all([
          this.loadNextGames(),
          this.loadStandings(this.standingsByDivision),
          this.loadSeasonStatus(this.selectedSeasonId) // Force refresh season status
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

      console.log('Playoff bracket response:', result);
      
      if (result.success) {
        runInAction(() => {
          this.playoffBracket = result.data.bracket;
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

      console.log('Next playoff games response:', result);
      
      if (result.success) {
        runInAction(() => {
          console.log('Updating nextPlayoffGames with data:', result.data);
          this.nextPlayoffGames = result.data;
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
          this.loadSeasonStatus(this.selectedSeasonId)
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
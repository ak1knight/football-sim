import { makeAutoObservable, runInAction } from 'mobx';

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
  async createSeason(seasonYear: number = 2024, seed?: number) {
    this.setLoading(true);
    this.setError(null);
    
    try {
      const response = await fetch('/api/season/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ season_year: seasonYear, seed })
      });
      
      const result = await response.json();
      
      if (result.success) {
        runInAction(() => {
          this.currentSeason = result.season_status;
        });
        
        // Load additional data after creating season
        await this.loadTeams();
        await this.loadNextGames();
        
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

  async loadSeasonStatus() {
    try {
      const response = await fetch('/api/season/status');
      const result = await response.json();
      
      if (result.success) {
        runInAction(() => {
          this.currentSeason = result.season_status;
        });
      }
      
      return result;
    } catch (error) {
      console.error('Error loading season status:', error);
      return { success: false, error: `Network error: ${error}` };
    }
  }

  async loadTeams() {
    try {
      const response = await fetch('/api/season/teams');
      const result = await response.json();
      
      if (result.success) {
        runInAction(() => {
          this.teams = result.teams;
          this.organizedTeams = result.organized_teams;
        });
      }
      
      return result;
    } catch (error) {
      console.error('Error loading teams:', error);
      return { success: false, error: `Network error: ${error}` };
    }
  }

  async loadNextGames(limit: number = 16) {
    try {
      const response = await fetch(`/api/season/next-games?limit=${limit}`);
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
      const response = await fetch(`/api/season/week/${week}`);
      const result = await response.json();
      
      if (result.success) {
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
      const response = await fetch(`/api/season/standings?by_division=${byDivision}`);
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
      const response = await fetch('/api/season/simulate-game', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ game_id: gameId, seed })
      });
      
      const result = await response.json();
      
      if (result.success) {
        runInAction(() => {
          this.currentSeason = result.season_status;
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
      const response = await fetch('/api/season/simulate-week', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ week, seed })
      });
      
      const result = await response.json();
      
      if (result.success) {
        runInAction(() => {
          this.currentSeason = result.season_status;
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
      const response = await fetch('/api/season/simulate-to-week', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target_week: targetWeek, seed })
      });
      
      const result = await response.json();
      
      if (result.success) {
        runInAction(() => {
          this.currentSeason = result.season_status;
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
      const response = await fetch('/api/season/simulate-season', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ seed })
      });
      
      const result = await response.json();
      
      if (result.success) {
        runInAction(() => {
          this.currentSeason = result.season_status;
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
      const response = await fetch('/api/season/playoffs/bracket');
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
      const response = await fetch('/api/season/playoffs/next-games');
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
      const response = await fetch('/api/season/playoffs/simulate-game', {
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
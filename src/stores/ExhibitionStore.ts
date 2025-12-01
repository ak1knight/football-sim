import { makeAutoObservable, runInAction } from 'mobx';
import { apiFetch } from '../api';

export interface Team {
  id: string;
  name: string;
  city: string;
  abbreviation: string;
  conference?: string;
  division?: string;
}

export interface GameResult {
  homeTeam: Team;
  awayTeam: Team;
  homeScore: number;
  awayScore: number;
  quarter: number;
  timeRemaining: string;
  gameComplete: boolean;
  summary?: string;
  winner?: {
    team: Team | null;
    margin: number;
    tie?: boolean;
  };
  weather?: {
    condition: string;
    temperature: number;
    wind_speed: number;
    wind_direction: string;
  };
  detailedStats?: {
    total_plays: number;
    total_drives: number;
    turnovers: { home: number; away: number };
    time_of_possession: { home: number; away: number };
    yards_gained: { home: number; away: number };
    plays_by_type: { run: number; pass: number; turnover: number };
    average_yards_per_play: { home: number; away: number };
  };
  driveSummary?: Array<{
    drive_number: number;
    quarter: number;
    offense: string;
    starting_position: string;
    result: string;
    points: number;
    total_plays: number;
    total_yards: number;
  }>;
  keyPlays?: Array<{
    quarter: number;
    time: string;
    description: string;
    scoring_play: boolean;
    points?: number;
    yards?: number;
    play_type?: string;
  }>;
}

export class ExhibitionStore {
  teams: Team[] = [];
  selectedHomeTeam: Team | null = null;
  selectedAwayTeam: Team | null = null;
  gameResult: GameResult | null = null;
  isSimulating: boolean = false;
  isLoadingTeams: boolean = false;
  error: string | null = null;

  constructor() {
    makeAutoObservable(this);
  }

  setSelectedHomeTeam(team: Team | null) {
    this.selectedHomeTeam = team;
  }

  setSelectedAwayTeam(team: Team | null) {
    this.selectedAwayTeam = team;
  }

  async loadTeams() {
    this.isLoadingTeams = true;
    this.error = null;

    try {
      const response = await apiFetch('/api/teams/all');
      if (!response.ok) {
        throw new Error('Failed to fetch teams');
      }
      const data = await response.json();
      
      runInAction(() => {
        // Handle the teams response format from the IPC API
        if (data.success && data.data) {
          this.teams = data.data.map((team: any) => ({
            id: team.id,
            name: team.name,
            city: team.city,
            abbreviation: team.abbreviation,
            conference: team.conference,
            division: team.division
          }));
        } else {
          this.teams = [];
        }
        this.isLoadingTeams = false;
      });
    } catch (error) {
      runInAction(() => {
        this.error = error instanceof Error ? error.message : 'Unknown error';
        this.isLoadingTeams = false;
        // Fallback to mock data for development
        this.loadMockTeams();
      });
    }
  }

  private loadMockTeams() {
    this.teams = [
      { id: '1', name: 'Eagles', city: 'Philadelphia', abbreviation: 'PHI', conference: 'NFC', division: 'East' },
      { id: '2', name: 'Patriots', city: 'New England', abbreviation: 'NE', conference: 'AFC', division: 'East' },
      { id: '3', name: 'Cowboys', city: 'Dallas', abbreviation: 'DAL', conference: 'NFC', division: 'East' },
      { id: '4', name: 'Steelers', city: 'Pittsburgh', abbreviation: 'PIT', conference: 'AFC', division: 'North' },
      { id: '5', name: '49ers', city: 'San Francisco', abbreviation: 'SF', conference: 'NFC', division: 'West' },
      { id: '6', name: 'Chiefs', city: 'Kansas City', abbreviation: 'KC', conference: 'AFC', division: 'West' }
    ];
  }

  async simulateGame() {
    if (!this.selectedHomeTeam || !this.selectedAwayTeam) {
      this.error = 'Please select both teams';
      return;
    }

    this.isSimulating = true;
    this.error = null;

    try {
      const response = await apiFetch(`/api/exhibition/simulate?homeTeam=${this.selectedHomeTeam.id}&awayTeam=${this.selectedAwayTeam.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          game_settings: {
            detailed_stats: true
          }
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to simulate game');
      }

      const result = await response.json();
      
      runInAction(() => {
        if (result.success && result.data) {
          const gameData = result.data;
          
          this.gameResult = {
            homeTeam: {
              id: gameData.home_team.id,
              name: gameData.home_team.name,
              city: gameData.home_team.name.split(' ')[0], // Extract city from full name
              abbreviation: gameData.home_team.abbreviation
            },
            awayTeam: {
              id: gameData.away_team.id,
              name: gameData.away_team.name,
              city: gameData.away_team.name.split(' ')[0], // Extract city from full name  
              abbreviation: gameData.away_team.abbreviation
            },
            homeScore: gameData.home_team.score,
            awayScore: gameData.away_team.score,
            quarter: 4,
            timeRemaining: '00:00',
            gameComplete: true,
            summary: gameData.summary || `Final Score: ${gameData.away_team.name} ${gameData.away_team.score} - ${gameData.home_team.name} ${gameData.home_team.score}`,
            winner: gameData.winner ? {
              team: gameData.winner === 'home' ? this.gameResult?.homeTeam || null : 
                    gameData.winner === 'away' ? this.gameResult?.awayTeam || null : null,
              margin: Math.abs(gameData.home_team.score - gameData.away_team.score),
              tie: gameData.winner === 'tie'
            } : undefined,
            weather: gameData.weather,
            detailedStats: gameData.detailed_stats ? {
              total_plays: (gameData.detailed_stats.home?.plays || 0) + (gameData.detailed_stats.away?.plays || 0),
              total_drives: gameData.drives?.length || 0,
              turnovers: { 
                home: gameData.detailed_stats.home?.turnovers || 0, 
                away: gameData.detailed_stats.away?.turnovers || 0 
              },
              time_of_possession: { 
                home: gameData.detailed_stats.home?.timeOfPossession || 0, 
                away: gameData.detailed_stats.away?.timeOfPossession || 0 
              },
              yards_gained: { 
                home: gameData.detailed_stats.home?.totalYards || 0, 
                away: gameData.detailed_stats.away?.totalYards || 0 
              },
              plays_by_type: { 
                run: 0, // Would need to calculate from play-by-play
                pass: 0, // Would need to calculate from play-by-play
                turnover: (gameData.detailed_stats.home?.turnovers || 0) + (gameData.detailed_stats.away?.turnovers || 0)
              },
              average_yards_per_play: { 
                home: gameData.detailed_stats.home ? (gameData.detailed_stats.home.totalYards / Math.max(gameData.detailed_stats.home.plays, 1)) : 0,
                away: gameData.detailed_stats.away ? (gameData.detailed_stats.away.totalYards / Math.max(gameData.detailed_stats.away.plays, 1)) : 0
              }
            } : undefined,
            driveSummary: gameData.drives?.map((drive: any, index: number) => ({
              drive_number: index + 1,
              quarter: 1, // Would need to calculate from drive data
              offense: drive.team || 'Unknown',
              starting_position: drive.startPosition || 'Unknown',
              result: drive.result || 'Unknown',
              points: drive.points || 0,
              total_plays: drive.plays || 0,
              total_yards: drive.yards || 0
            })) || []
          };
        } else {
          throw new Error(result.error || 'Unknown error from simulation');
        }
        this.isSimulating = false;
      });
    } catch (error) {
      runInAction(() => {
        this.error = error instanceof Error ? error.message : 'Unknown error';
        this.isSimulating = false;
        // Fallback to mock simulation for development
        this.mockSimulateGame();
      });
    }
  }

  private mockSimulateGame() {
    if (!this.selectedHomeTeam || !this.selectedAwayTeam) return;

    // Mock simulation result
    const homeScore = Math.floor(Math.random() * 35) + 7;
    const awayScore = Math.floor(Math.random() * 35) + 7;

    this.gameResult = {
      homeTeam: this.selectedHomeTeam,
      awayTeam: this.selectedAwayTeam,
      homeScore,
      awayScore,
      quarter: 4,
      timeRemaining: '00:00',
      gameComplete: true,
      summary: `Final Score: ${this.selectedHomeTeam.city} ${homeScore} - ${this.selectedAwayTeam.city} ${awayScore}`
    };
  }

  resetGame() {
    this.gameResult = null;
    this.selectedHomeTeam = null;
    this.selectedAwayTeam = null;
    this.error = null;
  }

  get canSimulate() {
    return this.selectedHomeTeam && this.selectedAwayTeam && !this.isSimulating;
  }

  get availableAwayTeams() {
    return this.teams.filter(team => team.abbreviation !== this.selectedHomeTeam?.abbreviation);
  }

  get availableHomeTeams() {
    return this.teams.filter(team => team.abbreviation !== this.selectedAwayTeam?.abbreviation);
  }
}

export const exhibitionStore = new ExhibitionStore();
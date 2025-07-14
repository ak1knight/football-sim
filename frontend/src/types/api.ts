/**
 * TypeScript types for the Football Simulation API.
 * These mirror the Python models used in the backend.
 */

export interface Team {
  abbreviation: string;
  name: string;
  city: string;
  conference: string;
  division: string;
  colors?: {
    primary: string;
    secondary: string;
  };
}

export interface Weather {
  condition: 'clear' | 'cloudy' | 'rain' | 'snow' | 'windy';
  temperature: number;
  wind_speed: number;
  wind_direction: string;
}

export interface GameSettings {
  overtime: boolean;
  detailed_stats: boolean;
}

export interface ExhibitionGameRequest {
  home_team: string;
  away_team: string;
  weather?: Weather;
  game_settings?: GameSettings;
}

export interface GameResult {
  home_team: {
    abbreviation: string;
    name: string;
    city: string;
    score: number;
  };
  away_team: {
    abbreviation: string;
    name: string;
    city: string;
    score: number;
  };
  final_score: string;
  winner: {
    team: {
      abbreviation: string;
      name: string;
      city: string;
    } | null;
    margin: number;
    tie?: boolean;
  };
  overtime: boolean;
  game_duration: number;
  weather: Weather;
  detailed_stats?: {
    total_plays: number;
    total_drives: number;
    turnovers: {
      home: number;
      away: number;
    };
    time_of_possession: {
      home: number;
      away: number;
    };
    yards_gained: {
      home: number;
      away: number;
    };
    plays_by_type: {
      run: number;
      pass: number;
      turnover: number;
    };
    average_yards_per_play: {
      home: number;
      away: number;
    };
  };
  drive_summary?: Array<{
    drive_number: number;
    quarter: number;
    offense: string;
    starting_position: number;
    result: string;
    points: number;
    total_plays: number;
    total_yards: number;
    plays: Array<{
      down: number;
      yards_to_go: number;
      play_type: string;
      yards_gained: number;
      description: string;
    }>;
  }>;
  key_plays?: Array<{
    quarter: number;
    time: string;
    description: string;
    scoring_play: boolean;
    points?: number;
    yards?: number;
    play_type?: string;
  }>;
}

export interface ExhibitionGameResponse {
  success: boolean;
  game_result?: GameResult;
  error?: string;
}

export interface TeamsResponse {
  success: boolean;
  teams: Team[];
  total_teams: number;
  error?: string;
}

export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
}

import { Team } from '../database/dao/team-dao';
import { NFLScheduleGenerator, ScheduleGenerator } from './schedule-generator';
import { PlayoffEngine, PlayoffBracket } from './playoff-engine';

export enum GameStatus {
  SCHEDULED = 'scheduled',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  POSTPONED = 'postponed',
}

export enum SeasonPhase {
  PRESEASON = 'preseason',
  REGULAR_SEASON = 'regular_season',
  PLAYOFFS = 'playoffs',
  OFFSEASON = 'offseason',
}

export interface ScheduledGame {
  game_id: string;
  home_team: Team;
  away_team: Team;
  week: number;
  status: GameStatus;
  scheduled_date?: string;
  home_score?: number;
  away_score?: number;
  overtime?: boolean;
  game_duration?: number;
}

export class TeamRecord {
  constructor(
    public team: Team,
    public wins = 0,
    public losses = 0,
    public ties = 0,
    public points_for = 0,
    public points_against = 0,
    public division_wins = 0,
    public division_losses = 0,
    public conference_wins = 0,
    public conference_losses = 0,
  ) {}

  get win_percentage(): number {
    const total = this.wins + this.losses + this.ties;
    return total === 0 ? 0 : (this.wins + 0.5 * this.ties) / total;
  }

  get point_differential(): number {
    return this.points_for - this.points_against;
  }

  get games_played(): number {
    return this.wins + this.losses + this.ties;
  }

  toJSON() {
    return {
      team: {
        name: this.team.name,
        city: this.team.city,
        abbreviation: this.team.abbreviation,
        conference: this.team.conference,
        division: this.team.division,
      },
      wins: this.wins,
      losses: this.losses,
      ties: this.ties,
      win_percentage: Number(this.win_percentage.toFixed(3)),
      points_for: this.points_for,
      points_against: this.points_against,
      point_differential: this.point_differential,
      division_record: `${this.division_wins}-${this.division_losses}`,
      conference_record: `${this.conference_wins}-${this.conference_losses}`,
      games_played: this.games_played,
    };
  }
}

export interface SeasonEngineOptions {
  teams: Team[];
  seasonYear: number;
  seed?: number;
  scheduleGenerator?: ScheduleGenerator;
  currentWeek?: number;
  currentPhase?: SeasonPhase;
  schedule?: ScheduledGame[];
  records?: Record<string, TeamRecord>;
  completedGames?: ScheduledGame[];
}

export class SeasonEngine {
  teams: Team[];
  seasonYear: number;
  seed?: number;
  scheduleGenerator: ScheduleGenerator;
  currentWeek: number;
  currentPhase: SeasonPhase;
  schedule: ScheduledGame[];
  records: Record<string, TeamRecord>;
  completedGames: ScheduledGame[];
  playoffEngine?: PlayoffEngine;

  constructor(options: SeasonEngineOptions) {
    this.teams = options.teams;
    this.seasonYear = options.seasonYear;
    this.seed = options.seed;
    this.scheduleGenerator = options.scheduleGenerator || new NFLScheduleGenerator();
    this.currentWeek = options.currentWeek ?? 1;
    this.currentPhase = options.currentPhase ?? SeasonPhase.REGULAR_SEASON;
    this.schedule = options.schedule ?? [];
    this.completedGames = options.completedGames ?? [];
    this.records =
      options.records ||
      Object.fromEntries(this.teams.map((team) => [team.id, new TeamRecord(team)]));

    if (this.schedule.length === 0) {
      this.generateSchedule();
    }

    this.recalculateRecords();
  }

  generateSchedule(): void {
    const weekly = this.scheduleGenerator.generateSchedule(this.teams, this.seasonYear, this.seed);
    this.schedule = [];
    let counter = 0;
    Object.entries(weekly).forEach(([week, games]) => {
      games.forEach((game) => {
        this.schedule.push({
          game_id: `${this.seasonYear}_W${String(week).padStart(2, '0')}_G${String(counter++).padStart(3, '0')}`,
          home_team: game.home,
          away_team: game.away,
          week: parseInt(week, 10),
          status: GameStatus.SCHEDULED,
        });
      });
    });
  }

  recalculateRecords(): void {
    // Reset
    for (const team of this.teams) {
      this.records[team.id] = new TeamRecord(team);
    }

    const completedGames = this.schedule.filter((g) => g.status === GameStatus.COMPLETED);
    for (const game of completedGames) {
      if (game.home_score === undefined || game.away_score === undefined) continue;
      this.updateTeamRecords(game);
    }
  }

  getNextGames(limit = 16): ScheduledGame[] {
    const next: ScheduledGame[] = [];
    for (const game of this.schedule) {
      if (game.status === GameStatus.SCHEDULED) {
        next.push(game);
        if (next.length >= limit) break;
      }
    }
    return next;
  }

  getWeekGames(week: number): ScheduledGame[] {
    return this.schedule.filter((g) => g.week === week);
  }

  processGameResult(gameId: string, homeScore: number, awayScore: number, overtime = false, gameDuration = 60): boolean {
    const game = this.schedule.find((g) => g.game_id === gameId);
    if (!game) return false;

    game.home_score = homeScore;
    game.away_score = awayScore;
    game.overtime = overtime;
    game.game_duration = gameDuration;
    game.status = GameStatus.COMPLETED;
    this.completedGames.push(game);

    this.updateTeamRecords(game);
    this.checkWeekAdvancement();
    return true;
  }

  getStandings(byDivision = true): Record<string, TeamRecord[]> {
    if (byDivision) {
      return this.getDivisionStandings();
    }
    return this.getConferenceStandings();
  }

  getSeasonStatus() {
    const totalGames = this.schedule.length;
    const completedGames = this.completedGames.length;
    const totalWeeks = this.scheduleGenerator.getTotalWeeks();
    const scheduledGames = this.schedule.filter((g) => g.status === GameStatus.SCHEDULED).length;

    return {
      season_year: this.seasonYear,
      current_week: this.currentWeek,
      current_phase: this.currentPhase,
      total_games: totalGames,
      completed_games: completedGames,
      completion_percentage: totalGames > 0 ? Math.round((completedGames / totalGames) * 1000) / 10 : 0,
      next_games_count: scheduledGames,
      weeks_remaining: this.currentPhase === SeasonPhase.REGULAR_SEASON ? Math.max(0, totalWeeks - this.currentWeek + 1) : 0,
      schedule_type: this.scheduleGenerator.getScheduleName(),
    };
  }

  getPlayoffPicture() {
    const playoffEngine = this.playoffEngine ?? new PlayoffEngine(this.seasonYear, Object.values(this.records));
    if (!playoffEngine.bracket) {
      playoffEngine.generatePlayoffBracket();
    }
    return playoffEngine.getBracketStatus();
  }

  getPlayoffBracket(): PlayoffBracket | null {
    const engine = this.playoffEngine ?? new PlayoffEngine(this.seasonYear, Object.values(this.records));
    if (!engine.bracket) {
      engine.generatePlayoffBracket();
    }
    return engine.bracket;
  }

  getNextPlayoffGames() {
    const engine = this.playoffEngine ?? new PlayoffEngine(this.seasonYear, Object.values(this.records));
    if (!engine.bracket) engine.generatePlayoffBracket();
    return engine.getNextPlayoffGames();
  }

  private getDivisionStandings(): Record<string, TeamRecord[]> {
    const divisions: Record<string, TeamRecord[]> = {};
    Object.values(this.records).forEach((record) => {
      const key = `${record.team.conference} ${record.team.division}`;
      divisions[key] = divisions[key] || [];
      divisions[key].push(record);
    });

    Object.keys(divisions).forEach((division) => {
      divisions[division].sort((a, b) => {
        if (b.win_percentage !== a.win_percentage) return b.win_percentage - a.win_percentage;
        if (b.point_differential !== a.point_differential) return b.point_differential - a.point_differential;
        return b.division_wins - a.division_wins;
      });
    });

    return divisions;
  }

  private getConferenceStandings(): Record<string, TeamRecord[]> {
    const conferences: Record<string, TeamRecord[]> = {};
    Object.values(this.records).forEach((record) => {
      conferences[record.team.conference] = conferences[record.team.conference] || [];
      conferences[record.team.conference].push(record);
    });

    Object.keys(conferences).forEach((conference) => {
      conferences[conference].sort((a, b) => {
        if (b.win_percentage !== a.win_percentage) return b.win_percentage - a.win_percentage;
        if (b.point_differential !== a.point_differential) return b.point_differential - a.point_differential;
        return b.conference_wins - a.conference_wins;
      });
    });

    return conferences;
  }

  private updateTeamRecords(game: ScheduledGame): void {
    if (game.home_score === undefined || game.away_score === undefined) return;
    const homeTeam = game.home_team;
    const awayTeam = game.away_team;
    const homeRecord = this.records[homeTeam.id] || new TeamRecord(homeTeam);
    const awayRecord = this.records[awayTeam.id] || new TeamRecord(awayTeam);

    homeRecord.points_for += game.home_score;
    homeRecord.points_against += game.away_score;
    awayRecord.points_for += game.away_score;
    awayRecord.points_against += game.home_score;

    if (game.home_score > game.away_score) {
      homeRecord.wins += 1;
      awayRecord.losses += 1;
    } else if (game.away_score > game.home_score) {
      awayRecord.wins += 1;
      homeRecord.losses += 1;
    } else {
      homeRecord.ties += 1;
      awayRecord.ties += 1;
    }

    const divisionGame = this.isDivisionGame(homeTeam, awayTeam);
    const conferenceGame = this.isConferenceGame(homeTeam, awayTeam);
    if (divisionGame) {
      if (game.home_score > game.away_score) {
        homeRecord.division_wins += 1;
        awayRecord.division_losses += 1;
      } else if (game.away_score > game.home_score) {
        awayRecord.division_wins += 1;
        homeRecord.division_losses += 1;
      }
    }
    if (conferenceGame) {
      if (game.home_score > game.away_score) {
        homeRecord.conference_wins += 1;
        awayRecord.conference_losses += 1;
      } else if (game.away_score > game.home_score) {
        awayRecord.conference_wins += 1;
        homeRecord.conference_losses += 1;
      }
    }

    this.records[homeTeam.id] = homeRecord;
    this.records[awayTeam.id] = awayRecord;
  }

  private isDivisionGame(team1: Team, team2: Team): boolean {
    return team1.conference === team2.conference && team1.division === team2.division;
  }

  private isConferenceGame(team1: Team, team2: Team): boolean {
    return team1.conference === team2.conference;
  }

  private checkWeekAdvancement(): void {
    const currentWeekGames = this.getWeekGames(this.currentWeek);
    if (currentWeekGames.length === 0) return;

    if (currentWeekGames.every((g) => g.status === GameStatus.COMPLETED)) {
      this.currentWeek += 1;
      if (this.currentWeek > this.scheduleGenerator.getTotalWeeks()) {
        this.currentPhase = SeasonPhase.PLAYOFFS;
        this.initializePlayoffs();
      }
    }
  }

  private initializePlayoffs(): void {
    this.playoffEngine = new PlayoffEngine(this.seasonYear, Object.values(this.records));
    this.playoffEngine.generatePlayoffBracket();
  }
}

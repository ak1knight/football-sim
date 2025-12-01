import { Team } from '../database/dao/team-dao';
import { TeamRecord } from './season-engine';

export enum PlayoffRound {
  WILD_CARD = 'wild_card',
  DIVISIONAL = 'divisional',
  CONFERENCE_CHAMPIONSHIP = 'conference_championship',
  SUPER_BOWL = 'super_bowl',
}

export interface PlayoffTeam {
  team: Team;
  seed: number;
  division_winner: boolean;
  wild_card: boolean;
  wins: number;
  losses: number;
  ties: number;
  win_percentage: number;
  points_for: number;
  points_against: number;
  point_differential: number;
  division_wins: number;
  conference_wins: number;
}

export interface PlayoffGame {
  game_id: string;
  round: PlayoffRound;
  conference: string;
  game_number: number;
  higher_seed: PlayoffTeam | null;
  lower_seed: PlayoffTeam | null;
  home_team: Team | null;
  away_team: Team | null;
  scheduled_date?: string;
  home_score?: number;
  away_score?: number;
  winner?: Team;
  overtime?: boolean;
  completed: boolean;
}

export interface PlayoffBracket {
  season_year: number;
  afc_teams: PlayoffTeam[];
  nfc_teams: PlayoffTeam[];
  wild_card_games: PlayoffGame[];
  divisional_games: PlayoffGame[];
  conference_championship_games: PlayoffGame[];
  super_bowl: PlayoffGame | null;
  afc_champion: PlayoffTeam | null;
  nfc_champion: PlayoffTeam | null;
  super_bowl_champion: PlayoffTeam | null;
  current_round: PlayoffRound;
}

export class PlayoffEngine {
  bracket: PlayoffBracket | null = null;

  constructor(private seasonYear: number, private records: TeamRecord[]) {}

  generatePlayoffBracket(): PlayoffBracket {
    const afcTeams = this.getPlayoffTeams('AFC');
    const nfcTeams = this.getPlayoffTeams('NFC');

    this.bracket = {
      season_year: this.seasonYear,
      afc_teams: afcTeams,
      nfc_teams: nfcTeams,
      wild_card_games: [],
      divisional_games: [],
      conference_championship_games: [],
      super_bowl: null,
      afc_champion: null,
      nfc_champion: null,
      super_bowl_champion: null,
      current_round: PlayoffRound.WILD_CARD,
    };

    this.generateWildCardGames();
    return this.bracket;
  }

  getNextPlayoffGames(): PlayoffGame[] {
    if (!this.bracket) return [];
    const round = this.bracket.current_round;
    const games = this.getGamesByRound(round);
    return games.filter((g) => this.isReady(g) && !g.completed);
  }

  advanceBracket(gameId: string, winner: Team, homeScore: number, awayScore: number, overtime = false): boolean {
    if (!this.bracket) return false;
    const game = this.getAllGames().find((g) => g.game_id === gameId);
    if (!game) return false;

    game.home_score = homeScore;
    game.away_score = awayScore;
    game.winner = winner;
    game.overtime = overtime;
    game.completed = true;

    if (this.isRoundComplete(this.bracket.current_round)) {
      this.advanceRound();
    }
    return true;
  }

  getBracketStatus() {
    if (!this.bracket) {
      this.generatePlayoffBracket();
    }
    return {
      ...this.bracket!,
      next_games: this.getNextPlayoffGames(),
      is_complete:
        this.bracket?.current_round === PlayoffRound.SUPER_BOWL &&
        !!this.bracket?.super_bowl &&
        this.bracket?.super_bowl.completed,
    };
  }

  private getPlayoffTeams(conference: string): PlayoffTeam[] {
    const conferenceRecords = this.records.filter((r) => r.team.conference === conference);
    const divisionWinners = this.getDivisionWinners(conferenceRecords);
    divisionWinners.sort((a, b) => this.compareRecords(a, b));

    const wildCardCandidates = conferenceRecords.filter((r) => !divisionWinners.includes(r));
    wildCardCandidates.sort((a, b) => this.compareRecords(a, b));
    const wildCards = wildCardCandidates.slice(0, 3);

    const playoffTeams: PlayoffTeam[] = [];
    divisionWinners.forEach((record, idx) => playoffTeams.push(this.toPlayoffTeam(record, idx + 1, true, false)));
    wildCards.forEach((record, idx) => playoffTeams.push(this.toPlayoffTeam(record, idx + 5, false, true)));

    return playoffTeams;
  }

  private getDivisionWinners(conferenceRecords: TeamRecord[]): TeamRecord[] {
    const divisions: Record<string, TeamRecord[]> = {};
    for (const record of conferenceRecords) {
      const key = `${record.team.conference} ${record.team.division}`;
      divisions[key] = divisions[key] || [];
      divisions[key].push(record);
    }

    const winners: TeamRecord[] = [];
    for (const division of Object.values(divisions)) {
      const winner = division.sort((a, b) => this.compareRecords(a, b))[0];
      if (winner) winners.push(winner);
    }
    return winners;
  }

  private compareRecords(a: TeamRecord, b: TeamRecord): number {
    if (b.win_percentage !== a.win_percentage) return b.win_percentage - a.win_percentage;
    if (b.point_differential !== a.point_differential) return b.point_differential - a.point_differential;
    if (b.division_wins !== a.division_wins) return b.division_wins - a.division_wins;
    return b.conference_wins - a.conference_wins;
  }

  private toPlayoffTeam(record: TeamRecord, seed: number, division_winner: boolean, wild_card: boolean): PlayoffTeam {
    return {
      team: record.team,
      seed,
      division_winner,
      wild_card,
      wins: record.wins,
      losses: record.losses,
      ties: record.ties,
      win_percentage: record.win_percentage,
      points_for: record.points_for,
      points_against: record.points_against,
      point_differential: record.point_differential,
      division_wins: record.division_wins,
      conference_wins: record.conference_wins,
    };
  }

  private generateWildCardGames() {
    if (!this.bracket) return;
    const baseDate = new Date(this.seasonYear, 0, 13); // mid-Jan
    const makeGames = (teams: PlayoffTeam[], conference: string, offset: number) => {
      const matchups: Array<[number, number]> = [
        [2, 7],
        [3, 6],
        [4, 5],
      ];
      let gameCounter = 1;
      for (const [higher, lower] of matchups) {
        const higherSeed = teams.find((t) => t.seed === higher) || null;
        const lowerSeed = teams.find((t) => t.seed === lower) || null;
        this.bracket!.wild_card_games.push({
          game_id: `${this.seasonYear}_WC_${conference}_${gameCounter}`,
          round: PlayoffRound.WILD_CARD,
          conference,
          game_number: gameCounter,
          higher_seed: higherSeed,
          lower_seed: lowerSeed,
          home_team: higherSeed?.team || null,
          away_team: lowerSeed?.team || null,
          scheduled_date: new Date(baseDate.getTime() + (gameCounter + offset) * 24 * 60 * 60 * 1000).toISOString(),
          completed: false,
        });
        gameCounter += 1;
      }
    };

    makeGames(this.bracket.afc_teams, 'AFC', 0);
    makeGames(this.bracket.nfc_teams, 'NFC', 3);
  }

  private setupDivisionalGames() {
    if (!this.bracket) return;
    const baseDate = new Date(this.seasonYear, 0, 20);
    this.bracket.divisional_games = [];

    const setupForConference = (teams: PlayoffTeam[], games: PlayoffGame[], conference: string) => {
      const oneSeed = teams.find((t) => t.seed === 1);
      const winners = this.bracket?.wild_card_games
        .filter((g) => g.conference === conference && g.completed && g.winner)
        .map((g) => this.findPlayoffTeam(teams, g.winner!))
        .filter((t): t is PlayoffTeam => !!t);
      if (!oneSeed || !winners || winners.length < 2) return;

      winners.sort((a, b) => a.seed - b.seed);
      const lowest = winners[winners.length - 1];
      const highest = winners[0];

      const matchups: Array<[PlayoffTeam, PlayoffTeam]> = [
        [oneSeed, lowest],
        [highest, winners[1] || lowest],
      ];

      matchups.forEach(([higher, lower], idx) => {
        games.push({
          game_id: `${this.seasonYear}_DIV_${conference}_${idx + 1}`,
          round: PlayoffRound.DIVISIONAL,
          conference,
          game_number: idx + 1,
          higher_seed: higher,
          lower_seed: lower,
          home_team: higher.team,
          away_team: lower.team,
          scheduled_date: new Date(baseDate.getTime() + idx * 24 * 60 * 60 * 1000).toISOString(),
          completed: false,
        });
      });
    };

    setupForConference(this.bracket.afc_teams, this.bracket.divisional_games, 'AFC');
    setupForConference(this.bracket.nfc_teams, this.bracket.divisional_games, 'NFC');
  }

  private setupConferenceChampionships() {
    if (!this.bracket) return;
    const baseDate = new Date(this.seasonYear, 0, 27);
    this.bracket.conference_championship_games = [];

    const setup = (conference: string, teams: PlayoffTeam[]) => {
      const winners = this.bracket?.divisional_games
        .filter((g) => g.conference === conference && g.completed && g.winner)
        .map((g) => this.findPlayoffTeam(teams, g.winner!))
        .filter((t): t is PlayoffTeam => !!t);
      if (!winners || winners.length < 2) return;

      winners.sort((a, b) => a.seed - b.seed);
      const higher = winners[0];
      const lower = winners[1];
      this.bracket!.conference_championship_games.push({
        game_id: `${this.seasonYear}_CONF_${conference}_1`,
        round: PlayoffRound.CONFERENCE_CHAMPIONSHIP,
        conference,
        game_number: 1,
        higher_seed: higher,
        lower_seed: lower,
        home_team: higher.team,
        away_team: lower.team,
        scheduled_date: baseDate.toISOString(),
        completed: false,
      });
    };

    setup('AFC', this.bracket.afc_teams);
    setup('NFC', this.bracket.nfc_teams);
  }

  private setupSuperBowl() {
    if (!this.bracket) return;
    const baseDate = new Date(this.seasonYear, 1, 10);
    const afcWinner = this.bracket.conference_championship_games.find((g) => g.conference === 'AFC' && g.completed && g.winner);
    const nfcWinner = this.bracket.conference_championship_games.find((g) => g.conference === 'NFC' && g.completed && g.winner);
    if (!afcWinner?.winner || !nfcWinner?.winner) return;

    const afcTeam = this.findPlayoffTeam(this.bracket.afc_teams, afcWinner.winner);
    const nfcTeam = this.findPlayoffTeam(this.bracket.nfc_teams, nfcWinner.winner);
    if (!afcTeam || !nfcTeam) return;

    const higher = afcTeam.seed < nfcTeam.seed ? afcTeam : nfcTeam;
    const lower = higher === afcTeam ? nfcTeam : afcTeam;

    this.bracket.super_bowl = {
      game_id: `${this.seasonYear}_SB_1`,
      round: PlayoffRound.SUPER_BOWL,
      conference: 'NFL',
      game_number: 1,
      higher_seed: higher,
      lower_seed: lower,
      home_team: higher.team,
      away_team: lower.team,
      scheduled_date: baseDate.toISOString(),
      completed: false,
    };
  }

  private advanceRound() {
    if (!this.bracket) return;
    if (this.bracket.current_round === PlayoffRound.WILD_CARD) {
      this.bracket.current_round = PlayoffRound.DIVISIONAL;
      this.setupDivisionalGames();
    } else if (this.bracket.current_round === PlayoffRound.DIVISIONAL) {
      this.bracket.current_round = PlayoffRound.CONFERENCE_CHAMPIONSHIP;
      this.setupConferenceChampionships();
    } else if (this.bracket.current_round === PlayoffRound.CONFERENCE_CHAMPIONSHIP) {
      this.bracket.current_round = PlayoffRound.SUPER_BOWL;
      this.setupSuperBowl();
    }
  }

  private isRoundComplete(round: PlayoffRound): boolean {
    return this.getGamesByRound(round).every((g) => g.completed);
  }

  private getGamesByRound(round: PlayoffRound): PlayoffGame[] {
    if (!this.bracket) return [];
    if (round === PlayoffRound.WILD_CARD) return this.bracket.wild_card_games;
    if (round === PlayoffRound.DIVISIONAL) return this.bracket.divisional_games;
    if (round === PlayoffRound.CONFERENCE_CHAMPIONSHIP) return this.bracket.conference_championship_games;
    if (round === PlayoffRound.SUPER_BOWL) return this.bracket.super_bowl ? [this.bracket.super_bowl] : [];
    return [];
  }

  private getAllGames(): PlayoffGame[] {
    if (!this.bracket) return [];
    const all: PlayoffGame[] = [];
    all.push(...this.bracket.wild_card_games);
    all.push(...this.bracket.divisional_games);
    all.push(...this.bracket.conference_championship_games);
    if (this.bracket.super_bowl) all.push(this.bracket.super_bowl);
    return all;
  }

  private isReady(game: PlayoffGame): boolean {
    return !!game.higher_seed && !!game.lower_seed;
  }

  private findPlayoffTeam(pool: PlayoffTeam[], team: Team): PlayoffTeam | undefined {
    return pool.find((t) => t.team.id === team.id || t.team.abbreviation === team.abbreviation);
  }
}

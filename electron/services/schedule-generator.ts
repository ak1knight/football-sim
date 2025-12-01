import { Team } from '../database/dao/team-dao';

export interface ScheduleGenerator {
  generateSchedule(teams: Team[], seasonYear: number, seed?: number): Record<number, Array<{ home: Team; away: Team }>>;
  getTotalWeeks(): number;
  getGamesPerTeam(): number;
  getScheduleName(): string;
}

type Rng = () => number;

export class NFLScheduleGenerator implements ScheduleGenerator {
  private totalWeeks = 18;
  private gamesPerTeam = 17;

  generateSchedule(teams: Team[], _seasonYear: number, seed?: number): Record<number, Array<{ home: Team; away: Team }>> {
    const rng = seed !== undefined ? this.createSeededRandom(seed) : Math.random;
    const byDivision = this.organizeByDivision(teams);
    const matchups: Array<{ home: Team; away: Team }> =
      teams.length === 32 && Object.keys(byDivision).length === 8
        ? this.buildNFLMatchups(byDivision, rng)
        : this.buildRoundRobinMatchups(teams, rng);

    const byeWeeks = this.assignByeWeeks(teams, rng);
    return this.distributeAcrossWeeks(matchups, byeWeeks, rng);
  }

  getTotalWeeks(): number {
    return this.totalWeeks;
  }

  getGamesPerTeam(): number {
    return this.gamesPerTeam;
  }

  getScheduleName(): string {
    return 'NFL Schedule (17 games, 18 weeks, bye weeks)';
  }

  private buildNFLMatchups(divisions: Record<string, Team[]>, rng: Rng): Array<{ home: Team; away: Team }> {
    const matchups: Array<{ home: Team; away: Team }> = [];
    const gamesPerTeam: Record<string, number> = {};
    Object.values(divisions)
      .flat()
      .forEach((t) => (gamesPerTeam[t.id] = 0));

    // Divisional home/away
    Object.values(divisions).forEach((teams) => {
      for (let i = 0; i < teams.length; i++) {
        for (let j = i + 1; j < teams.length; j++) {
          matchups.push({ home: teams[i], away: teams[j] });
          matchups.push({ home: teams[j], away: teams[i] });
          gamesPerTeam[teams[i].id] += 2;
          gamesPerTeam[teams[j].id] += 2;
        }
      }
    });

    // Simple conference cross-division pairings
    const afcDivisions = Object.keys(divisions).filter((k) => k.startsWith('AFC'));
    const nfcDivisions = Object.keys(divisions).filter((k) => k.startsWith('NFC'));
    const pairings = (list: string[]) => {
      const pairs: Array<[string, string]> = [];
      for (let i = 0; i < list.length; i += 2) {
        if (list[i + 1]) pairs.push([list[i], list[i + 1]]);
      }
      return pairs;
    };

    const addDivisionGames = (pairs: Array<[string, string]>) => {
      pairs.forEach(([a, b]) => {
        const divA = divisions[a];
        const divB = divisions[b];
        for (const teamA of divA) {
          for (const teamB of divB) {
            const homeFirst = rng() < 0.5;
            matchups.push({ home: homeFirst ? teamA : teamB, away: homeFirst ? teamB : teamA });
            gamesPerTeam[teamA.id] += 1;
            gamesPerTeam[teamB.id] += 1;
          }
        }
      });
    };

    addDivisionGames(pairings(afcDivisions));
    addDivisionGames(pairings(nfcDivisions));

    // Inter-conference pairings (rotate lists)
    for (let i = 0; i < afcDivisions.length; i++) {
      const afcDiv = divisions[afcDivisions[i]];
      const nfcDiv = divisions[nfcDivisions[i % nfcDivisions.length]];
      for (const afcTeam of afcDiv) {
        for (const nfcTeam of nfcDiv) {
          const homeFirst = rng() < 0.5;
          matchups.push({ home: homeFirst ? afcTeam : nfcTeam, away: homeFirst ? nfcTeam : afcTeam });
          gamesPerTeam[afcTeam.id] += 1;
          gamesPerTeam[nfcTeam.id] += 1;
        }
      }
    }

    // Fill to 17 games with intra-conference opponents
    const allTeams = Object.values(divisions).flat();
    const maxAttempts = 5000;
    let attempts = 0;
    while (attempts < maxAttempts) {
      const team = allTeams[Math.floor(rng() * allTeams.length)];
      if (gamesPerTeam[team.id] >= this.gamesPerTeam) {
        attempts++;
        continue;
      }
      const conferenceMates = allTeams.filter((t) => t.conference === team.conference && t.id !== team.id);
      const opponent = conferenceMates[Math.floor(rng() * conferenceMates.length)];
      if (gamesPerTeam[opponent.id] >= this.gamesPerTeam) {
        attempts++;
        continue;
      }

      matchups.push({ home: rng() < 0.5 ? team : opponent, away: rng() < 0.5 ? opponent : team });
      gamesPerTeam[team.id] += 1;
      gamesPerTeam[opponent.id] += 1;
      attempts++;
      if (Object.values(gamesPerTeam).every((g) => g >= this.gamesPerTeam)) break;
    }

    return matchups;
  }

  private buildRoundRobinMatchups(teams: Team[], rng: Rng): Array<{ home: Team; away: Team }> {
    const matchups: Array<{ home: Team; away: Team }> = [];
    for (let i = 0; i < teams.length; i++) {
      for (let j = i + 1; j < teams.length; j++) {
        if (rng() < 0.5) matchups.push({ home: teams[i], away: teams[j] });
        else matchups.push({ home: teams[j], away: teams[i] });
      }
    }
    return matchups;
  }

  private distributeAcrossWeeks(
    matchups: Array<{ home: Team; away: Team }>,
    byeWeeks: Record<string, number>,
    rng: Rng,
  ): Record<number, Array<{ home: Team; away: Team }>> {
    const weeks: Record<number, Array<{ home: Team; away: Team }>> = {};
    for (let i = 1; i <= this.totalWeeks; i++) weeks[i] = [];

    const remaining = [...matchups];
    let safety = 0;

    while (remaining.length && safety < matchups.length * 3) {
      for (let week = 1; week <= this.totalWeeks; week++) {
        const weeklyTeams = new Set<string>();
        const weekByeTeams = Object.keys(byeWeeks).filter((id) => byeWeeks[id] === week);

        for (const bye of weekByeTeams) {
          weeklyTeams.add(bye);
        }

        for (let i = remaining.length - 1; i >= 0; i--) {
          const game = remaining[i];
          if (weeklyTeams.has(game.home.id) || weeklyTeams.has(game.away.id)) continue;
          if (weeks[week].some((g) => g.home.id === game.home.id || g.away.id === game.home.id || g.home.id === game.away.id || g.away.id === game.away.id)) {
            continue;
          }

          weeks[week].push(game);
          weeklyTeams.add(game.home.id);
          weeklyTeams.add(game.away.id);
          remaining.splice(i, 1);
        }
      }
      safety++;
    }

    // If any games remain, stuff them into later weeks
    if (remaining.length) {
      for (const game of remaining) {
        for (let week = 1; week <= this.totalWeeks; week++) {
          const conflict = weeks[week].some(
            (g) => g.home.id === game.home.id || g.away.id === game.home.id || g.home.id === game.away.id || g.away.id === game.away.id,
          );
          if (!conflict) {
            weeks[week].push(game);
            break;
          }
        }
      }
    }

    // Shuffle weekly games for variety
    for (let week = 1; week <= this.totalWeeks; week++) {
      weeks[week] = this.shuffle(weeks[week], rng);
    }

    return weeks;
  }

  private assignByeWeeks(teams: Team[], rng: Rng): Record<string, number> {
    const byeWeeks: Record<string, number> = {};
    const byeSlots = this.shuffle(
      Array.from({ length: teams.length }, (_, idx) => 5 + (idx % 10)), // spread byes across weeks 5-14
      rng,
    );

    teams.forEach((team, idx) => {
      byeWeeks[team.id] = byeSlots[idx] || 9;
    });

    return byeWeeks;
  }

  private organizeByDivision(teams: Team[]): Record<string, Team[]> {
    const divisions: Record<string, Team[]> = {};
    for (const team of teams) {
      const key = `${team.conference} ${team.division}`;
      if (!divisions[key]) divisions[key] = [];
      divisions[key].push(team);
    }
    return divisions;
  }

  private shuffle<T>(arr: T[], rng: Rng): T[] {
    const copy = [...arr];
    for (let i = copy.length - 1; i > 0; i--) {
      const j = Math.floor(rng() * (i + 1));
      [copy[i], copy[j]] = [copy[j], copy[i]];
    }
    return copy;
  }

  private createSeededRandom(seed: number): Rng {
    let state = seed >>> 0;
    return () => {
      state = (state * 1664525 + 1013904223) % 4294967296;
      return state / 4294967296;
    };
  }
}

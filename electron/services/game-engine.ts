import { Team } from '../database/dao/team-dao';
import {
  Weather,
  WeatherCondition,
  WeatherEffects,
  WindDirection,
  generateRandomWeather,
  getWeatherEffects,
  weatherToString,
} from './weather';

type PlayType = 'run' | 'pass' | 'turnover' | 'special';
type DriveResultType = 'touchdown' | 'field_goal' | 'turnover' | 'turnover_on_downs' | 'punt' | 'missed_fg' | 'end_of_quarter';

export interface PlayLogEntry {
  quarter: number;
  down: number;
  yardsToGo: number;
  startField: number;
  endField: number;
  playType: PlayType;
  yardsGained: number;
  clock: string;
}

export interface DriveLog {
  quarter: number;
  driveNumber: number;
  offense: string;
  defense: string;
  startField: number;
  result: DriveResultType;
  points: number;
  timeElapsed: number;
  plays: number;
  playLog: PlayLogEntry[];
  finalPlayDescription?: string;
}

export interface TeamSimulationStats {
  totalYards: number;
  passingYards: number;
  rushingYards: number;
  turnovers: number;
  plays: number;
  timeOfPossession: number;
  thirdDown: { attempts: number; conversions: number };
  fourthDown: { attempts: number; conversions: number };
}

export interface GameResult {
  gameId?: string;
  homeTeam: Team;
  awayTeam: Team;
  homeScore: number;
  awayScore: number;
  duration: number;
  overtime: boolean;
  winnerId?: string;
  weather: Weather;
  summary: string;
  playByPlay: PlayLogEntry[];
  drives: DriveLog[];
  teamStats: {
    home: TeamSimulationStats;
    away: TeamSimulationStats;
  };
}

interface DriveOutcome {
  result: DriveResultType;
  points: number;
  plays: number;
  finalFieldPosition: number;
  timeElapsed: number;
  down: number;
  yardsForFirstDown: number;
  playLog: PlayLogEntry[];
}

interface QuarterPossessionState {
  team: Team;
  opponent: Team;
  fieldPosition: number;
  down: number;
  yardsForFirstDown: number;
}

interface EngineOptions {
  seed?: number;
  weather?: Weather;
}

export class GameEngine {
  private seed?: number;
  private rng: () => number;
  private weather?: Weather;
  private weatherEffects: WeatherEffects;
  private openingKickoffReceiver?: Team;
  private quarterPossession?: QuarterPossessionState;

  constructor(options: EngineOptions = {}) {
    this.seed = options.seed;
    this.rng = options.seed !== undefined ? this.createSeededRandom(options.seed) : Math.random;
    this.weather = options.weather;
    this.weatherEffects = getWeatherEffects(
      options.weather || {
        condition: WeatherCondition.CLEAR,
        temperature: 72,
        wind_speed: 0,
        wind_direction: WindDirection.NONE,
        precipitation_intensity: 0,
      },
    );
  }

  simulateGame(homeTeam: Team, awayTeam: Team): GameResult {
    if (this.seed !== undefined) {
      this.rng = this.createSeededRandom(this.seed);
    }

    if (!this.weather) {
      const weatherSeed = this.seed !== undefined ? this.seed + 1000 : undefined;
      this.weather = generateRandomWeather(weatherSeed);
    }
    this.weatherEffects = getWeatherEffects(this.weather);

    this.openingKickoffReceiver = homeTeam;
    this.quarterPossession = undefined;

    const aggregates = {
      home: this.createTeamAgg(),
      away: this.createTeamAgg(),
    };

    let homeScore = 0;
    let awayScore = 0;
    const allPlays: PlayLogEntry[] = [];
    const drives: DriveLog[] = [];

    for (let quarter = 1; quarter <= 4; quarter++) {
      const quarterResult = this.simulateQuarter(homeTeam, awayTeam, quarter, aggregates);
      homeScore += quarterResult.homePoints;
      awayScore += quarterResult.awayPoints;
      allPlays.push(...quarterResult.playByPlay);
      drives.push(...quarterResult.drives);
    }

    let overtime = false;
    let duration = 60;

    if (homeScore === awayScore) {
      overtime = true;
      const overtimeResult = this.simulateOvertime(homeTeam, awayTeam, aggregates);
      homeScore += overtimeResult.homePoints;
      awayScore += overtimeResult.awayPoints;
      allPlays.push(...overtimeResult.playByPlay);
      drives.push(...overtimeResult.drives);
      duration += 15;
    }

    const winnerId = homeScore > awayScore ? homeTeam.id : awayScore > homeScore ? awayTeam.id : undefined;

    return {
      homeTeam,
      awayTeam,
      homeScore,
      awayScore,
      duration,
      overtime,
      winnerId,
      weather: this.weather!,
      summary: `${awayTeam.abbreviation} ${awayScore} - ${homeTeam.abbreviation} ${homeScore} (${weatherToString(
        this.weather!,
      )})`,
      playByPlay: allPlays,
      drives,
      teamStats: {
        home: aggregates.home,
        away: aggregates.away,
      },
    };
  }

  private simulateQuarter(
    homeTeam: Team,
    awayTeam: Team,
    quarter: number,
    aggregates: { home: TeamSimulationStats; away: TeamSimulationStats },
  ): {
    homePoints: number;
    awayPoints: number;
    playByPlay: PlayLogEntry[];
    drives: DriveLog[];
  } {
    let homePoints = 0;
    let awayPoints = 0;
    let timeRemaining = 900;

    let possessionTeam: Team;
    let defendingTeam: Team;
    let fieldPosition: number;
    let isHomePossession: boolean;
    let down = 1;
    let yardsForFirstDown = 10;

    if (quarter === 1) {
      possessionTeam = homeTeam;
      defendingTeam = awayTeam;
      fieldPosition = this.simulateKickoff(awayTeam, homeTeam);
      isHomePossession = true;
    } else if (quarter === 3) {
      if (this.openingKickoffReceiver === homeTeam) {
        possessionTeam = awayTeam;
        defendingTeam = homeTeam;
        fieldPosition = this.simulateKickoff(homeTeam, awayTeam);
        isHomePossession = false;
      } else {
        possessionTeam = homeTeam;
        defendingTeam = awayTeam;
        fieldPosition = this.simulateKickoff(awayTeam, homeTeam);
        isHomePossession = true;
      }
    } else {
      if (this.quarterPossession) {
        possessionTeam = this.quarterPossession.team;
        defendingTeam = this.quarterPossession.opponent;
        fieldPosition = this.quarterPossession.fieldPosition;
        down = this.quarterPossession.down;
        yardsForFirstDown = this.quarterPossession.yardsForFirstDown;
        isHomePossession = possessionTeam.id === homeTeam.id;
      } else if (quarter === 4) {
        possessionTeam = awayTeam;
        defendingTeam = homeTeam;
        fieldPosition = this.simulateKickoff(homeTeam, awayTeam);
        isHomePossession = false;
      } else {
        if (this.rng() < 0.5) {
          possessionTeam = homeTeam;
          defendingTeam = awayTeam;
          isHomePossession = true;
        } else {
          possessionTeam = awayTeam;
          defendingTeam = homeTeam;
          isHomePossession = false;
        }
        fieldPosition = 20 + Math.floor(this.rng() * 60);
      }
    }

    const playByPlay: PlayLogEntry[] = [];
    const drives: DriveLog[] = [];
    let drivesInQuarter = 0;

    while (timeRemaining > 0) {
      drivesInQuarter += 1;
      const driveOutcome = this.simulateDriveWithTime(
        possessionTeam,
        defendingTeam,
        isHomePossession,
        fieldPosition,
        timeRemaining,
        quarter,
        aggregates,
      );

      timeRemaining -= driveOutcome.timeElapsed;

      if (isHomePossession) {
        homePoints += driveOutcome.points;
      } else {
        awayPoints += driveOutcome.points;
      }

      playByPlay.push(...driveOutcome.playLog);
      
      // Generate final play description for scoring/turnover drives
      let finalPlayDescription: string | undefined;
      if (driveOutcome.playLog.length > 0) {
        const finalPlay = driveOutcome.playLog[driveOutcome.playLog.length - 1];
        if (driveOutcome.result === 'touchdown') {
          const playTypeStr = finalPlay.playType === 'run' ? 'rush' : finalPlay.playType === 'pass' ? 'pass' : 'play';
          finalPlayDescription = `${finalPlay.yardsGained} yd ${playTypeStr}`;
        } else if (driveOutcome.result === 'field_goal') {
          const fgDistance = (100 - driveOutcome.finalFieldPosition) + 17;
          finalPlayDescription = `${fgDistance} yd FG`;
        } else if (driveOutcome.result === 'missed_fg') {
          const fgDistance = (100 - driveOutcome.finalFieldPosition) + 17;
          finalPlayDescription = `Missed ${fgDistance} yd FG`;
        } else if (driveOutcome.result === 'turnover') {
          if (finalPlay.playType === 'turnover') {
            finalPlayDescription = 'Turnover';
          } else {
            finalPlayDescription = `Turnover on ${finalPlay.playType}`;
          }
        } else if (driveOutcome.result === 'turnover_on_downs') {
          finalPlayDescription = `Failed on 4th & ${finalPlay.yardsToGo}`;
        }
      } else if (driveOutcome.result === 'field_goal' || driveOutcome.result === 'missed_fg') {
        // FG/missed FG with no plays (decided before play)
        const fgDistance = (100 - driveOutcome.finalFieldPosition) + 17;
        finalPlayDescription = driveOutcome.result === 'field_goal' 
          ? `${fgDistance} yd FG` 
          : `Missed ${fgDistance} yd FG`;
      }
      
      drives.push({
        quarter,
        driveNumber: drivesInQuarter,
        offense: possessionTeam.abbreviation,
        defense: defendingTeam.abbreviation,
        startField: fieldPosition,
        result: driveOutcome.result,
        points: driveOutcome.points,
        timeElapsed: driveOutcome.timeElapsed,
        plays: driveOutcome.plays,
        playLog: driveOutcome.playLog,
        finalPlayDescription,
      });

      if (timeRemaining <= 0) {
        if (quarter === 1 || quarter === 3) {
          if (driveOutcome.result === 'end_of_quarter') {
            this.quarterPossession = {
              team: possessionTeam,
              opponent: defendingTeam,
              fieldPosition: driveOutcome.finalFieldPosition,
              down: driveOutcome.down,
              yardsForFirstDown: driveOutcome.yardsForFirstDown,
            };
          } else {
            this.quarterPossession = undefined;
          }
        } else {
          this.quarterPossession = undefined;
        }
        break;
      }

      const next = this.handleDriveTransition(driveOutcome, possessionTeam, defendingTeam);
      possessionTeam = next.team;
      defendingTeam = next.opponent;
      isHomePossession = possessionTeam.id === homeTeam.id;
      fieldPosition = next.fieldPosition;
      down = 1;
      yardsForFirstDown = 10;
    }

    return { homePoints, awayPoints, playByPlay, drives };
  }

  private simulatePlay(
    offense: Team,
    defense: Team,
    isHome: boolean,
    down: number,
    yardsForFirst: number,
    yardsToGoal: number,
  ): { playType: PlayType; yardsGained: number } {
    const offRating = offense.stats.offensive_rating;
    const defRating = defense.stats.defensive_rating;
    const homeBonus = isHome ? offense.stats.home_field_advantage || 0 : 0;
    const situationModifier = this.getSituationModifier(down, yardsForFirst, yardsToGoal);

    const successRating = (offRating + homeBonus - defRating + situationModifier) / 90;
    const playType = this.choosePlayType(down, yardsForFirst, yardsToGoal);

    let yardsGained = 0;
    if (playType === 'run') {
      yardsGained = this.simulateRunPlay(successRating, yardsToGoal);
    } else if (playType === 'pass') {
      yardsGained = this.simulatePassPlay(successRating, yardsForFirst, yardsToGoal);
    } else {
      yardsGained = this.simulateSpecialPlay(successRating);
    }

    const turnoverChance = this.calculateTurnoverChance(playType, successRating, down);
    if (this.rng() < turnoverChance) {
      return { playType: 'turnover', yardsGained: 0 };
    }

    return { playType, yardsGained: Math.max(yardsGained, -(100 - yardsToGoal)) };
  }

  private getSituationModifier(down: number, yardsForFirst: number, yardsToGoal: number): number {
    let modifier = 0;
    if (down === 1) modifier += 5;
    else if (down === 2) modifier += 2;
    else if (down === 3) modifier -= 3;
    else modifier -= 8;

    if (yardsForFirst <= 3) modifier += 3;
    else if (yardsForFirst >= 10) modifier -= 5;

    if (yardsToGoal <= 20) modifier += 3;
    return modifier;
  }

  private choosePlayType(down: number, yardsForFirst: number, yardsToGoal: number): PlayType {
    let runProb = 0.45;
    let passProb = 0.55;

    if (yardsForFirst <= 3) {
      runProb = 0.65;
      passProb = 0.35;
    } else if (yardsForFirst >= 10) {
      runProb = 0.25;
      passProb = 0.75;
    }

    if (down >= 3 && yardsForFirst > 5) {
      runProb = 0.15;
      passProb = 0.85;
    }

    if (yardsToGoal <= 5) {
      runProb = 0.7;
      passProb = 0.3;
    }

    const roll = this.rng();
    if (roll < runProb) return 'run';
    if (roll < runProb + passProb) return 'pass';
    return 'special';
  }

  private simulateRunPlay(successRating: number, yardsToGoal: number): number {
    const baseYards = 4.2;
    let adjustedAvg = baseYards + successRating * 2.5;

    adjustedAvg *= this.weatherEffects.rushing_yards_modifier;

    let yards = this.normal(adjustedAvg, 2.5);
    yards = Math.max(-3, Math.min(yards, 25));
    if (yardsToGoal <= 5) {
      yards = Math.max(0, Math.min(yards, yardsToGoal + 2));
    }

    return Math.round(yards);
  }

  private simulatePassPlay(successRating: number, yardsForFirst: number, yardsToGoal: number): number {
    let completionProb = 0.7 + successRating * 0.2;
    completionProb = Math.max(0.45, Math.min(0.9, completionProb));

    completionProb *= this.weatherEffects.passing_accuracy_modifier;
    completionProb *= this.weatherEffects.visibility_modifier;
    completionProb = Math.max(0.15, Math.min(0.9, completionProb));

    if (this.rng() < completionProb) {
      let baseYards = 8.5;
      if (yardsForFirst > 10) {
        baseYards = yardsForFirst * 0.9;
      }

      let adjustedAvg = baseYards + successRating * 4.0;
      adjustedAvg *= this.weatherEffects.passing_distance_modifier;

      let yards = this.normal(adjustedAvg, 4);
      yards = Math.max(0, Math.min(yards, 40));
      if (yardsToGoal <= 10) {
        yards = Math.max(0, Math.min(yards, yardsToGoal + 2));
      }
      return Math.round(yards);
    }

    return 0;
  }

  private simulateSpecialPlay(successRating: number): number {
    if (this.rng() < 0.3 + successRating * 0.2) {
      return Math.floor(8 + this.rng() * 17);
    }
    return Math.floor(-5 + this.rng() * 7);
  }

  private calculateTurnoverChance(playType: PlayType, successRating: number, down: number): number {
    let baseTurnover = 0.015;
    if (playType === 'pass') baseTurnover = 0.018;
    else if (playType === 'run') baseTurnover = 0.012;

    let turnoverChance = baseTurnover - successRating * 0.015;
    if (playType === 'run') {
      turnoverChance *= this.weatherEffects.fumble_chance_modifier;
    } else {
      const visibilityEffect = 2 - this.weatherEffects.visibility_modifier;
      const fieldEffect = 2 - this.weatherEffects.field_condition_modifier;
      turnoverChance *= (visibilityEffect + fieldEffect) / 2;
    }

    if (down >= 3) {
      turnoverChance *= 1.5;
    }

    return Math.max(0.005, Math.min(0.12, turnoverChance));
  }

  private attemptFieldGoal(offense: Team, yardsToGoal: number, isHome: boolean): boolean {
    const fgDistance = yardsToGoal + 17;
    let baseSuccess = 0.98;
    if (fgDistance <= 30) baseSuccess = 0.98;
    else if (fgDistance <= 40) baseSuccess = 0.9;
    else if (fgDistance <= 50) baseSuccess = 0.78;
    else baseSuccess = 0.58;

    const stRating = (offense.stats.special_teams_rating || 75) / 100;
    const ratingModifier = (stRating * 100 - 75) / 100;
    const homeBonus = isHome ? 0.05 : 0;

    let successProb = baseSuccess + ratingModifier + homeBonus;
    successProb *= this.weatherEffects.kicking_accuracy_modifier;
    if (fgDistance > 40) {
      successProb *= this.weatherEffects.kicking_distance_modifier;
    }

    successProb = Math.max(0.15, Math.min(0.98, successProb));
    return this.rng() < successProb;
  }

  private decideFourthDown(
    offense: Team,
    fieldPosition: number,
    yardsToGo: number,
    isHome: boolean,
    quarter: number,
    timeRemaining: number
  ): 'punt' | 'field_goal' | 'go_for_it' {
    const yardsToGoal = 100 - fieldPosition;
    const fgDistance = yardsToGoal + 17;
    
    // Short yardage situations (1-2 yards) - more likely to go for it
    if (yardsToGo <= 2) {
      // In opponent territory or desperate situations
      if (fieldPosition >= 50 || quarter >= 4) {
        return 'go_for_it';
      }
      // Otherwise random chance to go for it
      if (this.rng() < 0.3) {
        return 'go_for_it';
      }
    }
    
    // Field goal range (roughly < 53 yards, field position >= 47)
    if (fieldPosition >= 47 && fgDistance <= 53) {
      // Late in game when points matter, more likely to kick
      if (quarter === 4 && timeRemaining < 300) {
        return 'field_goal';
      }
      // Otherwise kick if it's a reasonable distance
      if (fgDistance <= 45) {
        return 'field_goal';
      }
      // Longer FGs - sometimes go for it instead
      if (yardsToGo <= 5 && this.rng() < 0.4) {
        return 'go_for_it';
      }
      return 'field_goal';
    }
    
    // Desperate situations - go for it more often
    if (quarter === 4 && timeRemaining < 120) {
      // Near midfield or better
      if (fieldPosition >= 45) {
        return 'go_for_it';
      }
    }
    
    // Deep in own territory - always punt
    if (fieldPosition < 35) {
      return 'punt';
    }
    
    // Midfield area (35-47) - mostly punt, sometimes go for it
    if (yardsToGo <= 3 && this.rng() < 0.2) {
      return 'go_for_it';
    }
    
    return 'punt';
  }

  private simulateKickoff(kickingTeam: Team, receivingTeam: Team): number {
    const baseReturn = 25;
    const kickingStrength = (kickingTeam.stats.special_teams_rating || 70) / 100;
    const returnStrength = (receivingTeam.stats.special_teams_rating || 70) / 100;

    const returnVariance = this.normal(0, 8);
    let returnDistance = baseReturn + returnVariance + (returnStrength - kickingStrength) * 5;
    returnDistance = Math.max(10, Math.min(50, returnDistance));
    return Math.round(returnDistance);
  }

  private handleDriveTransition(drive: DriveOutcome, offense: Team, defense: Team): {
    team: Team;
    opponent: Team;
    fieldPosition: number;
  } {
    let nextTeam = defense;
    let nextOpponent = offense;
    let fieldPosition = 20;

    if (drive.result === 'touchdown' || drive.result === 'field_goal') {
      fieldPosition = this.simulateKickoff(offense, defense);
    } else if (drive.result === 'turnover') {
      fieldPosition = 100 - drive.finalFieldPosition;
    } else if (drive.result === 'turnover_on_downs') {
      // Failed 4th down conversion - other team gets ball at spot
      fieldPosition = 100 - drive.finalFieldPosition;
    } else if (drive.result === 'punt') {
      fieldPosition = this.simulatePunt(offense, defense, drive.finalFieldPosition);
    } else if (drive.result === 'missed_fg') {
      fieldPosition = 100 - drive.finalFieldPosition;
    }

    return { team: nextTeam, opponent: nextOpponent, fieldPosition };
  }

  private simulatePunt(puntingTeam: Team, receivingTeam: Team, puntFrom: number): number {
    const basePunt = 42;
    const puntVariance = this.normal(0, 8);
    const puntSkill = (puntingTeam.stats.special_teams_rating || 70) / 100;
    const returnSkill = (receivingTeam.stats.special_teams_rating || 70) / 100;

    let puntDistance = basePunt + puntVariance + puntSkill * 5;
    puntDistance = Math.max(25, Math.min(60, puntDistance));

    const puntLandsAt = puntFrom + puntDistance;
    if (puntLandsAt >= 100) {
      return 20;
    }

    let returnDistance = this.normal(8, 4) + returnSkill * 3;
    returnDistance = Math.max(0, Math.min(20, returnDistance));
    let receivingPosition = 100 - puntLandsAt + returnDistance;
    receivingPosition = Math.max(1, Math.min(99, receivingPosition));
    return Math.round(receivingPosition);
  }

  private simulateDriveWithTime(
    offense: Team,
    defense: Team,
    isHome: boolean,
    fieldPosition: number,
    timeRemaining: number,
    quarter: number,
    aggregates: { home: TeamSimulationStats; away: TeamSimulationStats },
  ): DriveOutcome {
    let yardsToGo = 100 - fieldPosition;
    let down = 1;
    let yardsForFirstDown = 10;
    let playsInDrive = 0;
    const maxPlays = 20;
    let currentFieldPosition = fieldPosition;
    let driveTimeElapsed = 0;
    let result: DriveResultType | undefined;
    let points = 0;
    const playLog: PlayLogEntry[] = [];

    const agg = isHome ? aggregates.home : aggregates.away;
    let clock = timeRemaining;

    while (playsInDrive < maxPlays && driveTimeElapsed < timeRemaining) {
      // BEFORE the play, check if this is 4th down and make punt/FG/go-for-it decision
      if (down === 4) {
        const fourthDownDecision = this.decideFourthDown(
          offense,
          currentFieldPosition,
          yardsForFirstDown,
          isHome,
          quarter,
          timeRemaining
        );

        if (fourthDownDecision === 'punt') {
          // Execute punt
          result = 'punt';
          points = 0;
          break;
        } else if (fourthDownDecision === 'field_goal') {
          // Attempt field goal
          const fgSuccess = this.attemptFieldGoal(offense, 100 - currentFieldPosition, isHome);
          driveTimeElapsed += 5; // FG attempt takes ~5 seconds
          clock = Math.max(0, clock - 5);
          
          if (fgSuccess) {
            result = 'field_goal';
            points = 3;
          } else {
            result = 'missed_fg';
            points = 0;
          }
          break;
        }
        // Otherwise, go for it on 4th down (continue with normal play)
        agg.fourthDown.attempts += 1;
      }

      playsInDrive += 1;
      const playResult = this.simulatePlayWithTime(offense, defense, isHome, down, yardsForFirstDown, currentFieldPosition);
      driveTimeElapsed += playResult.timeElapsed;
      clock = Math.max(0, clock - playResult.timeElapsed);

      const endField = currentFieldPosition + playResult.yardsGained;
      playLog.push({
        quarter,
        down,
        yardsToGo: yardsForFirstDown,
        startField: currentFieldPosition,
        endField,
        playType: playResult.playType,
        yardsGained: playResult.yardsGained,
        clock: this.formatClock(clock),
      });

      const startingDown = down;
      const gained = playResult.yardsGained;
      currentFieldPosition = endField;
      yardsToGo = 100 - currentFieldPosition;
      yardsForFirstDown -= gained;

      agg.plays += 1;
      agg.totalYards += Math.max(0, gained);
      agg.timeOfPossession += playResult.timeElapsed;
      if (playResult.playType === 'run') {
        agg.rushingYards += Math.max(0, gained);
      } else if (playResult.playType === 'pass') {
        agg.passingYards += Math.max(0, gained);
      } else if (playResult.playType === 'turnover') {
        agg.turnovers += 1;
      }

      if (startingDown === 3) agg.thirdDown.attempts += 1;

      if (currentFieldPosition >= 100) {
        if (playResult.playType === 'turnover') {
          result = 'turnover';
          points = 0;
        } else {
          result = 'touchdown';
          points = 7;
          currentFieldPosition = 100;
        }
        if (startingDown === 3 && yardsForFirstDown <= 0) agg.thirdDown.conversions += 1;
        if (startingDown === 4 && yardsForFirstDown <= 0) agg.fourthDown.conversions += 1;
        break;
      }

      if (playResult.playType === 'turnover') {
        result = 'turnover';
        points = 0;
        break;
      }

      if (yardsForFirstDown <= 0) {
        if (startingDown === 3) agg.thirdDown.conversions += 1;
        if (startingDown === 4) agg.fourthDown.conversions += 1;
        down = 1;
        yardsForFirstDown = 10;
        continue;
      }

      down += 1;
      
      // If we failed on 4th down, it's a turnover on downs
      if (down > 4) {
        result = 'turnover_on_downs';
        points = 0;
        break;
      }

      if (driveTimeElapsed >= timeRemaining) {
        result = 'end_of_quarter';
        points = 0;
        break;
      }
    }

    if (!result) {
      if (driveTimeElapsed >= timeRemaining) {
        result = down > 4 ? 'punt' : 'end_of_quarter';
      } else if (playsInDrive >= maxPlays) {
        result = 'punt';
      } else {
        result = 'punt';
      }
    }

    return {
      result,
      points,
      plays: playsInDrive,
      finalFieldPosition: currentFieldPosition,
      timeElapsed: driveTimeElapsed,
      down,
      yardsForFirstDown,
      playLog,
    };
  }

  private simulatePlayWithTime(
    offense: Team,
    defense: Team,
    isHome: boolean,
    down: number,
    yardsForFirst: number,
    yardsToGoal: number,
  ): { playType: PlayType; yardsGained: number; timeElapsed: number } {
    const play = this.simulatePlay(offense, defense, isHome, down, yardsForFirst, yardsToGoal);
    const timeElapsed = this.calculatePlayTime(play.playType, play.yardsGained, down);
    return { playType: play.playType, yardsGained: play.yardsGained, timeElapsed };
  }

  private calculatePlayTime(playType: PlayType, yardsGained: number, down: number): number {
    let playTime = 3;
    if (playType === 'run') {
      playTime = yardsGained > 0 ? (this.rng() < 0.2 ? this.randomInt(2, 4) : this.randomInt(3, 6)) : this.randomInt(2, 4);
    } else if (playType === 'pass') {
      if (yardsGained > 0) {
        playTime = this.rng() < 0.3 ? this.randomInt(3, 5) : this.randomInt(4, 7);
      } else {
        playTime = this.randomInt(1, 3);
      }
    } else if (playType === 'turnover') {
      playTime = this.randomInt(3, 6);
    } else {
      playTime = this.randomInt(3, 5);
    }

    const betweenPlays = down >= 3 ? this.randomInt(10, 20) : this.randomInt(15, 25);
    let total = playTime + betweenPlays;
    if (this.rng() < 0.03) {
      total += this.randomInt(15, 45);
    }
    return total;
  }

  private simulateOvertime(
    homeTeam: Team,
    awayTeam: Team,
    aggregates: { home: TeamSimulationStats; away: TeamSimulationStats },
  ): {
    homePoints: number;
    awayPoints: number;
    playByPlay: PlayLogEntry[];
    drives: DriveLog[];
  } {
    const playByPlay: PlayLogEntry[] = [];
    const drives: DriveLog[] = [];
    const firstTeam = this.rng() < 0.5 ? homeTeam : awayTeam;
    const secondTeam = firstTeam.id === homeTeam.id ? awayTeam : homeTeam;

    const firstIsHome = firstTeam.id === homeTeam.id;
    const firstDrive = this.simulateDriveWithTime(firstTeam, secondTeam, firstIsHome, 25, 900, 5, aggregates);
    playByPlay.push(...firstDrive.playLog);
    drives.push({
      quarter: 5,
      driveNumber: 1,
      offense: firstTeam.abbreviation,
      defense: secondTeam.abbreviation,
      startField: 25,
      result: firstDrive.result,
      points: firstDrive.points,
      timeElapsed: firstDrive.timeElapsed,
      plays: firstDrive.plays,
      playLog: firstDrive.playLog,
    });

    if (firstDrive.points >= 7) {
      return {
        homePoints: firstIsHome ? firstDrive.points : 0,
        awayPoints: firstIsHome ? 0 : firstDrive.points,
        playByPlay,
        drives,
      };
    }

    const secondIsHome = secondTeam.id === homeTeam.id;
    const secondDrive = this.simulateDriveWithTime(secondTeam, firstTeam, secondIsHome, 25, 900, 5, aggregates);
    playByPlay.push(...secondDrive.playLog);
    drives.push({
      quarter: 5,
      driveNumber: 2,
      offense: secondTeam.abbreviation,
      defense: firstTeam.abbreviation,
      startField: 25,
      result: secondDrive.result,
      points: secondDrive.points,
      timeElapsed: secondDrive.timeElapsed,
      plays: secondDrive.plays,
      playLog: secondDrive.playLog,
    });

    if (firstTeam.id === homeTeam.id) {
      return {
        homePoints: firstDrive.points,
        awayPoints: secondDrive.points,
        playByPlay,
        drives,
      };
    }

    return {
      homePoints: secondDrive.points,
      awayPoints: firstDrive.points,
      playByPlay,
      drives,
    };
  }

  private createTeamAgg(): TeamSimulationStats {
    return {
      totalYards: 0,
      passingYards: 0,
      rushingYards: 0,
      turnovers: 0,
      plays: 0,
      timeOfPossession: 0,
      thirdDown: { attempts: 0, conversions: 0 },
      fourthDown: { attempts: 0, conversions: 0 },
    };
  }

  private formatClock(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = Math.max(0, Math.floor(seconds % 60));
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  }

  private createSeededRandom(seed: number): () => number {
    let state = seed >>> 0;
    return () => {
      state = (state * 1664525 + 1013904223) % 4294967296;
      return state / 4294967296;
    };
  }

  private normal(mean: number, std: number): number {
    let u = 0;
    let v = 0;
    while (u === 0) u = this.rng();
    while (v === 0) v = this.rng();
    const magnitude = Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
    return mean + std * magnitude;
  }

  private randomInt(min: number, max: number): number {
    return Math.floor(this.rng() * (max - min + 1)) + min;
  }
}

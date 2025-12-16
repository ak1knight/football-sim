import { BaseService } from './base-service';
import { GameEngine, GameResult } from './game-engine';
import { Weather } from './weather';
import { NFLScheduleGenerator } from './schedule-generator';
import { SeasonService } from './season-service';

export class SimulationService extends BaseService {
  private createEngine(options: SimulationOptions = {}): GameEngine {
    const { seed, weather } = options;
    return new GameEngine({ seed, weather });
  }

  async simulateGame(gameId: string, options: SimulationOptions = {}): Promise<any> {
    try {
      this.validateId(gameId, 'game');
      
      const game = this.daoManager.games.getById(gameId);
      if (!game) {
        throw new Error('Game not found');
      }

      const homeTeam = this.daoManager.teams.getById(game.home_team_id);
      const awayTeam = this.daoManager.teams.getById(game.away_team_id);
      
      if (!homeTeam || !awayTeam) {
        throw new Error('Team data not found');
      }

      const engine = this.createEngine(options);
      const result = engine.simulateGame(homeTeam, awayTeam);
      const resultWithId: GameResult = { ...result, gameId };
      
      this.daoManager.games.completeGame(gameId, result.homeScore, result.awayScore, this.buildGameData(resultWithId));

      // If this is a playoff game, update the playoff bracket
      const season = this.daoManager.seasons.getById(game.season_id);
      if (season && season.status === 'playoffs' && game.week >= 19) {
        await this.updatePlayoffBracketAfterGame(game.season_id, gameId, result);
      }

      // Check if all games for this week are now complete
      const allWeekGames = this.daoManager.games.getWeekGames(game.season_id, game.week);
      const allGamesComplete = allWeekGames.every(g => 
        g.status === 'completed' || g.status === 'simulated'
      );

      // If all games are complete, advance to the next week
      if (allGamesComplete) {
        if (season && season.current_week === game.week) {
          this.daoManager.seasons.setCurrentWeek(game.season_id, game.week + 1);
          console.log(`✅ Week ${game.week} complete - Advanced to week ${game.week + 1}`);
          
          // Check if regular season is complete and start playoffs if needed
          await this.startPlayoffsIfNeeded(game.season_id, game.week + 1);
          
          // Check if playoff round is complete and advance to next round
          await this.advancePlayoffRoundIfNeeded(game.season_id, game.week + 1);
        }
      }

      // Get updated season status
      const seasonStatus = await this.getSeasonStatusForGame(game.season_id);

      return {
        game_result: this.formatGameResult(resultWithId),
        season_status: seasonStatus,
        message: `Game simulated: ${result.awayTeam.city} ${result.awayScore} - ${result.homeTeam.city} ${result.homeScore}`,
        simulation_details: this.formatGameResult(resultWithId)
      };
    } catch (error) {
      this.handleError(error, 'Simulate game');
    }
  }

  async simulateExhibitionGame(homeTeamId: string, awayTeamId: string, options: SimulationOptions = {}): Promise<any> {
    try {
      this.validateId(homeTeamId, 'home team');
      this.validateId(awayTeamId, 'away team');
      
      const homeTeam = this.daoManager.teams.getById(homeTeamId);
      const awayTeam = this.daoManager.teams.getById(awayTeamId);
      
      if (!homeTeam || !awayTeam) {
        throw new Error('Team not found');
      }

      const engine = this.createEngine(options);
      const result = engine.simulateGame(homeTeam, awayTeam);
      return this.formatGameResult(result);
    } catch (error) {
      this.handleError(error, 'Simulate exhibition game');
    }
  }

  async simulateWeek(seasonId: string, week: number, options: SimulationOptions = {}): Promise<any> {
    try {
      this.validateId(seasonId, 'season');
      this.validateRequired(week, 'week');
      
      const games = this.daoManager.games.getWeekGames(seasonId, week)
        .filter(game => game.status === 'scheduled');
      
      const simulatedGames = [];
      
      for (const game of games) {
        const result = await this.simulateGame(game.id, options);
        simulatedGames.push(result.game_result);
      }

      // Check if all games for this week are now complete
      const allWeekGames = this.daoManager.games.getWeekGames(seasonId, week);
      const allGamesComplete = allWeekGames.every(game => 
        game.status === 'completed' || game.status === 'simulated'
      );

      // If all games are complete, advance to the next week
      if (allGamesComplete && simulatedGames.length > 0) {
        const season = this.daoManager.seasons.getById(seasonId);
        if (season && season.current_week === week) {
          this.daoManager.seasons.setCurrentWeek(seasonId, week + 1);
          console.log(`✅ Week ${week} complete - Advanced to week ${week + 1}`);
          
          // Check if regular season is complete and start playoffs if needed
          await this.startPlayoffsIfNeeded(seasonId, week + 1);
          
          // Check if playoff round is complete and advance to next round
          await this.advancePlayoffRoundIfNeeded(seasonId, week + 1);
        }
      }

      // Get updated season status after simulating all week games
      const seasonStatus = await this.getSeasonStatusForGame(seasonId);
      
      return {
        season_status: seasonStatus,
        simulated_games: simulatedGames,
        message: `Week ${week} simulated: ${simulatedGames.length} games completed`,
        week,
        games_simulated: simulatedGames.length
      };
    } catch (error) {
      this.handleError(error, 'Simulate week');
    }
  }

  async simulateToWeek(seasonId: string, targetWeek: number, options: SimulationOptions = {}): Promise<any> {
    try {
      console.log(`Simulating to week ${targetWeek} for season ID: "${seasonId}"`);
      this.validateId(seasonId, 'season');
      this.validateRequired(targetWeek, 'target week');
      
      const season = this.daoManager.seasons.getById(seasonId);
      if (!season) {
        throw new Error('Season not found');
      }
      
      const allSimulatedGames = [];
      
      for (let week = season.current_week; week <= targetWeek; week++) {
        const weekResult = await this.simulateWeek(seasonId, week, options);
        allSimulatedGames.push(...weekResult.simulated_games);
        
        // Update season week
        this.daoManager.seasons.setCurrentWeek(seasonId, week + 1);
      }

      // Get final season status
      const seasonStatus = await this.getSeasonStatusForGame(seasonId);
      
      return {
        season_status: seasonStatus,
        simulated_games: allSimulatedGames,
        message: `Simulated to week ${targetWeek}: ${allSimulatedGames.length} total games`,
        target_week: targetWeek,
        weeks_simulated: targetWeek - season.current_week + 1
      };
    } catch (error) {
      this.handleError(error, 'Simulate to week');
    }
  }

  async simulateSeason(seasonId: string, options: SimulationOptions = {}): Promise<any> {
    try {
      this.validateId(seasonId, 'season');
      
      // Simulate all remaining regular season games (weeks 1-17)
      const generator = new NFLScheduleGenerator();
      const result = await this.simulateToWeek(seasonId, generator.getTotalWeeks(), options);
      
      return {
        ...result,
        message: `Full season simulated: ${result.simulated_games?.length || 0} games completed`
      };
    } catch (error) {
      this.handleError(error, 'Simulate season');
    }
  }

  async simulatePlayoffGame(gameId: string, options: SimulationOptions = {}): Promise<any> {
    try {
      // For now, same as regular game simulation
      return this.simulateGame(gameId, options);
    } catch (error) {
      this.handleError(error, 'Simulate playoff game');
    }
  }

  private buildGameData(result: GameResult) {
    return {
      winner_id: result.winnerId,
      weather: result.weather,
      stats: result.teamStats,
      play_by_play: result.playByPlay,
      drives: result.drives,
      detailed_stats: {
        summary: result.summary,
        overtime: result.overtime,
        duration: result.duration,
      },
    };
  }

  private formatGameResult(result: GameResult) {
    // Count play types from play-by-play
    const playTypeCounts = { run: 0, pass: 0, turnover: 0 };
    for (const play of result.playByPlay) {
      if (play.playType === 'run') playTypeCounts.run++;
      else if (play.playType === 'pass') playTypeCounts.pass++;
      else if (play.playType === 'turnover') playTypeCounts.turnover++;
    }

    return {
      game_id: result.gameId || `${result.homeTeam.id}-${result.awayTeam.id}-${result.duration}`,
      home_team: {
        id: result.homeTeam.id,
        name: `${result.homeTeam.city} ${result.homeTeam.name}`,
        abbreviation: result.homeTeam.abbreviation,
        score: result.homeScore,
      },
      away_team: {
        id: result.awayTeam.id,
        name: `${result.awayTeam.city} ${result.awayTeam.name}`,
        abbreviation: result.awayTeam.abbreviation,
        score: result.awayScore,
      },
      winner: result.winnerId ? (result.winnerId === result.homeTeam.id ? 'home' : 'away') : 'tie',
      weather: result.weather,
      summary: result.summary,
      detailed_stats: {
        home: {
          total_yards: result.teamStats.home.totalYards,
          passing_yards: result.teamStats.home.passingYards,
          rushing_yards: result.teamStats.home.rushingYards,
          turnovers: result.teamStats.home.turnovers,
          plays: result.teamStats.home.plays,
          time_of_possession: result.teamStats.home.timeOfPossession,
        },
        away: {
          total_yards: result.teamStats.away.totalYards,
          passing_yards: result.teamStats.away.passingYards,
          rushing_yards: result.teamStats.away.rushingYards,
          turnovers: result.teamStats.away.turnovers,
          plays: result.teamStats.away.plays,
          time_of_possession: result.teamStats.away.timeOfPossession,
        },
        play_type_counts: playTypeCounts,
        total_plays: result.teamStats.home.plays + result.teamStats.away.plays,
        total_drives: result.drives.length,
      },
      play_by_play: result.playByPlay,
      drives: result.drives.map((drive, index) => ({
        drive_number: index + 1, // Ensure sequential drive numbering across the entire game
        quarter: drive.quarter,
        offense: drive.offense,
        defense: drive.defense,
        starting_position: `${drive.startField}`,
        result: drive.result,
        points: drive.points,
        total_plays: drive.plays,
        total_yards: drive.playLog.reduce((sum, play) => sum + play.yardsGained, 0),
        time_elapsed: drive.timeElapsed,
        final_play_description: drive.finalPlayDescription,
        play_log: drive.playLog.map((play) => ({
          quarter: play.quarter,
          down: play.down,
          yards_to_go: play.yardsToGo,
          start_field: play.startField,
          end_field: play.endField,
          play_type: play.playType,
          yards_gained: play.yardsGained,
          clock: play.clock,
        })),
      })),
      overtime: result.overtime,
      duration: result.duration,
    };
  }

  private async getSeasonStatusForGame(seasonId: string): Promise<any> {
    const season = this.daoManager.seasons.getById(seasonId);
    if (!season) {
      throw new Error('Season not found');
    }

    const seasonStats = this.daoManager.seasons.getSeasonStats(seasonId);
    return {
      id: season.id,
      year: season.year,
      name: season.name,
      current_week: season.current_week,
      current_phase: season.status === 'playoffs' ? 'playoffs' : 'regular_season',
      total_games: seasonStats.games?.total || 0,
      completed_games: seasonStats.games?.completed || 0,
      completion_percentage: seasonStats.games?.completion_percentage || 0,
      next_games_count: seasonStats.games?.remaining || 0,
      weeks_remaining: Math.max(0, 18 - season.current_week),
      schedule_type: 'balanced'
    };
  }

  private async startPlayoffsIfNeeded(seasonId: string, currentWeek: number): Promise<void> {
    try {
      // Check if we've completed week 18 (regular season is over)
      if (currentWeek > 18) {
        const season = this.daoManager.seasons.getById(seasonId);
        
        // Only transition to playoffs if we're still in active status
        if (season && season.status === 'active') {
          console.log('🏈 Regular season complete! Starting playoffs...');
          
          // Update season status to playoffs
          this.daoManager.seasons.updateStatus(seasonId, 'playoffs');
          
          // Generate playoff bracket using the season service helper
          const seasonService = new SeasonService(this.daoManager);
          const bracketData = await seasonService.getPlayoffBracket(seasonId);
          
          if (bracketData && bracketData.bracket) {
            // Create playoff games in database
            await this.createPlayoffGamesFromBracket(seasonId, bracketData.bracket);
            console.log('✅ Playoffs initialized successfully!');
          }
        }
      }
    } catch (error) {
      console.error('Error starting playoffs:', error);
    }
  }

  private async createPlayoffGamesFromBracket(seasonId: string, bracket: any): Promise<void> {
    try {
      // Only create Wild Card games initially (week 19)
      // Other rounds will be created dynamically as previous rounds complete
      const wildCardGames = bracket.wild_card_games || [];
      for (const playoffGame of wildCardGames) {
        if (playoffGame.home_team && playoffGame.away_team) {
          this.daoManager.games.create({
            season_id: seasonId,
            week: 19,
            home_team_id: playoffGame.home_team.id,
            away_team_id: playoffGame.away_team.id,
            status: 'scheduled'
          });
        }
      }
      console.log(`✅ Created ${wildCardGames.length} Wild Card games (Week 19)`);
    } catch (error) {
      console.error('Error creating playoff games:', error);
      throw error;
    }
  }

  private async advancePlayoffRoundIfNeeded(seasonId: string, currentWeek: number): Promise<void> {
    try {
      const season = this.daoManager.seasons.getById(seasonId);
      if (!season || season.status !== 'playoffs') {
        return;
      }

      // Check which playoff week just completed
      let justCompletedWeek = currentWeek - 1;
      
      // Week 19 = Wild Card, Week 20 = Divisional, Week 21 = Conference Championships
      if (justCompletedWeek === 19 || justCompletedWeek === 20 || justCompletedWeek === 21) {
        const weekGames = this.daoManager.games.getWeekGames(seasonId, justCompletedWeek);
        const allComplete = weekGames.length > 0 && weekGames.every(g => 
          g.status === 'completed' || g.status === 'simulated'
        );

        if (allComplete) {
          console.log(`🏈 Playoff week ${justCompletedWeek} complete! Generating next round...`);
          
          // Get updated bracket with completed game results
          const seasonService = new SeasonService(this.daoManager);
          const bracketData = await seasonService.getPlayoffBracket(seasonId);
          
          if (!bracketData || !bracketData.bracket) {
            console.log('⚠️ Could not load playoff bracket');
            return;
          }

          const bracket = bracketData.bracket;

          // Create games for the next round based on which week just completed
          if (justCompletedWeek === 19) {
            // Wild Card complete -> Create Divisional games (Week 20)
            await this.createDivisionalGames(seasonId, bracket);
          } else if (justCompletedWeek === 20) {
            // Divisional complete -> Create Conference Championship games (Week 21)
            await this.createConferenceChampionshipGames(seasonId, bracket);
          } else if (justCompletedWeek === 21) {
            // Conference Championships complete -> Create Super Bowl (Week 22)
            await this.createSuperBowlGame(seasonId, bracket);
          }
        }
      }
    } catch (error) {
      console.error('Error advancing playoff round:', error);
    }
  }

  private async createDivisionalGames(seasonId: string, bracket: any): Promise<void> {
    try {
      // Get all completed wild card games to determine winners
      const wildCardGames = this.daoManager.games.getWeekGames(seasonId, 19);
      const winners = wildCardGames
        .filter(g => g.status === 'completed' || g.status === 'simulated')
        .map(g => {
          const winnerId = g.game_data?.winner_id;
          if (!winnerId) return null;
          return this.daoManager.teams.getById(winnerId);
        })
        .filter(t => t !== null && t !== undefined);

      console.log(`🏈 Wild Card winners: ${winners.map(w => w?.abbreviation).join(', ')}`);

      // Separate by conference
      const afcWinners = winners.filter(t => t?.conference === 'AFC');
      const nfcWinners = winners.filter(t => t?.conference === 'NFC');

      // Sort by seed (need to get from bracket)
      const afcWinnersWithSeeds = afcWinners.map(team => {
        const playoffTeam = bracket.afc_teams?.find((t: any) => t.team.id === team?.id);
        return playoffTeam;
      }).filter(Boolean).sort((a: any, b: any) => a.seed - b.seed);

      const nfcWinnersWithSeeds = nfcWinners.map(team => {
        const playoffTeam = bracket.nfc_teams?.find((t: any) => t.team.id === team?.id);
        return playoffTeam;
      }).filter(Boolean).sort((a: any, b: any) => a.seed - b.seed);

      // Create divisional matchups
      let gamesCreated = 0;

      // AFC Divisional games
      if (afcWinnersWithSeeds.length >= 3) {
        const afcOneSeed = bracket.afc_teams?.find((t: any) => t.seed === 1);
        const lowestSeed = afcWinnersWithSeeds[afcWinnersWithSeeds.length - 1];
        const highestWildCard = afcWinnersWithSeeds[0];
        const middleWildCard = afcWinnersWithSeeds[1];

        // 1 seed vs lowest remaining seed
        if (afcOneSeed && lowestSeed) {
          this.daoManager.games.create({
            season_id: seasonId,
            week: 20,
            home_team_id: afcOneSeed.team.id,
            away_team_id: lowestSeed.team.id,
            status: 'scheduled'
          });
          gamesCreated++;
        }

        // Highest wild card vs middle wild card
        if (highestWildCard && middleWildCard) {
          this.daoManager.games.create({
            season_id: seasonId,
            week: 20,
            home_team_id: highestWildCard.team.id,
            away_team_id: middleWildCard.team.id,
            status: 'scheduled'
          });
          gamesCreated++;
        }
      }

      // NFC Divisional games
      if (nfcWinnersWithSeeds.length >= 3) {
        const nfcOneSeed = bracket.nfc_teams?.find((t: any) => t.seed === 1);
        const lowestSeed = nfcWinnersWithSeeds[nfcWinnersWithSeeds.length - 1];
        const highestWildCard = nfcWinnersWithSeeds[0];
        const middleWildCard = nfcWinnersWithSeeds[1];

        // 1 seed vs lowest remaining seed
        if (nfcOneSeed && lowestSeed) {
          this.daoManager.games.create({
            season_id: seasonId,
            week: 20,
            home_team_id: nfcOneSeed.team.id,
            away_team_id: lowestSeed.team.id,
            status: 'scheduled'
          });
          gamesCreated++;
        }

        // Highest wild card vs middle wild card
        if (highestWildCard && middleWildCard) {
          this.daoManager.games.create({
            season_id: seasonId,
            week: 20,
            home_team_id: highestWildCard.team.id,
            away_team_id: middleWildCard.team.id,
            status: 'scheduled'
          });
          gamesCreated++;
        }
      }

      console.log(`✅ Created ${gamesCreated} Divisional games (Week 20)`);
    } catch (error) {
      console.error('Error creating divisional games:', error);
      throw error;
    }
  }

  private async createConferenceChampionshipGames(seasonId: string, bracket: any): Promise<void> {
    try {
      const divisionalGames = this.daoManager.games.getWeekGames(seasonId, 20);
      const winners = divisionalGames
        .filter(g => g.status === 'completed' || g.status === 'simulated')
        .map(g => {
          const winnerId = g.game_data?.winner_id;
          if (!winnerId) return null;
          return this.daoManager.teams.getById(winnerId);
        })
        .filter(t => t !== null && t !== undefined);

      console.log(`🏈 Divisional winners: ${winners.map(w => w?.abbreviation).join(', ')}`);

      const afcWinners = winners.filter(t => t?.conference === 'AFC');
      const nfcWinners = winners.filter(t => t?.conference === 'NFC');

      // Get seeds for winners
      const afcWinnersWithSeeds = afcWinners.map(team => {
        const playoffTeam = bracket.afc_teams?.find((t: any) => t.team.id === team?.id);
        return playoffTeam;
      }).filter(Boolean).sort((a: any, b: any) => a.seed - b.seed);

      const nfcWinnersWithSeeds = nfcWinners.map(team => {
        const playoffTeam = bracket.nfc_teams?.find((t: any) => t.team.id === team?.id);
        return playoffTeam;
      }).filter(Boolean).sort((a: any, b: any) => a.seed - b.seed);

      let gamesCreated = 0;

      // AFC Championship
      if (afcWinnersWithSeeds.length >= 2) {
        this.daoManager.games.create({
          season_id: seasonId,
          week: 21,
          home_team_id: afcWinnersWithSeeds[0].team.id,
          away_team_id: afcWinnersWithSeeds[1].team.id,
          status: 'scheduled'
        });
        gamesCreated++;
      }

      // NFC Championship
      if (nfcWinnersWithSeeds.length >= 2) {
        this.daoManager.games.create({
          season_id: seasonId,
          week: 21,
          home_team_id: nfcWinnersWithSeeds[0].team.id,
          away_team_id: nfcWinnersWithSeeds[1].team.id,
          status: 'scheduled'
        });
        gamesCreated++;
      }

      console.log(`✅ Created ${gamesCreated} Conference Championship games (Week 21)`);
    } catch (error) {
      console.error('Error creating conference championship games:', error);
      throw error;
    }
  }

  private async createSuperBowlGame(seasonId: string, bracket: any): Promise<void> {
    try {
      const confChampGames = this.daoManager.games.getWeekGames(seasonId, 21);
      const winners = confChampGames
        .filter(g => g.status === 'completed' || g.status === 'simulated')
        .map(g => {
          const winnerId = g.game_data?.winner_id;
          if (!winnerId) return null;
          return this.daoManager.teams.getById(winnerId);
        })
        .filter(t => t !== null && t !== undefined);

      console.log(`🏈 Conference Champions: ${winners.map(w => w?.abbreviation).join(', ')}`);

      if (winners.length >= 2) {
        const afcChamp = winners.find(t => t?.conference === 'AFC');
        const nfcChamp = winners.find(t => t?.conference === 'NFC');

        if (afcChamp && nfcChamp) {
          // Get seeds to determine home team (higher seed gets home field)
          const afcTeam = bracket.afc_teams?.find((t: any) => t.team.id === afcChamp.id);
          const nfcTeam = bracket.nfc_teams?.find((t: any) => t.team.id === nfcChamp.id);
          
          const homeTeam = (afcTeam?.seed || 99) < (nfcTeam?.seed || 99) ? afcChamp : nfcChamp;
          const awayTeam = homeTeam.id === afcChamp.id ? nfcChamp : afcChamp;

          this.daoManager.games.create({
            season_id: seasonId,
            week: 22,
            home_team_id: homeTeam.id,
            away_team_id: awayTeam.id,
            status: 'scheduled'
          });
          console.log(`✅ Created Super Bowl (Week 22): ${awayTeam.abbreviation} @ ${homeTeam.abbreviation}`);
        }
      }
    } catch (error) {
      console.error('Error creating Super Bowl game:', error);
      throw error;
    }
  }

  private async updatePlayoffBracketAfterGame(seasonId: string, gameId: string, result: GameResult): Promise<void> {
    try {
      // Get the season service to access the season engine with playoff bracket
      const seasonService = new SeasonService(this.daoManager);
      const seasonStatus = await seasonService.getSeasonStatus(seasonId);
      
      if (!seasonStatus.season_engine) {
        console.warn('No season engine available to update bracket');
        return;
      }

      const playoffEngine = seasonStatus.season_engine.playoffEngine;
      if (!playoffEngine || !playoffEngine.bracket) {
        console.warn('No playoff engine or bracket available');
        return;
      }

      // Find the bracket game and update it directly (don't use advanceBracket which advances rounds)
      const allGames = [
        ...playoffEngine.bracket.wild_card_games,
        ...playoffEngine.bracket.divisional_games,
        ...playoffEngine.bracket.conference_championship_games,
        ...(playoffEngine.bracket.super_bowl ? [playoffEngine.bracket.super_bowl] : [])
      ];

      const bracketGame = allGames.find(g => g.game_id === gameId);
      if (!bracketGame) {
        console.warn(`Bracket game not found for ID: ${gameId}`);
        return;
      }

      // Determine the winner
      const winnerId = result.homeScore > result.awayScore ? result.homeTeam.id : result.awayTeam.id;
      const winner = this.daoManager.teams.getById(winnerId);
      
      if (!winner) {
        console.warn('Winner team not found');
        return;
      }

      // Update the bracket game directly
      bracketGame.home_score = result.homeScore;
      bracketGame.away_score = result.awayScore;
      bracketGame.winner = winner;
      bracketGame.overtime = result.overtime || false;
      bracketGame.completed = true;

      console.log(`✅ Updated playoff bracket game ${gameId}, winner: ${winner.abbreviation}`);
    } catch (error) {
      console.error('Error updating playoff bracket after game:', error);
      // Don't throw - this is a non-critical enhancement
    }
  }
}

export interface SimulationOptions {
  seed?: number;
  weather?: Weather;
}

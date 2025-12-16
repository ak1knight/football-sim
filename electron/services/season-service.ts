import { BaseService } from './base-service';
import { Season } from '../database/dao/season-dao';
import { NFLScheduleGenerator } from './schedule-generator';
import { GameStatus, SeasonEngine, SeasonPhase, ScheduledGame, TeamRecord } from './season-engine';

export class SeasonService extends BaseService {

  async createSeason(seasonData: { name: string; year: number }): Promise<string> {
    try {
      this.validateRequired(seasonData.name, 'season name');
      this.validateRequired(seasonData.year, 'season year');

      return this.daoManager.transaction((dao) => {
        // Create season
        const seasonId = dao.seasons.create({
          name: seasonData.name,
          year: seasonData.year,
          status: 'setup',
          current_week: 1
        });
        
        console.log(`🏈 [CREATE DEBUG] Created season with ID: "${seasonId}"`);

        // Generate schedule for all teams
        const teams = dao.teams.getAll();
        console.log(`🏈 [CREATE DEBUG] Found ${teams.length} teams`);
        
        const generator = new NFLScheduleGenerator();
        const weeklySchedule = generator.generateSchedule(teams, seasonData.year);
        
        // Create games
        const gamesToCreate = Object.entries(weeklySchedule).flatMap(([week, games]) =>
          games.map(game => ({
            season_id: seasonId,
            week: parseInt(week, 10),
            home_team_id: game.home.id,
            away_team_id: game.away.id,
            status: 'scheduled' as const
          }))
        );
        
        console.log(`🏈 [CREATE DEBUG] Creating ${gamesToCreate.length} games with season_id: "${seasonId}"`);
        console.log(`🏈 [CREATE DEBUG] First game example:`, gamesToCreate[0]);
        
        dao.games.createGames(gamesToCreate);
        console.log(`🏈 [CREATE DEBUG] Games created successfully`);

        // Update season to active
        dao.seasons.updateStatus(seasonId, 'active');
        console.log(`🏈 [CREATE DEBUG] Season updated to active status`);
        
        return seasonId;
      });
    } catch (error) {
      this.handleError(error, 'Create season');
    }
  }

  async getGameDetails(gameId: string): Promise<any> {
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

      // If game hasn't been simulated yet, return basic info
      if (game.status === 'scheduled' || !game.game_data) {
        return {
          game_id: game.id,
          home_team: {
            id: homeTeam.id,
            name: `${homeTeam.city} ${homeTeam.name}`,
            abbreviation: homeTeam.abbreviation,
            score: 0,
          },
          away_team: {
            id: awayTeam.id,
            name: `${awayTeam.city} ${awayTeam.name}`,
            abbreviation: awayTeam.abbreviation,
            score: 0,
          },
          status: 'scheduled',
        };
      }

      // Count play types from play-by-play
      const playTypeCounts = { run: 0, pass: 0, turnover: 0 };
      const playByPlay = game.game_data.play_by_play || [];
      for (const play of playByPlay) {
        if (play.playType === 'run') playTypeCounts.run++;
        else if (play.playType === 'pass') playTypeCounts.pass++;
        else if (play.playType === 'turnover') playTypeCounts.turnover++;
      }

      // Extract key plays (scoring plays and turnovers)
      const keyPlays = [];
      let currentQuarter = 1;
      const drives = game.game_data.drives || [];
      
      for (const drive of drives) {
        if (drive.playLog && drive.playLog.length > 0) {
          currentQuarter = drive.quarter;
          const lastPlay = drive.playLog[drive.playLog.length - 1];
          
          // Add scoring plays
          if (drive.result === 'touchdown' || drive.result === 'field_goal') {
            keyPlays.push({
              quarter: currentQuarter,
              time: lastPlay.clock || '0:00',
              description: drive.finalPlayDescription || drive.result,
              scoring_play: true,
              points: drive.points,
              team: drive.offense,
            });
          }
          // Add turnovers
          else if (drive.result === 'turnover' || drive.result === 'turnover_on_downs') {
            keyPlays.push({
              quarter: currentQuarter,
              time: lastPlay.clock || '0:00',
              description: drive.finalPlayDescription || drive.result,
              scoring_play: false,
              team: drive.offense,
            });
          }
        }
      }

      return {
        game_id: game.id,
        home_team: {
          id: homeTeam.id,
          name: `${homeTeam.city} ${homeTeam.name}`,
          abbreviation: homeTeam.abbreviation,
          score: game.home_score || 0,
        },
        away_team: {
          id: awayTeam.id,
          name: `${awayTeam.city} ${awayTeam.name}`,
          abbreviation: awayTeam.abbreviation,
          score: game.away_score || 0,
        },
        winner: game.home_score! > game.away_score! ? 'home' : game.away_score! > game.home_score! ? 'away' : 'tie',
        weather: game.game_data.weather,
        summary: game.game_data.detailed_stats?.summary || '',
        detailed_stats: {
          home: {
            total_yards: game.game_data.stats?.home?.totalYards || 0,
            passing_yards: game.game_data.stats?.home?.passingYards || 0,
            rushing_yards: game.game_data.stats?.home?.rushingYards || 0,
            turnovers: game.game_data.stats?.home?.turnovers || 0,
            plays: game.game_data.stats?.home?.plays || 0,
            time_of_possession: game.game_data.stats?.home?.timeOfPossession || 0,
          },
          away: {
            total_yards: game.game_data.stats?.away?.totalYards || 0,
            passing_yards: game.game_data.stats?.away?.passingYards || 0,
            rushing_yards: game.game_data.stats?.away?.rushingYards || 0,
            turnovers: game.game_data.stats?.away?.turnovers || 0,
            plays: game.game_data.stats?.away?.plays || 0,
            time_of_possession: game.game_data.stats?.away?.timeOfPossession || 0,
          },
          play_type_counts: playTypeCounts,
          total_plays: (game.game_data.stats?.home?.plays || 0) + (game.game_data.stats?.away?.plays || 0),
          total_drives: drives.length,
        },
        drives: drives.map((drive: any, index: number) => ({
          drive_number: index + 1,
          quarter: drive.quarter,
          offense: drive.offense,
          defense: drive.defense,
          starting_position: `${drive.startField}`,
          result: drive.result,
          points: drive.points,
          total_plays: drive.plays,
          total_yards: drive.playLog?.reduce((sum: number, play: any) => sum + play.yardsGained, 0) || 0,
          time_elapsed: drive.timeElapsed,
          final_play_description: drive.finalPlayDescription,
          play_log: drive.playLog?.map((play: any) => ({
            quarter: play.quarter,
            down: play.down,
            yards_to_go: play.yardsToGo,
            start_field: play.startField,
            end_field: play.endField,
            play_type: play.playType,
            yards_gained: play.yardsGained,
            clock: play.clock,
          })) || [],
        })),
        key_plays: keyPlays,
        overtime: game.game_data.detailed_stats?.overtime || false,
        duration: game.game_data.detailed_stats?.duration || 60,
      };
    } catch (error) {
      this.handleError(error, 'Get game details');
    }
  }

  async getSeasonStatus(seasonId: string): Promise<any> {
    try {
      this.validateId(seasonId, 'season');
      
      console.log(`🏈 [SEASON SERVICE DEBUG] getSeasonStatus called with seasonId: "${seasonId}"`);
      console.log(`🏈 [SEASON SERVICE DEBUG] seasonId length: ${seasonId.length}, type: ${typeof seasonId}`);
      
      const season = this.daoManager.seasons.getById(seasonId);
      console.log(`🏈 [SEASON SERVICE DEBUG] getById result:`, season);
      
      if (!season) {
        // List all seasons to help debug
        const allSeasons = this.daoManager.seasons.getAll();
        console.log(`🏈 [SEASON SERVICE DEBUG] All seasons in DB (${allSeasons.length}):`, allSeasons.map(s => ({ id: s.id, name: s.name })));
        throw new Error('Season not found');
      }

      console.log(`🏈 [SEASON SERVICE DEBUG] Getting stats for season: ${seasonId}`);
      const seasonStats = this.daoManager.seasons.getSeasonStats(seasonId);
      console.log(`🏈 [SEASON SERVICE DEBUG] seasonStats:`, seasonStats);
      
      const gameStats = this.daoManager.games.getGameStats(seasonId);
      console.log(`🏈 [SEASON SERVICE DEBUG] gameStats:`, gameStats);

      // Return in the format expected by frontend SeasonStatus interface
      const result = {
        id: season.id,
        year: season.year,
        season_year: season.year, // Added for SeasonSetup component compatibility
        name: season.name,
        current_week: season.current_week,
        current_phase: season.status === 'playoffs' ? 'playoffs' : 'regular_season',
        total_games: seasonStats?.games?.total || 0,
        completed_games: seasonStats?.games?.completed || 0,
        completion_percentage: seasonStats?.games?.completion_percentage || 0,
        next_games_count: seasonStats?.games?.remaining || 0,
        weeks_remaining: Math.max(0, 18 - season.current_week),
        schedule_type: 'balanced',
        status: season.status || 'active' // Added status field
      };
      
      console.log(`🏈 [SEASON SERVICE DEBUG] Final result:`, result);
      return result;
    } catch (error) {
      this.handleError(error, 'Get season status');
    }
  }

  async getStandings(seasonId: string): Promise<any> {
    try {
      this.validateId(seasonId, 'season');
      return this.daoManager.getLeagueStandings(seasonId);
    } catch (error) {
      this.handleError(error, 'Get standings');
    }
  }

  async getNextGames(seasonId: string, limit?: number): Promise<any[]> {
    try {
      this.validateId(seasonId, 'season');
      const games = this.daoManager.games.getNextGames(seasonId, limit || 16);
      
      return games.map(game => this.formatGameSummary(game));
    } catch (error) {
      this.handleError(error, 'Get next games');
    }
  }

  async getWeekGames(seasonId: string, week: number): Promise<any[]> {
    try {
      this.validateId(seasonId, 'season');
      this.validateRequired(week, 'week');
      
      if (week < 1 || week > 22) {
        throw new Error('Week must be between 1 and 22');
      }

      const games = this.daoManager.games.getWeekGames(seasonId, week);
      return games.map(game => this.formatGameSummary(game));
    } catch (error) {
      this.handleError(error, 'Get week games');
    }
  }

  async getTeamSchedule(seasonId: string, teamId: string): Promise<any[]> {
    try {
      this.validateId(seasonId, 'season');
      this.validateId(teamId, 'team');
      
      return this.daoManager.games.getTeamSchedule(seasonId, teamId);
    } catch (error) {
      this.handleError(error, 'Get team schedule');
    }
  }

  async getPlayoffBracket(seasonId: string): Promise<any> {
    try {
      this.validateId(seasonId, 'season');
      const engine = this.buildSeasonEngine(seasonId);
      const bracket = engine.getPlayoffBracket();
      const picture = engine.getPlayoffPicture();
      
      // Enhance bracket games with additional metadata
      if (bracket) {
        this.enhanceBracketGames(bracket);
      }
      
      return {
        season_id: seasonId,
        bracket,
        playoff_picture: picture
      };
    } catch (error) {
      this.handleError(error, 'Get playoff bracket');
    }
  }

  async getAllSeasons(): Promise<Season[]> {
    try {
      return this.daoManager.seasons.getAll();
    } catch (error) {
      this.handleError(error, 'Get all seasons');
    }
  }

  async getActiveSeason(): Promise<Season | null> {
    try {
      const season = this.daoManager.seasons.getActiveSeason();
      return season || null;
    } catch (error) {
      this.handleError(error, 'Get active season');
    }
  }

  async updateSeasonStatus(seasonId: string, status: Season['status']): Promise<boolean> {
    try {
      this.validateId(seasonId, 'season');
      this.validateRequired(status, 'status');
      
      return this.daoManager.seasons.updateStatus(seasonId, status);
    } catch (error) {
      this.handleError(error, 'Update season status');
    }
  }

  async advanceWeek(seasonId: string): Promise<boolean> {
    try {
      this.validateId(seasonId, 'season');
      return this.daoManager.seasons.advanceWeek(seasonId);
    } catch (error) {
      this.handleError(error, 'Advance week');
    }
  }

  private formatGameSummary(game: any) {
    const homeTeam = this.daoManager.teams.getById(game.home_team_id);
    const awayTeam = this.daoManager.teams.getById(game.away_team_id);
    
    return {
      game_id: game.id,
      week: game.week,
      status: game.status,
      home_team: homeTeam ? {
        name: homeTeam.name,
        city: homeTeam.city,
        abbreviation: homeTeam.abbreviation
      } : null,
      away_team: awayTeam ? {
        name: awayTeam.name,
        city: awayTeam.city,
        abbreviation: awayTeam.abbreviation
      } : null,
      home_score: game.home_score || 0,
      away_score: game.away_score || 0,
      overtime: game.game_data?.overtime || false,
      winner: game.game_data?.winner_id || null,
      scheduled_date: null // Could add this later if needed
    };
  }

  private buildSeasonEngine(seasonId: string): SeasonEngine {
    const season = this.daoManager.seasons.getById(seasonId);
    if (!season) {
      throw new Error('Season not found');
    }

    const teams = this.daoManager.teams.getAll();
    const teamMap = new Map(teams.map(team => [team.id, team]));

    const schedule: ScheduledGame[] = this.daoManager.games.getSeasonGames(seasonId)
      .map(game => {
        const homeTeam = teamMap.get(game.home_team_id);
        const awayTeam = teamMap.get(game.away_team_id);
        if (!homeTeam || !awayTeam) return null;

        const status = this.mapStatus(game.status);
        return {
          game_id: game.id,
          home_team: homeTeam,
          away_team: awayTeam,
          week: game.week,
          status,
          home_score: game.home_score ?? undefined,
          away_score: game.away_score ?? undefined,
          overtime: game.game_data?.overtime ?? false,
          game_duration: game.game_data?.duration
        } as ScheduledGame;
      })
      .filter((g): g is ScheduledGame => g !== null);

    const records: Record<string, TeamRecord> = {};
    for (const team of teams) {
      records[team.id] = new TeamRecord(team);
    }

    const currentPhase = season.status === 'playoffs' ? SeasonPhase.PLAYOFFS : SeasonPhase.REGULAR_SEASON;

    const engine = new SeasonEngine({
      teams,
      seasonYear: season.year,
      currentWeek: season.current_week,
      currentPhase,
      schedule,
      records
    });

    // If in playoffs, update bracket with completed game results
    if (season.status === 'playoffs') {
      this.updatePlayoffBracketWithResults(engine, seasonId, teamMap);
    }

    return engine;
  }

  private mapStatus(status: string): GameStatus {
    if (status === 'completed' || status === 'simulated') return GameStatus.COMPLETED;
    if (status === 'in_progress') return GameStatus.IN_PROGRESS;
    if (status === 'postponed') return GameStatus.POSTPONED;
    return GameStatus.SCHEDULED;
  }

  private updatePlayoffBracketWithResults(engine: any, seasonId: string, teamMap: Map<string, any>) {
    try {
      // Get playoff games (weeks 19-22)
      const playoffGames = this.daoManager.games.getSeasonGames(seasonId)
        .filter(g => g.week >= 19 && g.week <= 22);

      if (playoffGames.length === 0) return;

      // Get or generate the bracket
      const bracket = engine.getPlayoffBracket();
      if (!bracket) return;

      // Update bracket games with database game IDs and results
      playoffGames.forEach(game => {
        const homeTeam = teamMap.get(game.home_team_id);
        const awayTeam = teamMap.get(game.away_team_id);
        
        if (!homeTeam || !awayTeam) {
          console.warn(`Missing team data for game ${game.id}: home=${game.home_team_id}, away=${game.away_team_id}`);
          return;
        }

        // Try to find and update the game in the bracket
        const allBracketGames = [
          ...bracket.wild_card_games,
          ...bracket.divisional_games,
          ...bracket.conference_championship_games,
          ...(bracket.super_bowl ? [bracket.super_bowl] : [])
        ];

        console.log(`🔍 Looking for bracket game: ${awayTeam.abbreviation} @ ${homeTeam.abbreviation}`);
        console.log(`   Database game has: home_team_id=${game.home_team_id}, away_team_id=${game.away_team_id}`);
        console.log(`   Found ${allBracketGames.length} bracket games to search`);

        // Find matching game by teams - try multiple matching strategies
        const bracketGame = allBracketGames.find((bg, idx) => {
          console.log(`   Checking bracket game #${idx}: home=${bg.home_team?.abbreviation}/${bg.home_team?.id}, away=${bg.away_team?.abbreviation}/${bg.away_team?.id}`);
          
          if (!bg.home_team || !bg.away_team) {
            console.log(`     ❌ Missing teams`);
            return false;
          }
          
          // Try ID match
          if (bg.home_team.id === homeTeam.id && bg.away_team.id === awayTeam.id) {
            console.log(`     ✅ Matched by ID`);
            return true;
          }
          
          // Try abbreviation match
          if (bg.home_team.abbreviation === homeTeam.abbreviation && 
              bg.away_team.abbreviation === awayTeam.abbreviation) {
            console.log(`     ✅ Matched by abbreviation`);
            return true;
          }
          
          // Try name match as fallback
          if (bg.home_team.name === homeTeam.name && 
              bg.away_team.name === awayTeam.name) {
            console.log(`     ✅ Matched by name`);
            return true;
          }
          
          console.log(`     ❌ No match`);
          return false;
        });

        if (bracketGame) {
          console.log(`✅ Matched database game ${game.id} to bracket game ${bracketGame.game_id}: ${awayTeam.abbreviation} @ ${homeTeam.abbreviation}`);
          // CRITICAL: Update the game_id to use the database ID, not the bracket's internal ID
          bracketGame.game_id = game.id;
          
          // Update scores and completion status if game is completed
          if (game.status === 'completed' || game.status === 'simulated') {
            const winnerId = game.game_data?.winner_id;
            const winner = winnerId ? teamMap.get(winnerId) : null;
            
            bracketGame.home_score = game.home_score ?? 0;
            bracketGame.away_score = game.away_score ?? 0;
            bracketGame.winner = winner;
            bracketGame.completed = true;
            bracketGame.overtime = game.game_data?.overtime ?? false;
          }
        } else {
          console.warn(`❌ Could not match database game ${game.id} to bracket: ${awayTeam.abbreviation} @ ${homeTeam.abbreviation}`);
        }
      });

      // Update current round based on completed games
      if (bracket.wild_card_games.every((g: any) => g.completed)) {
        if (bracket.divisional_games.every((g: any) => g.completed)) {
          if (bracket.conference_championship_games.every((g: any) => g.completed)) {
            bracket.current_round = 'super_bowl';
          } else {
            bracket.current_round = 'conference_championship';
          }
        } else {
          bracket.current_round = 'divisional';
        }
      }
    } catch (error) {
      console.error('Error updating playoff bracket with results:', error);
    }
  }

  private enhanceBracketGames(bracket: any) {
    try {
      // Add metadata to each game
      const addMetadata = (games: any[]) => {
        games.forEach(game => {
          // Check if game is ready to play (both teams are set)
          game.is_ready_to_play = !!(game.home_team && game.away_team);
          
          // Add matchup description
          if (game.home_team && game.away_team) {
            const homeAbbr = game.home_team.abbreviation || game.home_team.name;
            const awayAbbr = game.away_team.abbreviation || game.away_team.name;
            game.matchup_description = `${awayAbbr} @ ${homeAbbr}`;
          } else {
            game.matchup_description = 'TBD';
          }
          
          // Ensure overtime field exists
          if (game.overtime === undefined) {
            game.overtime = false;
          }
        });
      };

      if (bracket.wild_card_games) addMetadata(bracket.wild_card_games);
      if (bracket.divisional_games) addMetadata(bracket.divisional_games);
      if (bracket.conference_championship_games) addMetadata(bracket.conference_championship_games);
      if (bracket.super_bowl) addMetadata([bracket.super_bowl]);
    } catch (error) {
      console.error('Error enhancing bracket games:', error);
    }
  }
}

// api.ts - API wrapper for Electron IPC communication

// Define the electron API interface that matches preload.ts
interface ElectronAPI {
  teams: {
    getAll: () => Promise<any>;
    getById: (teamId: string) => Promise<any>;
    getByConference: (conference: 'AFC' | 'NFC') => Promise<any>;
    getByDivision: (conference: 'AFC' | 'NFC', division: string) => Promise<any>;
    compare: (team1Id: string, team2Id: string) => Promise<any>;
  };
  seasons: {
    getAll: () => Promise<any>;
    create: (seasonData: any) => Promise<any>;
    getStatus: (seasonId: string) => Promise<any>;
    getStandings: (seasonId: string) => Promise<any>;
    getNextGames: (seasonId: string, limit?: number) => Promise<any>;
    getWeekGames: (seasonId: string, week: number) => Promise<any>;
    getTeamSchedule: (seasonId: string, teamId: string) => Promise<any>;
    simulateGame: (gameId: string, options?: any) => Promise<any>;
    simulateWeek: (seasonId: string, week: number, options?: any) => Promise<any>;
    simulateToWeek: (seasonId: string, targetWeek: number, options?: any) => Promise<any>;
    simulateSeason: (seasonId: string, options?: any) => Promise<any>;
    getPlayoffBracket: (seasonId: string) => Promise<any>;
    simulatePlayoffGame: (gameId: string, options?: any) => Promise<any>;
  };
  exhibition: {
    simulate: (homeTeamId: string, awayTeamId: string, options?: any) => Promise<any>;
  };
  app: {
    getVersion: () => Promise<any>;
    quit: () => Promise<any>;
    minimize: () => Promise<any>;
    maximize: () => Promise<any>;
    unmaximize: () => Promise<any>;
    close: () => Promise<any>;
  };
  debug: {
    listSeasons: () => Promise<any>;
    tableCounts: () => Promise<any>;
    seasonGames: (seasonId?: string) => Promise<any>;
  };
}

// Global electron API available on window object
declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}

/**
 * Unified API function that routes requests to appropriate Electron IPC handlers
 * This replaces HTTP fetch with IPC communication
 */
export async function apiFetch(endpoint: string, options: RequestInit = {}): Promise<Response> {
  try {
    // Parse the endpoint to determine which IPC method to call
    const url = new URL(endpoint, 'http://localhost'); // Base URL for parsing
    const pathParts = url.pathname.split('/').filter(part => part !== '');
    
    let result: any;
    
    // Route to appropriate IPC handler based on endpoint
    if (pathParts[0] === 'api') {
      const [, resource, action] = pathParts;
      
      switch (resource) {
        case 'teams':
          result = await handleTeamsAPI(action, url.searchParams, options);
          break;
          
        case 'seasons':
          result = await handleSeasonsAPI(action, pathParts.slice(2), url.searchParams, options);
          break;
          
        case 'exhibition':
          result = await handleExhibitionAPI(action, url.searchParams, options);
          break;
          
        case 'app':
          result = await handleAppAPI(action, url.searchParams, options);
          break;
          
        default:
          throw new Error(`Unknown API resource: ${resource}`);
      }
    } else {
      throw new Error(`Invalid API endpoint: ${endpoint}`);
    }
    
    // Convert IPC result to Response-like object for compatibility
    return createMockResponse(result);
    
  } catch (error) {
    console.error('API Error:', error);
    return createMockResponse({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    }, false);
  }
}

async function handleTeamsAPI(action: string, params: URLSearchParams, options: RequestInit) {
  const electronAPI = window.electronAPI;
  
  switch (action) {
    case 'all':
      return await electronAPI.teams.getAll();
      
    case 'by-id':
      const teamId = params.get('id');
      if (!teamId) throw new Error('Team ID required');
      return await electronAPI.teams.getById(teamId);
      
    case 'by-conference':
      const conference = params.get('conference') as 'AFC' | 'NFC';
      if (!conference) throw new Error('Conference required');
      return await electronAPI.teams.getByConference(conference);
      
    case 'by-division':
      const divConference = params.get('conference') as 'AFC' | 'NFC';
      const division = params.get('division');
      if (!divConference || !division) throw new Error('Conference and division required');
      return await electronAPI.teams.getByDivision(divConference, division);
      
    case 'compare':
      const team1Id = params.get('team1');
      const team2Id = params.get('team2');
      if (!team1Id || !team2Id) throw new Error('Both team IDs required for comparison');
      return await electronAPI.teams.compare(team1Id, team2Id);
      
    default:
      throw new Error(`Unknown teams action: ${action}`);
  }
}

async function handleSeasonsAPI(action: string, pathParts: string[], params: URLSearchParams, options: RequestInit) {
  const electronAPI = window.electronAPI;
  
  switch (action) {
    case 'all':
      return await electronAPI.seasons.getAll();
      
    case 'create':
      const seasonData = options.body ? JSON.parse(options.body as string) : {};
      return await electronAPI.seasons.create(seasonData);
      
    case 'status':
      const statusSeasonId = pathParts[1]; // Fixed: was pathParts[0]
      if (!statusSeasonId) throw new Error('Season ID required');
      return await electronAPI.seasons.getStatus(statusSeasonId);
      
    case 'standings':
      const standingsSeasonId = pathParts[1]; // Fixed: was pathParts[0]
      if (!standingsSeasonId) throw new Error('Season ID required');
      return await electronAPI.seasons.getStandings(standingsSeasonId);
      
    case 'next-games':
      const nextGamesSeasonId = pathParts[1]; // Fixed: was pathParts[0]
      const limit = params.get('limit') ? parseInt(params.get('limit')!) : undefined;
      if (!nextGamesSeasonId) throw new Error('Season ID required');
      return await electronAPI.seasons.getNextGames(nextGamesSeasonId, limit);
      
    case 'week-games':
      const weekSeasonId = pathParts[1]; // Fixed: was pathParts[0]
      const week = parseInt(pathParts[2] || params.get('week') || '1'); // Fixed: was pathParts[1]
      if (!weekSeasonId) throw new Error('Season ID required');
      return await electronAPI.seasons.getWeekGames(weekSeasonId, week);
      
    case 'team-schedule':
      const scheduleSeasonId = pathParts[1]; // Fixed: was pathParts[0]
      const scheduleTeamId = pathParts[2] || params.get('teamId'); // Fixed: was pathParts[1]
      if (!scheduleSeasonId || !scheduleTeamId) throw new Error('Season ID and Team ID required');
      return await electronAPI.seasons.getTeamSchedule(scheduleSeasonId, scheduleTeamId);
      
    case 'simulate-game':
      const gameOptions = options.body ? JSON.parse(options.body as string) : {};
      const gameId = gameOptions.game_id || pathParts[0] || params.get('gameId');
      if (!gameId) throw new Error('Game ID required');
      return await electronAPI.seasons.simulateGame(gameId, gameOptions);
      
    case 'simulate-week':
      const weekOptions = options.body ? JSON.parse(options.body as string) : {};
      if (!weekOptions.seasonId) throw new Error('Season ID required in request body');
      return await electronAPI.seasons.simulateWeek(weekOptions.seasonId, weekOptions.week, weekOptions);
      
    case 'simulate-to-week':
      const simToWeekSeasonId = pathParts[0]; // Reverted: this is not used, data comes from POST body
      const targetWeek = parseInt(pathParts[1] || params.get('targetWeek') || '1'); // Reverted: this is not used, data comes from POST body
      const toWeekOptions = options.body ? JSON.parse(options.body as string) : undefined;
      // For simulate-to-week, seasonId and targetWeek come from POST body, not URL
      return await electronAPI.seasons.simulateToWeek(toWeekOptions?.seasonId || simToWeekSeasonId, toWeekOptions?.targetWeek || targetWeek, toWeekOptions);
      
    case 'simulate-season':
      const simSeasonId = pathParts[1]; // Reverted: this is not used, data comes from POST body
      const seasonOptions = options.body ? JSON.parse(options.body as string) : undefined;
      // For simulate-season, seasonId comes from POST body, not URL
      return await electronAPI.seasons.simulateSeason(seasonOptions?.seasonId || simSeasonId, seasonOptions);
      
    case 'playoff-bracket':
      const playoffSeasonId = pathParts[1]; // Fixed: was pathParts[0]
      if (!playoffSeasonId) throw new Error('Season ID required');
      return await electronAPI.seasons.getPlayoffBracket(playoffSeasonId);
      
    case 'simulate-playoff-game':
      const playoffGameId = pathParts[1] || params.get('gameId'); // Fixed: was pathParts[0]
      const playoffOptions = options.body ? JSON.parse(options.body as string) : undefined;
      if (!playoffGameId) throw new Error('Game ID required');
      return await electronAPI.seasons.simulatePlayoffGame(playoffGameId, playoffOptions);
      
    default:
      throw new Error(`Unknown seasons action: ${action}`);
  }
}

async function handleExhibitionAPI(action: string, params: URLSearchParams, options: RequestInit) {
  const electronAPI = window.electronAPI;
  
  switch (action) {
    case 'simulate':
      const homeTeamId = params.get('homeTeam');
      const awayTeamId = params.get('awayTeam');
      const exhibitionOptions = options.body ? JSON.parse(options.body as string) : undefined;
      
      if (!homeTeamId || !awayTeamId) {
        throw new Error('Both home and away team IDs required');
      }
      
      return await electronAPI.exhibition.simulate(homeTeamId, awayTeamId, exhibitionOptions);
      
    default:
      throw new Error(`Unknown exhibition action: ${action}`);
  }
}

async function handleAppAPI(action: string, params: URLSearchParams, options: RequestInit) {
  const electronAPI = window.electronAPI;
  
  switch (action) {
    case 'version':
      return await electronAPI.app.getVersion();
      
    case 'quit':
      return await electronAPI.app.quit();
      
    case 'minimize':
      return await electronAPI.app.minimize();
      
    case 'maximize':
      return await electronAPI.app.maximize();
      
    case 'unmaximize':
      return await electronAPI.app.unmaximize();
      
    case 'close':
      return await electronAPI.app.close();
      
    default:
      throw new Error(`Unknown app action: ${action}`);
  }
}

/**
 * Create a mock Response object for compatibility with existing fetch-based code
 */
function createMockResponse(data: any, success: boolean = true): Response {
  const responseData = {
    success: success && data.success !== false,
    data: data.data || data,
    error: data.error
  };
  
  return {
    ok: success && data.success !== false,
    status: success && data.success !== false ? 200 : 400,
    statusText: success && data.success !== false ? 'OK' : 'Bad Request',
    json: async () => responseData,
    text: async () => JSON.stringify(responseData),
    headers: new Headers({ 'Content-Type': 'application/json' }),
    body: null,
    bodyUsed: false,
    arrayBuffer: async () => new ArrayBuffer(0),
    blob: async () => new Blob(),
    formData: async () => new FormData(),
    clone: () => createMockResponse(data, success),
    redirect: () => createMockResponse(data, success),
    type: 'basic' as ResponseType,
    url: '',
    redirected: false,
  } as Response;
}

// Debug functions for database inspection
export async function debugTableCounts(): Promise<void> {
  try {
    const result = await (window as any).electronAPI.invoke('debug:tableCounts');
    console.log('Debug table counts:', result);
  } catch (error) {
    console.error('Failed to get table counts:', error);
  }
}

export async function debugSeasonGames(seasonId?: string): Promise<void> {
  try {
    const result = await (window as any).electronAPI.invoke('debug:seasonGames', seasonId);
    console.log('Debug season games:', result);
  } catch (error) {
    console.error('Failed to get season games:', error);
  }
}

export async function debugListAllSeasons(): Promise<void> {
  try {
    const result = await (window as any).electronAPI.invoke('seasons:getAll');
    console.log('🏈 [DEBUG] All seasons in database:', result);
  } catch (error) {
    console.error('Failed to get all seasons:', error);
  }
}
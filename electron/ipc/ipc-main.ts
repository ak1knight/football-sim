import { ipcMain } from 'electron';
import { DAOManager } from '../database/dao/dao-manager';
import { TeamService } from '../services/team-service';
import { SeasonService } from '../services/season-service';
import { SimulationService } from '../services/simulation-service';
import { AppService } from '../services/app-service';

export function setupIpcHandlers(daoManager: DAOManager): void {
  console.log('🔗 Setting up IPC handlers...');

  // Initialize services
  const teamService = new TeamService(daoManager);
  const seasonService = new SeasonService(daoManager);
  const simulationService = new SimulationService(daoManager);
  const appService = new AppService(daoManager);

  // Team handlers
  ipcMain.handle('teams:getAll', async () => {
    try {
      const teams = await teamService.getAllTeams();
      return { success: true, data: teams };
    } catch (error) {
      console.error('teams:getAll error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  });

  ipcMain.handle('teams:getById', async (event, teamId: string) => {
    try {
      const team = await teamService.getTeamById(teamId);
      return { success: true, data: team };
    } catch (error) {
      console.error('teams:getById error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  });

  ipcMain.handle('teams:getByConference', async (event, conference: 'AFC' | 'NFC') => {
    try {
      const teams = await teamService.getTeamsByConference(conference);
      return { success: true, data: teams };
    } catch (error) {
      console.error('teams:getByConference error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  });

  ipcMain.handle('teams:getByDivision', async (event, conference: 'AFC' | 'NFC', division: string) => {
    try {
      const teams = await teamService.getTeamsByDivision(conference, division);
      return { success: true, data: teams };
    } catch (error) {
      console.error('teams:getByDivision error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  });

  ipcMain.handle('teams:compare', async (event, team1Id: string, team2Id: string) => {
    try {
      const comparison = await teamService.compareTeams(team1Id, team2Id);
      return { success: true, data: comparison };
    } catch (error) {
      console.error('teams:compare error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  });

  // Season handlers
  ipcMain.handle('seasons:create', async (event, seasonData: any) => {
    try {
      const seasonId = await seasonService.createSeason(seasonData);
      return { success: true, data: { seasonId } };
    } catch (error) {
      console.error('seasons:create error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  });

  ipcMain.handle('seasons:getStatus', async (event, seasonId: string) => {
    try {
      const status = await seasonService.getSeasonStatus(seasonId);
      return { success: true, data: status };
    } catch (error) {
      console.error('seasons:getStatus error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  });

  ipcMain.handle('seasons:getStandings', async (event, seasonId: string) => {
    try {
      const standings = await seasonService.getStandings(seasonId);
      return { success: true, data: standings };
    } catch (error) {
      console.error('seasons:getStandings error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  });

  ipcMain.handle('seasons:getNextGames', async (event, seasonId: string, limit?: number) => {
    try {
      const games = await seasonService.getNextGames(seasonId, limit);
      return { success: true, data: games };
    } catch (error) {
      console.error('seasons:getNextGames error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  });

  ipcMain.handle('seasons:getWeekGames', async (event, seasonId: string, week: number) => {
    try {
      const games = await seasonService.getWeekGames(seasonId, week);
      return { success: true, data: games };
    } catch (error) {
      console.error('seasons:getWeekGames error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  });

  ipcMain.handle('seasons:getTeamSchedule', async (event, seasonId: string, teamId: string) => {
    try {
      const schedule = await seasonService.getTeamSchedule(seasonId, teamId);
      return { success: true, data: schedule };
    } catch (error) {
      console.error('seasons:getTeamSchedule error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  });

  ipcMain.handle('seasons:simulateGame', async (event, gameId: string, options?: any) => {
    try {
      const result = await simulationService.simulateGame(gameId, options);
      return { success: true, data: result };
    } catch (error) {
      console.error('seasons:simulateGame error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  });

  ipcMain.handle('seasons:simulateWeek', async (event, seasonId: string, week: number, options?: any) => {
    try {
      const results = await simulationService.simulateWeek(seasonId, week, options);
      return { success: true, data: results };
    } catch (error) {
      console.error('seasons:simulateWeek error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  });

  ipcMain.handle('seasons:simulateToWeek', async (event, seasonId: string, targetWeek: number, options?: any) => {
    try {
      const results = await simulationService.simulateToWeek(seasonId, targetWeek, options);
      return { success: true, data: results };
    } catch (error) {
      console.error('seasons:simulateToWeek error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  });

  ipcMain.handle('seasons:simulateSeason', async (event, seasonId: string, options?: any) => {
    try {
      const results = await simulationService.simulateSeason(seasonId, options);
      return { success: true, data: results };
    } catch (error) {
      console.error('seasons:simulateSeason error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  });

  ipcMain.handle('seasons:getPlayoffBracket', async (event, seasonId: string) => {
    try {
      const bracket = await seasonService.getPlayoffBracket(seasonId);
      return { success: true, data: bracket };
    } catch (error) {
      console.error('seasons:getPlayoffBracket error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  });

  ipcMain.handle('seasons:simulatePlayoffGame', async (event, gameId: string, options?: any) => {
    try {
      const result = await simulationService.simulatePlayoffGame(gameId, options);
      return { success: true, data: result };
    } catch (error) {
      console.error('seasons:simulatePlayoffGame error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  });

  // Exhibition handlers
  ipcMain.handle('exhibition:simulate', async (event, homeTeamId: string, awayTeamId: string, options?: any) => {
    try {
      const result = await simulationService.simulateExhibitionGame(homeTeamId, awayTeamId, options);
      return { success: true, data: result };
    } catch (error) {
      console.error('exhibition:simulate error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  });

  // App utility handlers
  ipcMain.handle('app:getVersion', async () => {
    try {
      const version = await appService.getVersion();
      return { success: true, data: version };
    } catch (error) {
      console.error('app:getVersion error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  });

  ipcMain.handle('app:exportData', async () => {
    try {
      const data = await appService.exportData();
      return { success: true, data };
    } catch (error) {
      console.error('app:exportData error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  });

  ipcMain.handle('app:importData', async (event, data: string) => {
    try {
      await appService.importData(data);
      return { success: true, data: { message: 'Data imported successfully' } };
    } catch (error) {
      console.error('app:importData error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  });

  ipcMain.handle('app:showSaveDialog', async (event, options: any) => {
    try {
      const result = await appService.showSaveDialog(options);
      return { success: true, data: result };
    } catch (error) {
      console.error('app:showSaveDialog error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  });

  ipcMain.handle('app:showOpenDialog', async (event, options: any) => {
    try {
      const result = await appService.showOpenDialog(options);
      return { success: true, data: result };
    } catch (error) {
      console.error('app:showOpenDialog error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  });

  ipcMain.handle('app:createBackup', async (event, name?: string) => {
    try {
      const backupPath = await appService.createBackup(name);
      return { success: true, data: { backupPath } };
    } catch (error) {
      console.error('app:createBackup error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  });

  ipcMain.handle('app:restoreBackup', async (event, backupName: string) => {
    try {
      await appService.restoreBackup(backupName);
      return { success: true, data: { message: 'Backup restored successfully' } };
    } catch (error) {
      console.error('app:restoreBackup error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  });

  ipcMain.handle('app:listBackups', async () => {
    try {
      const backups = await appService.listBackups();
      return { success: true, data: backups };
    } catch (error) {
      console.error('app:listBackups error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  });

  ipcMain.handle('app:deleteBackup', async (event, backupName: string) => {
    try {
      await appService.deleteBackup(backupName);
      return { success: true, data: { message: 'Backup deleted successfully' } };
    } catch (error) {
      console.error('app:deleteBackup error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  });

  // Development utilities (only in development)
  if (!process.env.NODE_ENV || process.env.NODE_ENV === 'development') {
    ipcMain.handle('dev:openDevTools', async (event) => {
      try {
        const webContents = event.sender;
        webContents.openDevTools();
        return { success: true, data: { message: 'DevTools opened' } };
      } catch (error) {
        console.error('dev:openDevTools error:', error);
        return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
      }
    });

    ipcMain.handle('dev:reloadWindow', async (event) => {
      try {
        const webContents = event.sender;
        webContents.reload();
        return { success: true, data: { message: 'Window reloaded' } };
      } catch (error) {
        console.error('dev:reloadWindow error:', error);
        return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
      }
    });
  }

  console.log('✅ IPC handlers registered successfully');
}

// Remove all IPC handlers (useful for cleanup)
export function removeIpcHandlers(): void {
  ipcMain.removeAllListeners();
  console.log('🧹 IPC handlers removed');
}
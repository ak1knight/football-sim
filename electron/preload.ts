import { contextBridge, ipcRenderer } from 'electron';

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
const electronAPI = {
  // Teams API
  teams: {
    getAll: () => ipcRenderer.invoke('teams:getAll'),
    getById: (teamId: string) => ipcRenderer.invoke('teams:getById', teamId),
    getByConference: (conference: 'AFC' | 'NFC') => 
      ipcRenderer.invoke('teams:getByConference', conference),
    getByDivision: (conference: 'AFC' | 'NFC', division: string) =>
      ipcRenderer.invoke('teams:getByDivision', conference, division),
    compare: (team1Id: string, team2Id: string) => 
      ipcRenderer.invoke('teams:compare', team1Id, team2Id),
  },
  
  // Season API
  seasons: {
    getAll: () => ipcRenderer.invoke('seasons:getAll'),
    create: (seasonData: any) => ipcRenderer.invoke('seasons:create', seasonData),
    getStatus: (seasonId: string) => ipcRenderer.invoke('seasons:getStatus', seasonId),
    getStandings: (seasonId: string) => ipcRenderer.invoke('seasons:getStandings', seasonId),
    getNextGames: (seasonId: string, limit?: number) =>
      ipcRenderer.invoke('seasons:getNextGames', seasonId, limit),
    getWeekGames: (seasonId: string, week: number) =>
      ipcRenderer.invoke('seasons:getWeekGames', seasonId, week),
    getGameDetails: (gameId: string) => ipcRenderer.invoke('seasons:getGameDetails', gameId),
    getTeamSchedule: (seasonId: string, teamId: string) =>
      ipcRenderer.invoke('seasons:getTeamSchedule', seasonId, teamId),
    simulateGame: (gameId: string, options?: any) => 
      ipcRenderer.invoke('seasons:simulateGame', gameId, options),
    simulateWeek: (seasonId: string, week: number, options?: any) =>
      ipcRenderer.invoke('seasons:simulateWeek', seasonId, week, options),
    simulateToWeek: (seasonId: string, targetWeek: number, options?: any) =>
      ipcRenderer.invoke('seasons:simulateToWeek', seasonId, targetWeek, options),
    simulateSeason: (seasonId: string, options?: any) =>
      ipcRenderer.invoke('seasons:simulateSeason', seasonId, options),
    getPlayoffBracket: (seasonId: string) =>
      ipcRenderer.invoke('seasons:getPlayoffBracket', seasonId),
    simulatePlayoffGame: (gameId: string, options?: any) =>
      ipcRenderer.invoke('seasons:simulatePlayoffGame', gameId, options),
  },

  // Exhibition API
  exhibition: {
    simulate: (homeTeamId: string, awayTeamId: string, options?: any) =>
      ipcRenderer.invoke('exhibition:simulate', homeTeamId, awayTeamId, options),
  },

  // Game details API
  getGameDetails: (gameId: string) => ipcRenderer.invoke('games:getDetails', gameId),

  // App utilities
  app: {
    getVersion: () => ipcRenderer.invoke('app:getVersion'),
    exportData: () => ipcRenderer.invoke('app:exportData'),
    importData: (data: string) => ipcRenderer.invoke('app:importData', data),
    showSaveDialog: (options: any) => ipcRenderer.invoke('app:showSaveDialog', options),
    showOpenDialog: (options: any) => ipcRenderer.invoke('app:showOpenDialog', options),
    createBackup: (name?: string) => ipcRenderer.invoke('app:createBackup', name),
    restoreBackup: (backupName: string) => ipcRenderer.invoke('app:restoreBackup', backupName),
    listBackups: () => ipcRenderer.invoke('app:listBackups'),
    deleteBackup: (backupName: string) => ipcRenderer.invoke('app:deleteBackup', backupName),
    quit: () => ipcRenderer.send('quit-app'),
  },

  // Development utilities
  dev: {
    openDevTools: () => ipcRenderer.invoke('dev:openDevTools'),
    reloadWindow: () => ipcRenderer.invoke('dev:reloadWindow'),
  },

  // Debug utilities
  debug: {
    listSeasons: () => ipcRenderer.invoke('debug:listSeasons'),
    tableCounts: () => ipcRenderer.invoke('debug:tableCounts'),
    seasonGames: (seasonId?: string) => ipcRenderer.invoke('debug:seasonGames', seasonId),
  }
};

// Expose the API to the renderer process
contextBridge.exposeInMainWorld('electronAPI', electronAPI);

// Type definitions for TypeScript
declare global {
  interface Window {
    electronAPI: typeof electronAPI;
  }
}
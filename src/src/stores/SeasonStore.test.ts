// @jest-environment jsdom
import { SeasonStore } from './SeasonStore';

describe('SeasonStore', () => {
  let store: SeasonStore;

  beforeEach(() => {
    store = new SeasonStore();
    // Mock fetch globally
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('calls loadWeekGames after creating a new season', async () => {
    // Mock /api/season/create response
    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({
        json: async () => ({
          success: true,
          season_status: {
            id: 'season-1',
            season_year: 2025,
            current_week: 3,
            current_phase: 'regular',
            total_games: 16,
            completed_games: 0,
            completion_percentage: 0,
            next_games_count: 16,
            weeks_remaining: 14,
            schedule_type: 'standard'
          }
        })
      })
      // Mock /api/season/week response
      .mockResolvedValueOnce({
        json: async () => ({
          success: true,
          games: [{ game_id: 'g1', week: 3 }]
        })
      })
      // Mock loadTeams and loadNextGames (not implemented or not relevant)
      .mockResolvedValue({ json: async () => ({ success: false }) });

    // Spy on loadWeekGames
    const loadWeekGamesSpy = jest.spyOn(store, 'loadWeekGames');

    await store.createSeason(2025);

    expect(loadWeekGamesSpy).toHaveBeenCalledWith(3);
    expect(store.currentWeekGames).toEqual([{ game_id: 'g1', week: 3 }]);
  });
});
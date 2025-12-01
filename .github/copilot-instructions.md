# Copilot Instructions for Football Simulation Engine

This is a comprehensive American football simulation engine built as an **Electron desktop application** with TypeScript services and SQLite for offline usage. When working on this codebase:

## Architecture Overview

### Electron Desktop Application Structure
- **Main Process** (`electron/`): TypeScript services, IPC communication, SQLite database operations
- **Renderer Process** (`src/`): React + TypeScript with Vite, MobX for state management, Tailwind CSS
- **Database** (`electron/database/`): SQLite with better-sqlite3, DAO pattern for local storage
- **Legacy Backend** (`backend/`): **DEPRECATED** - Flask/Python code being phased out

### Core Service Boundaries
- **Season Engine** (`electron/services/season-engine.ts`): Manages full season scheduling, standings, playoffs - **NOT** individual game simulation
- **Game Engine** (`electron/services/game-engine.ts`): Handles individual game play-by-play simulation with weather effects
- **Database Layer** (`electron/database/`): SQLite with better-sqlite3, DAO pattern with transaction management
- **Legacy Python Services** (`backend/simulation/`): **DEPRECATED** - Being replaced by TypeScript services

## Critical Development Workflows

### Electron Desktop Application
```bash
# Full development environment (RECOMMENDED)
npm run dev  # Builds main process + starts renderer on :5173 + launches Electron

# Individual components for debugging
npm run dev:renderer    # React dev server only
npm run dev:electron    # Electron main process only

# Production builds
npm run build           # Build for current platform
npm run dist:all        # Package for Windows/macOS/Linux
```

### Testing Patterns
- **TypeScript Services**: `npm run test:unit` for service layer unit tests
- **Database Tests**: `npm run test:database` for SQLite integration tests
- **Integration Tests**: `npm run test` for full test suite
- **Legacy Python Tests**: `python -m pytest tests/` for deprecated backend (reference only)
- **Demo Scripts**: Legacy `demo_*.py` files available for simulation logic reference

### Key Integration Points
- **Electron IPC**: Use `window.electronAPI.*` in renderer, implement handlers in `electron/ipc/ipc-main.ts`
- **Database Transactions**: Always use SQLite `.transaction()` method via `DatabaseManager`
- **Service Layer**: Implement business logic in `electron/services/`, expose via IPC
- **React Renderer**: Components in `src/` communicate with main process via IPC only

## Project-Specific Patterns

### Simulation Engine Design
- **Deterministic**: All simulations use `random.seed()` for reproducible results
- **Pluggable Schedules**: Use `ScheduleGenerator` base class, implement `generate_schedule()` method
- **Game Flow**: `GameEngine.simulate_game()` → `GameReporter` → detailed play-by-play with drive tracking

### Data Models Convention
```python
# Use dataclasses with type hints
@dataclass
class TeamStats:
    offensive_rating: int = 70  # 0-100 scale
    defensive_rating: int = 70
```

### Database Access Pattern
```typescript
// SQLite (Electron main process)
const db = this.dbManager.getDatabase();
db.transaction((conn) => {
    const result = seasonDao.getSeasonById(conn, seasonId);
})();

// Service layer example
class SeasonService {
    async getSeasonById(seasonId: string): Promise<Season> {
        return this.daoManager.seasonDao.getById(seasonId);
    }
}
```

### API Response Format
- Exhibition games: Return `game_report` dict with play-by-play
- Season operations: Return `season_state` with current standings/schedule
- Always include error handling with meaningful HTTP status codes

## Football Domain Knowledge

### NFL-Accurate Implementation
- **All 32 teams** with realistic 2024-2025 ratings (SF 49ers: 87.5, Panthers: 72.5)
- **Field position tracking**: Drive starts, turnovers, special teams transitions
- **Situational football**: Down/distance/field position affect play calling
- **Red zone efficiency**: Separate ratings for scoring in red zone vs overall offense

### Critical Rating Scales
- Team ratings: 0-100 scale (average ~80, elite teams 85+)
- Weather effects: Temperature, precipitation, wind impact passing/kicking
- Home field advantage: Built into simulation algorithms

## Common Tasks & Examples

### Adding New Features
1. Implement service in `electron/services/` with business logic
2. Add IPC handlers in `electron/ipc/ipc-main.ts` to expose service methods
3. Use `window.electronAPI.*` in renderer components to call services
4. Add tests in `npm run test:unit` for service logic
5. Update DAO layer if new database operations are needed

### Extending Simulation Features
1. Modify `GameEngine` for new mechanics
2. Update `GameReporter` for new event types
3. Add demo script to showcase feature
4. Ensure deterministic behavior with seeds

### Database Schema Changes
1. Update SQLite schema in `electron/database/database-manager.ts`
2. Create migration script in database manager
3. Update corresponding DAO classes in `electron/database/dao/`
4. Test with SQLite database using `npm run test:database`
5. Ensure migrations run automatically on app startup

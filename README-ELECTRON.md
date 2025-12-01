# Football Simulation Engine - Electron Edition

A desktop application version of the Football Simulation Engine, built with Electron, TypeScript, and SQLite for local data storage.

## 🏗️ Architecture Overview

This Electron application transforms the web-based football simulation into a native desktop app with the following key changes:

- **Frontend**: React + TypeScript (minimal changes from web version)
- **Backend**: TypeScript services in Electron main process (replaces Flask)
- **Database**: SQLite with better-sqlite3 (replaces PostgreSQL)
- **Authentication**: Guest mode (no user authentication required)
- **Communication**: IPC (replaces HTTP API calls)

## 📁 Project Structure

```
football-sim-electron/
├── package.json                 # Dependencies and scripts
├── tsconfig.json               # TypeScript config for React
├── tsconfig.electron.json      # TypeScript config for Electron
├── vite.config.electron.ts     # Vite config for renderer
│
├── electron/                   # Main process (Backend)
│   ├── main.ts                # Electron entry point
│   ├── preload.ts             # Secure IPC bridge
│   ├── auto-updater.ts        # Auto-update functionality
│   │
│   ├── database/              # SQLite database layer
│   │   ├── database-manager.ts # SQLite connection management
│   │   └── dao/               # Data access objects
│   │       ├── base-dao.ts    # Base DAO with common operations
│   │       ├── team-dao.ts    # Team data operations
│   │       ├── season-dao.ts  # Season data operations
│   │       ├── game-dao.ts    # Game data operations
│   │       └── dao-manager.ts # Coordinates all DAOs
│   │
│   ├── services/              # Business logic services (to be created)
│   │   ├── team-service.ts    # Team management
│   │   ├── season-service.ts  # Season management
│   │   ├── simulation-service.ts # Game simulation
│   │   └── app-service.ts     # App utilities
│   │
│   └── ipc/                   # IPC communication
│       └── ipc-main.ts        # IPC handlers setup
│
├── src/                       # Renderer process (Frontend)
│   └── (React frontend - to be migrated from existing)
│
└── scripts/                   # Build and development scripts
    └── dev.js                # Development environment script
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn
- Git

### Installation
```bash
# Clone your existing football-sim project
git clone <your-repo-url>
cd football-sim

# Copy the frontend to the new Electron structure
cp -r frontend/src ./src
cp -r frontend/public ./public

# Install dependencies
npm install

# Run the application in development
npm run dev
```

## 🛠️ Development

### Available Commands

| Command | Description |
|---------|-------------|
| `npm run dev` | Start full development environment |
| `npm run dev:renderer` | Start only React dev server |
| `npm run dev:electron` | Start only Electron main process |
| `npm run build` | Build for production |
| `npm run dist` | Package for current platform |
| `npm run dist:all` | Package for all platforms |
| `npm test` | Run tests |
| `npm run lint` | Check code style |

### Development Workflow

1. **Start Development**: `npm run dev`
   - Builds Electron main process
   - Starts Vite dev server on port 5173
   - Launches Electron app
   - Watches for file changes and auto-restarts

2. **Debugging**:
   - **Main Process**: Attach debugger to port 9229
   - **Renderer Process**: Use Chrome DevTools (F12)
   - **Database**: Use SQLite browser extensions

3. **File Watching**: Changes to `electron/**/*` trigger rebuild and restart

## 🗄️ Database Architecture

### SQLite Schema
```sql
-- Teams (NFL teams data)
CREATE TABLE teams (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    abbreviation TEXT UNIQUE NOT NULL,
    conference TEXT CHECK (conference IN ('AFC', 'NFC')),
    division TEXT CHECK (division IN ('North', 'South', 'East', 'West')),
    stats TEXT NOT NULL, -- JSON blob
    created_at TEXT DEFAULT (datetime('now'))
);

-- Seasons (user's simulation seasons)
CREATE TABLE seasons (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    year INTEGER NOT NULL,
    status TEXT DEFAULT 'setup' CHECK (status IN ('setup', 'active', 'completed')),
    current_week INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Season Games (scheduled and completed games)
CREATE TABLE season_games (
    id TEXT PRIMARY KEY,
    season_id TEXT NOT NULL,
    week INTEGER NOT NULL,
    home_team_id TEXT NOT NULL,
    away_team_id TEXT NOT NULL,
    home_score INTEGER,
    away_score INTEGER,
    status TEXT DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'completed')),
    game_data TEXT, -- JSON blob for detailed results
    simulated_at TEXT,
    FOREIGN KEY (season_id) REFERENCES seasons (id),
    FOREIGN KEY (home_team_id) REFERENCES teams (id),
    FOREIGN KEY (away_team_id) REFERENCES teams (id)
);
```

### Data Location
- **Database**: `~/.football-sim/app-data.db`
- **Backups**: `~/.football-sim/backups/`
- **Logs**: `~/.football-sim/logs/`

## 🔧 Key Features

### Implemented ✅
- **Database Layer**: Complete SQLite implementation with DAOs
- **IPC Communication**: Type-safe communication between processes
- **Auto-Migration**: Database schema versioning and automatic updates
- **Data Seeding**: Automatic population of NFL teams and basic player data
- **Development Environment**: Hot-reload development setup

### In Progress 🚧
- **Service Layer**: Business logic services (team, season, simulation)
- **Frontend Integration**: React frontend adapted for IPC
- **Build System**: Production build and packaging

### Planned 📋
- **Game Simulation Engine**: Port from Python to TypeScript
- **Schedule Generation**: NFL-style schedule creation
- **Data Export/Import**: Backup and restore functionality
- **Auto-Updates**: Production update mechanism

## 🔗 IPC API

The app uses Electron IPC for communication between frontend and backend:

### Teams API
```typescript
window.electronAPI.teams.getAll()
window.electronAPI.teams.getById(teamId)
window.electronAPI.teams.compare(team1Id, team2Id)
```

### Seasons API
```typescript
window.electronAPI.seasons.create(seasonData)
window.electronAPI.seasons.getStatus(seasonId)
window.electronAPI.seasons.simulateGame(gameId, options)
```

### Exhibition API
```typescript
window.electronAPI.exhibition.simulate(homeTeamId, awayTeamId, options)
```

## 🎯 Migration Status

### ✅ Completed
- [x] Project structure and configuration
- [x] Database layer (SQLite + DAOs)
- [x] IPC communication framework
- [x] Development environment setup

### 🔄 In Progress
- [ ] Service layer implementation
- [ ] Frontend IPC integration
- [ ] Game simulation engine port

### 📋 Upcoming
- [ ] Build and distribution system
- [ ] Testing and optimization
- [ ] Documentation and deployment

## 🔒 Security

- **Context Isolation**: Enabled for secure IPC communication
- **Node Integration**: Disabled in renderer for security
- **Preload Script**: Secure API exposure to renderer process
- **Local Data**: All data stored locally, no external connections required

## 📦 Distribution

The app will be distributed as:
- **Windows**: NSIS installer + portable executable
- **macOS**: DMG installer + app bundle
- **Linux**: AppImage + deb/rpm packages

## 🤝 Contributing

1. Follow the existing code structure
2. Use TypeScript for all new code
3. Add tests for new functionality
4. Update this README for significant changes

## 📄 License

MIT License - see LICENSE file for details.

---

This Electron version provides the same great football simulation experience as the web version, but with the benefits of a native desktop application: local data storage, offline functionality, and platform integration.
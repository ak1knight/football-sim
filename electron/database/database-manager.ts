import Database from 'better-sqlite3';
import { app } from 'electron';
import * as path from 'path';
import * as fs from 'fs';

export class DatabaseError extends Error {
  constructor(message: string, public readonly cause?: Error) {
    super(message);
    this.name = 'DatabaseError';
  }
}

export class DatabaseManager {
  private db: Database.Database | null = null;
  private dbPath: string;
  private isInitialized = false;

  constructor(customPath?: string) {
    if (customPath) {
      this.dbPath = customPath;
    } else {
      const userDataPath = app.getPath('userData');
      this.dbPath = path.join(userDataPath, 'app-data.db');
    }
  }

  async initialize(): Promise<void> {
    if (this.isInitialized) return;

    try {
      // Ensure the directory exists
      const dbDir = path.dirname(this.dbPath);
      if (!fs.existsSync(dbDir)) {
        fs.mkdirSync(dbDir, { recursive: true });
      }

      // Initialize database connection
      this.db = new Database(this.dbPath);
      
      // Configure SQLite for better performance
      this.db.pragma('journal_mode = WAL');
      this.db.pragma('foreign_keys = ON');
      this.db.pragma('synchronous = NORMAL');
      this.db.pragma('temp_store = MEMORY');
      this.db.pragma('mmap_size = 268435456'); // 256MB

      this.isInitialized = true;
      console.log(`✅ Database initialized at: ${this.dbPath}`);
    } catch (error) {
      throw new DatabaseError(`Failed to initialize database: ${error.message}`, error);
    }
  }

  getDatabase(): Database.Database {
    if (!this.db || !this.isInitialized) {
      throw new DatabaseError('Database not initialized. Call initialize() first.');
    }
    return this.db;
  }

  getDbPath(): string {
    return this.dbPath;
  }

  async runMigrations(): Promise<void> {
    if (!this.db) {
      throw new DatabaseError('Database not initialized');
    }

    try {
      console.log('🔄 Running database migrations...');
      
      // Create schema_version table if it doesn't exist
      this.db.exec(`
        CREATE TABLE IF NOT EXISTS schema_version (
          version INTEGER PRIMARY KEY,
          applied_at TEXT DEFAULT (datetime('now')),
          description TEXT
        )
      `);

      // Get current schema version
      const currentVersion = this.getCurrentSchemaVersion();
      console.log(`📊 Current schema version: ${currentVersion}`);

      // Apply migrations
      const migrations = this.getMigrations();
      for (const migration of migrations) {
        if (migration.version > currentVersion) {
          console.log(`⬆️  Applying migration ${migration.version}: ${migration.description}`);
          
          const transaction = this.db.transaction(() => {
            migration.up(this.db!);
            
            // Record migration
            this.db!.prepare(`
              INSERT INTO schema_version (version, description) 
              VALUES (?, ?)
            `).run(migration.version, migration.description);
          });
          
          transaction();
          console.log(`✅ Migration ${migration.version} applied successfully`);
        }
      }

      console.log('✅ Database migrations complete');
    } catch (error) {
      throw new DatabaseError(`Migration failed: ${error.message}`, error);
    }
  }

  async seedInitialData(): Promise<void> {
    if (!this.db) {
      throw new DatabaseError('Database not initialized');
    }

    try {
      // Check if we already have teams data
      const teamCount = this.db.prepare('SELECT COUNT(*) as count FROM teams').get() as { count: number };
      
      if (teamCount.count === 0) {
        console.log('🌱 Seeding initial data...');
        await this.seedNFLTeams();
        await this.seedNFLPlayers();
        console.log('✅ Initial data seeding complete');
      } else {
        console.log('📊 Database already contains data, skipping seed');
      }
    } catch (error) {
      throw new DatabaseError(`Data seeding failed: ${error.message}`, error);
    }
  }

  private getCurrentSchemaVersion(): number {
    try {
      const result = this.db!.prepare('SELECT MAX(version) as version FROM schema_version').get() as { version: number | null };
      return result.version || 0;
    } catch (error) {
      // Table doesn't exist yet
      return 0;
    }
  }

  private getMigrations() {
    return [
      {
        version: 1,
        description: 'Create initial tables',
        up: (db: Database.Database) => {
          db.exec(`
            -- Teams table
            CREATE TABLE teams (
              id TEXT PRIMARY KEY,
              name TEXT NOT NULL,
              city TEXT NOT NULL,
              abbreviation TEXT UNIQUE NOT NULL,
              conference TEXT CHECK (conference IN ('AFC', 'NFC')) NOT NULL,
              division TEXT CHECK (division IN ('North', 'South', 'East', 'West')) NOT NULL,
              stats TEXT NOT NULL, -- JSON blob
              created_at TEXT DEFAULT (datetime('now'))
            );

            -- Players table
            CREATE TABLE players (
              id TEXT PRIMARY KEY,
              team_id TEXT NOT NULL,
              name TEXT NOT NULL,
              position TEXT NOT NULL,
              jersey_number INTEGER,
              stats TEXT NOT NULL, -- JSON blob
              created_at TEXT DEFAULT (datetime('now')),
              FOREIGN KEY (team_id) REFERENCES teams (id) ON DELETE CASCADE
            );

            -- Seasons table
            CREATE TABLE seasons (
              id TEXT PRIMARY KEY,
              name TEXT NOT NULL,
              year INTEGER NOT NULL,
              status TEXT DEFAULT 'setup' CHECK (status IN ('setup', 'active', 'completed')),
              current_week INTEGER DEFAULT 1,
              created_at TEXT DEFAULT (datetime('now')),
              updated_at TEXT DEFAULT (datetime('now'))
            );

            -- Season games table
            CREATE TABLE season_games (
              id TEXT PRIMARY KEY,
              season_id TEXT NOT NULL,
              week INTEGER NOT NULL,
              home_team_id TEXT NOT NULL,
              away_team_id TEXT NOT NULL,
              home_score INTEGER,
              away_score INTEGER,
              status TEXT DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'completed', 'simulated')),
              game_data TEXT, -- JSON blob for detailed results
              simulated_at TEXT,
              FOREIGN KEY (season_id) REFERENCES seasons (id) ON DELETE CASCADE,
              FOREIGN KEY (home_team_id) REFERENCES teams (id),
              FOREIGN KEY (away_team_id) REFERENCES teams (id)
            );

            -- App settings table
            CREATE TABLE app_settings (
              key TEXT PRIMARY KEY,
              value TEXT NOT NULL,
              updated_at TEXT DEFAULT (datetime('now'))
            );

            -- Create indexes for performance
            CREATE INDEX idx_teams_conference_division ON teams (conference, division);
            CREATE INDEX idx_players_team_id ON players (team_id);
            CREATE INDEX idx_players_position ON players (position);
            CREATE INDEX idx_season_games_season_week ON season_games (season_id, week);
            CREATE INDEX idx_season_games_teams ON season_games (home_team_id, away_team_id);
            CREATE INDEX idx_season_games_status ON season_games (status);
          `);
        }
      }
    ];
  }

  private async seedNFLTeams(): Promise<void> {
    const teams = this.getNFLTeamsData();
    const insertTeam = this.db!.prepare(`
      INSERT INTO teams (id, name, city, abbreviation, conference, division, stats)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `);

    const transaction = this.db!.transaction((teams: any[]) => {
      for (const team of teams) {
        insertTeam.run(
          team.id,
          team.name,
          team.city,
          team.abbreviation,
          team.conference,
          team.division,
          JSON.stringify(team.stats)
        );
      }
    });

    transaction(teams);
    console.log(`✅ Seeded ${teams.length} NFL teams`);
  }

  private async seedNFLPlayers(): Promise<void> {
    // For now, we'll create basic player data
    // In a real implementation, this would load from a comprehensive player database
    const teams = this.db!.prepare('SELECT id, abbreviation FROM teams').all();
    
    const insertPlayer = this.db!.prepare(`
      INSERT INTO players (id, team_id, name, position, jersey_number, stats)
      VALUES (?, ?, ?, ?, ?, ?)
    `);

    const transaction = this.db!.transaction(() => {
      let playerId = 1;
      
      for (const team of teams) {
        // Create basic roster for each team
        const positions = [
          { pos: 'QB', count: 3, start: 1 },
          { pos: 'RB', count: 4, start: 20 },
          { pos: 'WR', count: 6, start: 10 },
          { pos: 'TE', count: 3, start: 80 },
          { pos: 'OL', count: 8, start: 60 },
          { pos: 'DL', count: 6, start: 90 },
          { pos: 'LB', count: 6, start: 50 },
          { pos: 'CB', count: 5, start: 20 },
          { pos: 'S', count: 4, start: 30 },
          { pos: 'K', count: 1, start: 2 },
          { pos: 'P', count: 1, start: 4 }
        ];

        for (const posGroup of positions) {
          for (let i = 0; i < posGroup.count; i++) {
            const playerStats = {
              overall_rating: Math.floor(Math.random() * 30) + 60, // 60-89
              position_rating: Math.floor(Math.random() * 40) + 60
            };

            insertPlayer.run(
              `player_${playerId}`,
              team.id,
              `${posGroup.pos} Player ${i + 1}`,
              posGroup.pos,
              posGroup.start + i,
              JSON.stringify(playerStats)
            );
            
            playerId++;
          }
        }
      }
    });

    transaction();
    console.log(`✅ Seeded basic player rosters for all teams`);
  }

  private getNFLTeamsData() {
    // This is the same team data from your existing system
    return [
      // AFC East
      { id: 'buf', name: 'Bills', city: 'Buffalo', abbreviation: 'BUF', conference: 'AFC', division: 'East', stats: { offensive_rating: 86, defensive_rating: 83, special_teams_rating: 78, coaching_rating: 85, home_field_advantage: 3 }},
      { id: 'mia', name: 'Dolphins', city: 'Miami', abbreviation: 'MIA', conference: 'AFC', division: 'East', stats: { offensive_rating: 82, defensive_rating: 79, special_teams_rating: 75, coaching_rating: 78, home_field_advantage: 2 }},
      { id: 'ne', name: 'Patriots', city: 'New England', abbreviation: 'NE', conference: 'AFC', division: 'East', stats: { offensive_rating: 76, defensive_rating: 81, special_teams_rating: 82, coaching_rating: 82, home_field_advantage: 4 }},
      { id: 'nyj', name: 'Jets', city: 'New York', abbreviation: 'NYJ', conference: 'AFC', division: 'East', stats: { offensive_rating: 75, defensive_rating: 84, special_teams_rating: 77, coaching_rating: 74, home_field_advantage: 2 }},
      
      // AFC North  
      { id: 'bal', name: 'Ravens', city: 'Baltimore', abbreviation: 'BAL', conference: 'AFC', division: 'North', stats: { offensive_rating: 87, defensive_rating: 85, special_teams_rating: 83, coaching_rating: 88, home_field_advantage: 4 }},
      { id: 'cin', name: 'Bengals', city: 'Cincinnati', abbreviation: 'CIN', conference: 'AFC', division: 'North', stats: { offensive_rating: 84, defensive_rating: 78, special_teams_rating: 76, coaching_rating: 80, home_field_advantage: 2 }},
      { id: 'cle', name: 'Browns', city: 'Cleveland', abbreviation: 'CLE', conference: 'AFC', division: 'North', stats: { offensive_rating: 77, defensive_rating: 82, special_teams_rating: 79, coaching_rating: 76, home_field_advantage: 3 }},
      { id: 'pit', name: 'Steelers', city: 'Pittsburgh', abbreviation: 'PIT', conference: 'AFC', division: 'North', stats: { offensive_rating: 79, defensive_rating: 86, special_teams_rating: 81, coaching_rating: 84, home_field_advantage: 5 }},
      
      // AFC South
      { id: 'hou', name: 'Texans', city: 'Houston', abbreviation: 'HOU', conference: 'AFC', division: 'South', stats: { offensive_rating: 81, defensive_rating: 76, special_teams_rating: 74, coaching_rating: 78, home_field_advantage: 2 }},
      { id: 'ind', name: 'Colts', city: 'Indianapolis', abbreviation: 'IND', conference: 'AFC', division: 'South', stats: { offensive_rating: 78, defensive_rating: 80, special_teams_rating: 77, coaching_rating: 79, home_field_advantage: 2 }},
      { id: 'jax', name: 'Jaguars', city: 'Jacksonville', abbreviation: 'JAX', conference: 'AFC', division: 'South', stats: { offensive_rating: 76, defensive_rating: 75, special_teams_rating: 73, coaching_rating: 74, home_field_advantage: 1 }},
      { id: 'ten', name: 'Titans', city: 'Tennessee', abbreviation: 'TEN', conference: 'AFC', division: 'South', stats: { offensive_rating: 73, defensive_rating: 77, special_teams_rating: 75, coaching_rating: 72, home_field_advantage: 2 }},
      
      // AFC West
      { id: 'den', name: 'Broncos', city: 'Denver', abbreviation: 'DEN', conference: 'AFC', division: 'West', stats: { offensive_rating: 79, defensive_rating: 84, special_teams_rating: 78, coaching_rating: 81, home_field_advantage: 4 }},
      { id: 'kc', name: 'Chiefs', city: 'Kansas City', abbreviation: 'KC', conference: 'AFC', division: 'West', stats: { offensive_rating: 91, defensive_rating: 83, special_teams_rating: 85, coaching_rating: 90, home_field_advantage: 5 }},
      { id: 'lv', name: 'Raiders', city: 'Las Vegas', abbreviation: 'LV', conference: 'AFC', division: 'West', stats: { offensive_rating: 76, defensive_rating: 74, special_teams_rating: 72, coaching_rating: 73, home_field_advantage: 1 }},
      { id: 'lac', name: 'Chargers', city: 'Los Angeles', abbreviation: 'LAC', conference: 'AFC', division: 'West', stats: { offensive_rating: 83, defensive_rating: 79, special_teams_rating: 76, coaching_rating: 80, home_field_advantage: 1 }},

      // NFC East
      { id: 'dal', name: 'Cowboys', city: 'Dallas', abbreviation: 'DAL', conference: 'NFC', division: 'East', stats: { offensive_rating: 85, defensive_rating: 82, special_teams_rating: 80, coaching_rating: 83, home_field_advantage: 3 }},
      { id: 'nyg', name: 'Giants', city: 'New York', abbreviation: 'NYG', conference: 'NFC', division: 'East', stats: { offensive_rating: 74, defensive_rating: 78, special_teams_rating: 76, coaching_rating: 76, home_field_advantage: 2 }},
      { id: 'phi', name: 'Eagles', city: 'Philadelphia', abbreviation: 'PHI', conference: 'NFC', division: 'East', stats: { offensive_rating: 88, defensive_rating: 81, special_teams_rating: 83, coaching_rating: 86, home_field_advantage: 4 }},
      { id: 'was', name: 'Commanders', city: 'Washington', abbreviation: 'WAS', conference: 'NFC', division: 'East', stats: { offensive_rating: 80, defensive_rating: 77, special_teams_rating: 74, coaching_rating: 78, home_field_advantage: 2 }},

      // NFC North
      { id: 'chi', name: 'Bears', city: 'Chicago', abbreviation: 'CHI', conference: 'NFC', division: 'North', stats: { offensive_rating: 77, defensive_rating: 80, special_teams_rating: 78, coaching_rating: 76, home_field_advantage: 3 }},
      { id: 'det', name: 'Lions', city: 'Detroit', abbreviation: 'DET', conference: 'NFC', division: 'North', stats: { offensive_rating: 89, defensive_rating: 76, special_teams_rating: 79, coaching_rating: 85, home_field_advantage: 3 }},
      { id: 'gb', name: 'Packers', city: 'Green Bay', abbreviation: 'GB', conference: 'NFC', division: 'North', stats: { offensive_rating: 84, defensive_rating: 79, special_teams_rating: 81, coaching_rating: 87, home_field_advantage: 5 }},
      { id: 'min', name: 'Vikings', city: 'Minnesota', abbreviation: 'MIN', conference: 'NFC', division: 'North', stats: { offensive_rating: 82, defensive_rating: 77, special_teams_rating: 75, coaching_rating: 79, home_field_advantage: 2 }},

      // NFC South
      { id: 'atl', name: 'Falcons', city: 'Atlanta', abbreviation: 'ATL', conference: 'NFC', division: 'South', stats: { offensive_rating: 81, defensive_rating: 75, special_teams_rating: 73, coaching_rating: 77, home_field_advantage: 2 }},
      { id: 'car', name: 'Panthers', city: 'Carolina', abbreviation: 'CAR', conference: 'NFC', division: 'South', stats: { offensive_rating: 72, defensive_rating: 76, special_teams_rating: 74, coaching_rating: 71, home_field_advantage: 1 }},
      { id: 'no', name: 'Saints', city: 'New Orleans', abbreviation: 'NO', conference: 'NFC', division: 'South', stats: { offensive_rating: 78, defensive_rating: 83, special_teams_rating: 80, coaching_rating: 81, home_field_advantage: 4 }},
      { id: 'tb', name: 'Buccaneers', city: 'Tampa Bay', abbreviation: 'TB', conference: 'NFC', division: 'South', stats: { offensive_rating: 83, defensive_rating: 78, special_teams_rating: 77, coaching_rating: 82, home_field_advantage: 2 }},

      // NFC West
      { id: 'ari', name: 'Cardinals', city: 'Arizona', abbreviation: 'ARI', conference: 'NFC', division: 'West', stats: { offensive_rating: 75, defensive_rating: 73, special_teams_rating: 71, coaching_rating: 74, home_field_advantage: 1 }},
      { id: 'la', name: 'Rams', city: 'Los Angeles', abbreviation: 'LA', conference: 'NFC', division: 'West', stats: { offensive_rating: 80, defensive_rating: 81, special_teams_rating: 78, coaching_rating: 83, home_field_advantage: 2 }},
      { id: 'sf', name: '49ers', city: 'San Francisco', abbreviation: 'SF', conference: 'NFC', division: 'West', stats: { offensive_rating: 87, defensive_rating: 88, special_teams_rating: 84, coaching_rating: 89, home_field_advantage: 3 }},
      { id: 'sea', name: 'Seahawks', city: 'Seattle', abbreviation: 'SEA', conference: 'NFC', division: 'West', stats: { offensive_rating: 82, defensive_rating: 80, special_teams_rating: 79, coaching_rating: 81, home_field_advantage: 5 }}
    ];
  }

  async close(): Promise<void> {
    if (this.db) {
      this.db.close();
      this.db = null;
      this.isInitialized = false;
      console.log('📫 Database connection closed');
    }
  }

  // Test connection
  testConnection(): boolean {
    try {
      if (!this.db) return false;
      this.db.prepare('SELECT 1').get();
      return true;
    } catch (error) {
      console.error('Database connection test failed:', error);
      return false;
    }
  }

  // Backup functionality
  async createBackup(backupPath: string): Promise<void> {
    if (!this.db) {
      throw new DatabaseError('Database not initialized');
    }

    try {
      this.db.backup(backupPath);
      console.log(`✅ Database backed up to: ${backupPath}`);
    } catch (error) {
      throw new DatabaseError(`Backup failed: ${error.message}`, error);
    }
  }
}
-- Football Simulation Database Initialization Script
-- This script creates the core database structure for the football simulation application

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom types
CREATE TYPE season_phase AS ENUM ('regular_season', 'playoffs', 'offseason', 'complete');
CREATE TYPE game_status AS ENUM ('scheduled', 'in_progress', 'completed', 'cancelled');
CREATE TYPE playoff_round AS ENUM ('wild_card', 'divisional', 'conference_championship', 'super_bowl');

-- Users table for authentication and user management
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Teams table - stores base NFL team information
CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    abbreviation VARCHAR(10) UNIQUE NOT NULL,
    conference VARCHAR(10) NOT NULL CHECK (conference IN ('AFC', 'NFC')),
    division VARCHAR(20) NOT NULL CHECK (division IN ('East', 'West', 'North', 'South')),
    team_stats JSONB NOT NULL DEFAULT '{}',
    logo_url VARCHAR(255),
    primary_color VARCHAR(7),
    secondary_color VARCHAR(7),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Players table - stores player information
CREATE TABLE players (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    team_id UUID REFERENCES teams(id) ON DELETE SET NULL,
    name VARCHAR(100) NOT NULL,
    position VARCHAR(20) NOT NULL,
    jersey_number INTEGER CHECK (jersey_number BETWEEN 1 AND 99),
    age INTEGER CHECK (age BETWEEN 18 AND 45),
    years_pro INTEGER DEFAULT 0,
    player_stats JSONB NOT NULL DEFAULT '{}',
    injury_status BOOLEAN DEFAULT FALSE,
    contract_details JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(team_id, jersey_number)
);

-- User leagues - allows users to create custom leagues
CREATE TABLE user_leagues (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    settings JSONB NOT NULL DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Seasons table - user-specific seasons
CREATE TABLE seasons (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    league_id UUID REFERENCES user_leagues(id) ON DELETE SET NULL,
    season_year INTEGER NOT NULL,
    name VARCHAR(200) NOT NULL,
    current_week INTEGER DEFAULT 1,
    phase season_phase DEFAULT 'regular_season',
    settings JSONB NOT NULL DEFAULT '{}',
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Season teams - teams participating in a specific season
CREATE TABLE season_teams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    season_id UUID NOT NULL REFERENCES seasons(id) ON DELETE CASCADE,
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    ties INTEGER DEFAULT 0,
    points_for INTEGER DEFAULT 0,
    points_against INTEGER DEFAULT 0,
    division_wins INTEGER DEFAULT 0,
    conference_wins INTEGER DEFAULT 0,
    season_stats JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(season_id, team_id)
);

-- Season games - all games in a season (regular season + playoffs)
CREATE TABLE season_games (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    season_id UUID NOT NULL REFERENCES seasons(id) ON DELETE CASCADE,
    game_id VARCHAR(100) NOT NULL, -- semantic ID like "2024_W01_G001"
    week INTEGER,
    playoff_round playoff_round,
    home_team_id UUID NOT NULL REFERENCES teams(id),
    away_team_id UUID NOT NULL REFERENCES teams(id),
    home_score INTEGER DEFAULT 0,
    away_score INTEGER DEFAULT 0,
    status game_status DEFAULT 'scheduled',
    game_date TIMESTAMP WITH TIME ZONE,
    weather_conditions JSONB DEFAULT '{}',
    game_data JSONB DEFAULT '{}', -- detailed simulation data
    play_by_play JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(season_id, game_id)
);

-- Game stats - individual player/team statistics for games
CREATE TABLE game_stats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    game_id UUID NOT NULL REFERENCES season_games(id) ON DELETE CASCADE,
    team_id UUID NOT NULL REFERENCES teams(id),
    player_id UUID REFERENCES players(id) ON DELETE SET NULL,
    stat_type VARCHAR(50) NOT NULL, -- 'passing', 'rushing', 'receiving', etc.
    stat_data JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Playoff brackets - stores playoff bracket information
CREATE TABLE playoff_brackets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    season_id UUID NOT NULL REFERENCES seasons(id) ON DELETE CASCADE,
    bracket_data JSONB NOT NULL DEFAULT '{}',
    current_round playoff_round DEFAULT 'wild_card',
    afc_champion_id UUID REFERENCES teams(id),
    nfc_champion_id UUID REFERENCES teams(id),
    super_bowl_champion_id UUID REFERENCES teams(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(season_id)
);

-- User sessions - for authentication management
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = TRUE;

CREATE INDEX idx_teams_abbreviation ON teams(abbreviation);
CREATE INDEX idx_teams_conference_division ON teams(conference, division);

CREATE INDEX idx_players_team_id ON players(team_id);
CREATE INDEX idx_players_position ON players(position);
CREATE INDEX idx_players_jersey ON players(team_id, jersey_number);

CREATE INDEX idx_seasons_user_id ON seasons(user_id);
CREATE INDEX idx_seasons_year ON seasons(season_year);
CREATE INDEX idx_seasons_phase ON seasons(phase);

CREATE INDEX idx_season_teams_season_id ON season_teams(season_id);
CREATE INDEX idx_season_teams_team_id ON season_teams(team_id);
CREATE INDEX idx_season_teams_record ON season_teams(wins, losses, ties);

CREATE INDEX idx_season_games_season_id ON season_games(season_id);
CREATE INDEX idx_season_games_week ON season_games(week);
CREATE INDEX idx_season_games_status ON season_games(status);
CREATE INDEX idx_season_games_teams ON season_games(home_team_id, away_team_id);
CREATE INDEX idx_season_games_date ON season_games(game_date);

CREATE INDEX idx_game_stats_game_id ON game_stats(game_id);
CREATE INDEX idx_game_stats_team_id ON game_stats(team_id);
CREATE INDEX idx_game_stats_player_id ON game_stats(player_id);

CREATE INDEX idx_playoff_brackets_season_id ON playoff_brackets(season_id);

CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_token ON user_sessions(token_hash);
CREATE INDEX idx_user_sessions_expires ON user_sessions(expires_at);

-- Create GIN indexes for JSONB columns
CREATE INDEX idx_teams_stats_gin ON teams USING GIN (team_stats);
CREATE INDEX idx_players_stats_gin ON players USING GIN (player_stats);
CREATE INDEX idx_season_games_data_gin ON season_games USING GIN (game_data);
CREATE INDEX idx_game_stats_data_gin ON game_stats USING GIN (stat_data);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_teams_updated_at BEFORE UPDATE ON teams FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_players_updated_at BEFORE UPDATE ON players FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_seasons_updated_at BEFORE UPDATE ON seasons FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_season_teams_updated_at BEFORE UPDATE ON season_teams FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_season_games_updated_at BEFORE UPDATE ON season_games FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_leagues_updated_at BEFORE UPDATE ON user_leagues FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_playoff_brackets_updated_at BEFORE UPDATE ON playoff_brackets FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
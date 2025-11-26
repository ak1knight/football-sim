# Copilot Instructions for Football Simulation Engine

This is a comprehensive American football simulation engine with a Python Flask backend, React TypeScript frontend, and PostgreSQL database. When working on this codebase:

## Architecture Overview

### Full-Stack Structure
- **`backend/`**: Flask API server with SQLAlchemy, organized into blueprints (`/api/exhibition`, `/api/season`, `/api/teams`)
- **`frontend/`**: React + TypeScript with Vite, MobX for state management, Tailwind CSS
- **`database/`**: PostgreSQL with SQLAlchemy Core, DAO pattern for data access
- **Deployment**: Docker Compose setup with separate dev/test databases

### Core Service Boundaries
- **Season Engine** (`simulation/season_engine.py`): Manages full season scheduling, standings, playoffs - **NOT** individual game simulation
- **Game Engine** (`simulation/game_engine.py`): Handles individual game play-by-play simulation with weather effects
- **Database Layer** (`database/dao/`): DAO pattern with transaction management via `DatabaseManager` context managers

## Critical Development Workflows

### Running the Application
```bash
# Backend (Flask API on :5000)
cd backend && python app.py

# Frontend (React dev server on :5173) 
cd frontend && npm run dev

# Database (PostgreSQL on :5432)
docker-compose up postgres
```

### Testing Patterns
- **Unit tests**: `python -m pytest tests/` (49+ tests, 100% pass rate required)
- **Demo scripts**: Run `demo_*.py` files to see features in action before coding
- **Database tests**: Use separate test containers via `docker-compose up postgres-test`

### Key Integration Points
- **API Blueprints**: Register in `app.py` with URL prefixes (`/api/exhibition`, `/api/season`)
- **Database Transactions**: Always use `DatabaseManager.transaction()` context manager
- **CORS**: Frontend runs on :5173, backend expects requests from this origin

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
```python
# Always use transaction context managers
with db_manager.transaction() as conn:
    result = season_dao.get_season_by_id(conn, season_id)
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

### Adding New API Endpoints
1. Create blueprint in `api/` directory
2. Register in `app.py` with URL prefix  
3. Use DAO pattern for database access
4. Add corresponding tests in `tests/test_api.py`

### Extending Simulation Features
1. Modify `GameEngine` for new mechanics
2. Update `GameReporter` for new event types
3. Add demo script to showcase feature
4. Ensure deterministic behavior with seeds

### Database Schema Changes
1. Update `database/schema.py`
2. Create migration in `database/migrations.py`
3. Update corresponding DAO classes
4. Test with both dev and test databases

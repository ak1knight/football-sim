# American Football Simulation Engine

A comprehensive Python-based simulation engine for American football that models team statistics, player abilities, and game outcomes. Designed with a clean API architecture for easy integration with React frontends.

## Features

- **Realistic Game Simulation**: Models NFL-style gameplay with team and player statistics
- **Team Management**: Complete roster management with player positions and ratings
- **Statistical Analysis**: Offensive, defensive, and special teams ratings
- **API Ready**: REST API endpoints designed for React frontend integration
- **Extensible Design**: Easy to add new features, sports, or leagues
- **Comprehensive Testing**: Full unit test coverage for all components

## Project Structure

```
football-sim/
├── main.py                 # Main entry point and demo
├── models/                 # Data models
│   ├── player.py          # Player class with stats and positions
│   └── team.py            # Team class with roster and ratings
├── simulation/             # Game simulation engine
│   └── game_engine.py     # Core simulation logic
├── data/                   # Data management
│   └── team_loader.py     # Sample data and data loading utilities
├── api/                    # REST API (future React integration)
│   ├── simulation_api.py  # Game simulation endpoints
│   └── team_api.py        # Team management endpoints
├── tests/                  # Unit tests
│   ├── test_models.py     # Tests for data models
│   ├── test_simulation.py # Tests for game engine
│   └── test_api.py        # Tests for API endpoints
└── requirements.txt        # Python dependencies
```

## Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run a Simulation

```bash
python main.py
```

This will run a demonstration game between two sample teams and display the results.

### 3. Run Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=.

# Run specific test file
python -m pytest tests/test_simulation.py -v
```

## Usage Examples

### Basic Game Simulation

```python
from models.team import Team, TeamStats
from simulation.game_engine import GameEngine
from data.team_loader import load_sample_teams

# Load sample teams
teams = load_sample_teams()
home_team = teams[0]  # Philadelphia Eagles
away_team = teams[1]  # Dallas Cowboys

# Create game engine
engine = GameEngine(seed=42)  # Use seed for reproducible results

# Simulate the game
result = engine.simulate_game(home_team, away_team)

print(f"Final Score: {result.away_team.name} {result.away_score} - {result.home_team.name} {result.home_score}")
if result.winner:
    print(f"Winner: {result.winner.name}")
```

### API Usage (Future React Integration)

```python
from api.simulation_api import SimulationAPI
from api.team_api import TeamAPI

# Initialize APIs
sim_api = SimulationAPI()
team_api = TeamAPI()

# Get all teams
teams_response = team_api.get_all_teams()
print(f"Available teams: {len(teams_response['teams'])}")

# Simulate a game
game_result = sim_api.simulate_game("PHI", "DAL")
print(f"Game result: {game_result['summary']}")

# Get team comparison
comparison = team_api.compare_teams("PHI", "DAL")
print(f"Overall rating advantage: {comparison['comparison']['overall_rating']['advantage']}")
```

### Creating Custom Teams

```python
from models.team import Team, TeamStats
from models.player import Player, Position, PlayerStats

# Create custom team
team_stats = TeamStats(
    offensive_rating=85,
    defensive_rating=80,
    coaching_rating=78
)

custom_team = Team(
    name="Wildcats",
    city="Springfield", 
    abbreviation="SPR",
    conference="NFC",
    division="North",
    stats=team_stats
)

# Add players
qb_stats = PlayerStats(
    overall_rating=88,
    passing_accuracy=90,
    passing_power=85,
    awareness=87
)

quarterback = Player(
    name="John Smith",
    position=Position.QB,
    jersey_number=12,
    stats=qb_stats,
    age=28
)

custom_team.add_player(quarterback)
```

## Game Simulation Details

### Team Ratings

Each team has comprehensive ratings that affect simulation outcomes:

- **Offensive Ratings**: Overall offense, passing, rushing, red zone efficiency
- **Defensive Ratings**: Overall defense, pass defense, run defense, red zone defense  
- **Special Teams**: Kicking game, return game
- **Coaching**: Overall coaching rating, discipline, conditioning
- **Home Field Advantage**: Point bonus when playing at home

### Player Positions

The simulation supports all major NFL positions:

- **Offense**: QB, RB, WR, TE, OL
- **Defense**: DL, LB, CB, S
- **Special Teams**: K, P

### Simulation Features

- **Realistic Scoring**: Touchdowns (7 pts), field goals (3 pts), safeties (2 pts)
- **Drive Outcomes**: Touchdowns, field goals, punts, turnovers, missed field goals
- **Game Flow**: 4 quarters of 15 minutes each, with overtime handling
- **Statistical Factors**: Team ratings influence drive success probability
- **Home Field Advantage**: Home teams receive rating bonuses
- **Reproducible Results**: Use seeds for consistent outcomes in testing

## API Endpoints (Future React Integration)

### Simulation API

- `simulate_game(home_team_id, away_team_id, seed=None)` - Simulate a single game
- `get_simulation_history(limit=10)` - Get recent simulation results
- `simulate_season(team_ids, games_per_team=16)` - Simulate multiple games

### Team API

- `get_all_teams()` - Get all available teams
- `get_team_details(team_id)` - Get detailed team information
- `get_team_roster(team_id)` - Get complete team roster
- `get_team_stats(team_id)` - Get team ratings and statistics
- `compare_teams(team1_id, team2_id)` - Compare two teams side by side

## Development

### Code Style

This project follows PEP 8 style guidelines and uses type hints throughout:

```bash
# Format code
black .

# Check style
flake8 .

# Type checking
mypy .
```

### Testing

Comprehensive unit tests cover all major components:

```bash
# Run all tests with verbose output
python -m pytest tests/ -v

# Run tests with coverage report
python -m pytest tests/ --cov=. --cov-report=html

# Run specific test categories
python -m pytest tests/test_models.py -v      # Data model tests
python -m pytest tests/test_simulation.py -v # Simulation engine tests
python -m pytest tests/test_api.py -v        # API tests
```

### Adding New Features

The modular design makes it easy to extend:

1. **New Sports**: Create new models and simulation engines
2. **Advanced Statistics**: Add more detailed player and team stats
3. **Play-by-Play**: Extend simulation engine for detailed game events
4. **Machine Learning**: Integrate ML models for more realistic outcomes
5. **Web Interface**: Connect API to React frontend

## Future Enhancements

- **React Frontend**: Web interface for team management and simulations
- **Database Integration**: Persistent storage for teams and game history
- **Advanced Analytics**: More detailed statistics and trend analysis
- **League Management**: Season scheduling, playoffs, and championships
- **Real Data Integration**: Import actual NFL team and player statistics
- **Machine Learning**: Use historical data to improve simulation accuracy

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run the test suite (`python -m pytest tests/`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Contact

For questions or suggestions, please open an issue on GitHub.

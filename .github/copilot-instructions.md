# Copilot Instructions for Football Simulation Engine

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

This is a Python-based American football simulation engine project. When working on this codebase:

## Project Structure
- **simulation/**: Core simulation engine and game logic
- **models/**: Team, player, and statistical models
- **data/**: Team and player data files
- **api/**: API endpoints for future React frontend integration
- **tests/**: Unit tests for all components

## Code Style Guidelines
- Use type hints for all function parameters and return values
- Follow PEP 8 style guidelines
- Use dataclasses for structured data like Player and Team
- Implement comprehensive logging for simulation events
- Use numpy and pandas for statistical calculations
- Design the API with REST principles for frontend integration

## Football Domain Knowledge
- Focus on realistic NFL-style statistics and gameplay
- Consider factors like home field advantage, weather, injuries
- Implement both offensive and defensive team statistics
- Use historical data patterns for realistic simulation outcomes
- Model key game events: turnovers, touchdowns, field goals, etc.

## Architecture Principles
- Keep simulation logic separate from data models
- Design for extensibility (different sports, leagues)
- Ensure the simulation engine is deterministic with seed values
- Build API endpoints that can easily connect to a React frontend

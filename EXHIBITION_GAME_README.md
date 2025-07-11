# Football Simulation - Exhibition Game Feature

## Overview

The Exhibition Game feature allows users to simulate individual football games between any two teams with customizable weather conditions. This is built as a React frontend with a Python Flask backend API.

## Features

### 🏈 Team Selection
- Select any two teams from a comprehensive NFL-style team roster
- Clear visual distinction between home and away teams
- Prevents selecting the same team twice

### 🌤️ Weather Controls
- **Condition**: Choose from Clear, Cloudy, Rainy, Snowy, or Windy weather
- **Temperature**: Set temperature from 0°F to 120°F
- **Wind Speed**: Configure wind from 0 to 50 mph
- **Wind Direction**: 8-directional wind (N, NE, E, SE, S, SW, W, NW)

### 📊 Game Results
- **Live Score Display**: Real-time final scores for both teams
- **Winner Determination**: Automatic winner calculation with margin of victory
- **Game Duration**: Total game time tracking
- **Overtime Support**: Handles overtime scenarios
- **Weather Impact**: Shows how weather affected the game

### 📈 Detailed Statistics (Optional)
- Total plays count
- Turnovers by team
- Penalties by team  
- Time of possession breakdown

### 🎯 Key Plays
- Highlights of important scoring plays and game-changing moments
- Quarter and time stamps for each play
- Special indicators for scoring plays

## Architecture

### Backend (Python Flask)
- **Location**: `backend/`
- **Main File**: `app.py`
- **API Endpoint**: `/api/exhibition/`
- **Port**: 5000

Key files:
- `api/exhibition_api.py`: Exhibition game API endpoints
- `models/weather.py`: Weather condition models
- `simulation/game_engine.py`: Core game simulation logic
- `data/team_loader.py`: Team data management

### Frontend (React + TypeScript)
- **Location**: `frontend/`
- **Main Component**: `ExhibitionGame.tsx`
- **Port**: 5173 (Vite dev server)

Key files:
- `src/components/ExhibitionGame.tsx`: Main UI component
- `src/components/ExhibitionGame.css`: Styling
- `src/types/api.ts`: TypeScript type definitions
- `src/services/api.ts`: API communication layer

## How to Run

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python app.py
```

Backend will be available at `http://localhost:5000`

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at `http://localhost:5173`

## Usage Instructions

1. **Open the Application**: Navigate to `http://localhost:5173` in your browser

2. **Select Teams**: 
   - Choose an away team from the first dropdown
   - Choose a home team from the second dropdown
   - Teams must be different

3. **Configure Weather**:
   - Select weather condition (affects gameplay)
   - Set temperature (extreme temperatures impact performance)
   - Configure wind speed and direction (affects passing and kicking)

4. **Game Options**:
   - Toggle "Show detailed statistics" for extra game data

5. **Simulate Game**: Click "🏈 Simulate Game" button

6. **View Results**:
   - See final scores and winner
   - Review weather impact
   - Explore detailed statistics and key plays

## Weather Effects on Gameplay

The simulation incorporates realistic weather effects:

- **Cold Weather**: Reduces passing accuracy and kicking precision, increases fumbles
- **Hot Weather**: Slightly reduces rushing effectiveness
- **Wind**: Affects kicking distance/accuracy and passing based on direction
- **Rain**: Increases fumbles, reduces passing accuracy and field conditions
- **Snow**: Reduces visibility, passing accuracy, and field conditions
- **Fog**: Reduces overall visibility and accuracy

## API Endpoints

### GET `/api/exhibition/teams`
Returns list of all available teams with their details.

### POST `/api/exhibition/simulate`
Simulates a game between two teams with specified conditions.

Request body:
```json
{
  "home_team": "KC",
  "away_team": "BUF", 
  "weather": {
    "condition": "clear",
    "temperature": 72,
    "wind_speed": 5,
    "wind_direction": "N"
  },
  "game_settings": {
    "overtime": true,
    "detailed_stats": true
  }
}
```

## Development Notes

- Uses modern React with hooks and TypeScript
- Responsive design works on desktop and mobile
- CORS configured for local development
- Error handling for network issues and invalid inputs
- Comprehensive type safety with TypeScript interfaces

## Future Enhancements

- Save simulation history
- Export game results  
- Advanced team customization
- Playoff scenarios
- Multiple game simulation
- Performance analytics dashboard

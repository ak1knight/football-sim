# Frontend + Backend Setup Instructions

## Quick Start

To run the complete football simulation application with both frontend and backend:

### 1. Start the Backend (Terminal 1)
```bash
cd backend
python app.py
```
The backend will start on `http://localhost:5000`

### 2. Start the Frontend (Terminal 2)  
```bash
cd frontend
npm run dev
```
The frontend will start on `http://localhost:5173`

## API Endpoints Now Available

With the teams endpoint added, the following APIs are now available:

### Teams API
- `GET /api/teams/` - Get all teams
- `GET /api/teams/{team_id}` - Get specific team details
- `GET /api/teams/{team_id}/roster` - Get team roster
- `GET /api/teams/{team_id}/stats` - Get team statistics
- `GET /api/teams/compare/{team1_id}/{team2_id}` - Compare two teams

### Exhibition API
- `POST /api/exhibition/simulate` - Simulate exhibition game

### Health Check
- `GET /api/health` - Backend health check

## Frontend Features

- **Team Selection**: Now properly integrated with backend team data
- **Exhibition Games**: Full team selection and game simulation
- **Professional UI**: Football Manager-inspired interface
- **Error Handling**: Graceful fallback to mock data when backend unavailable

## Next Steps

1. Start both servers as described above
2. Open `http://localhost:5173` in your browser
3. Navigate to "Exhibition Game" section
4. Select teams from the dropdowns (now populated with real NFL teams)
5. Click "Simulate Game" to see the results

The frontend will automatically proxy API calls to the backend, and if the backend is unavailable, it will fall back to mock data for development.
# Football Simulation Frontend

A React-based frontend for the football simulation engine, built with Vite, TypeScript, TailwindCSS, and MobX. The interface is inspired by Football Manager with a professional, game-like design optimized for user workflow.

## 🚀 Quick Start

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your browser to `http://localhost:5173`

## 🏗️ Architecture

### Tech Stack
- **React 18** with TypeScript for type safety
- **Vite** for fast development and building
- **TailwindCSS** for utility-first styling
- **MobX** for state management
- **React Router v6+** for navigation

### Project Structure
```
src/
├── components/           # React components
│   ├── Layout.tsx       # Main layout wrapper
│   ├── Sidebar.tsx      # Navigation sidebar
│   ├── Header.tsx       # Top header with tabs and user info
│   ├── ExhibitionGame.tsx    # Main exhibition game functionality
│   ├── SeasonManagement.tsx  # Season simulation (placeholder)
│   ├── TeamManagement.tsx    # Team management (placeholder)
│   ├── LeagueManagement.tsx  # League settings (placeholder)
│   ├── UserSettings.tsx      # User preferences (placeholder)
│   └── index.ts         # Component exports
├── stores/              # MobX stores
│   ├── AppStore.ts      # Global app state
│   ├── UserStore.ts     # User authentication and profile
│   ├── ExhibitionStore.ts    # Exhibition game state
│   └── index.ts         # Store exports
├── App.tsx              # Main app component with routing
├── main.tsx             # Entry point
└── index.css            # Global styles and Tailwind imports
```

## 🎮 Features

### Current (v1.0)
- **Exhibition Game Simulation**: Select two teams and simulate a quick game
- **Professional UI**: Football Manager-inspired dark theme
- **Responsive Layout**: Left sidebar navigation + top header with tabs
- **Mock Data**: Fallback team data when backend is unavailable
- **TypeScript**: Full type safety throughout the application

### Navigation Structure
- **Exhibition Game**: Quick game simulation between two teams
- **Season Simulation**: (Placeholder) Full season management
- **Team Management**: (Placeholder) Roster and team statistics
- **League Management**: (Placeholder) League configuration
- **User Settings**: (Placeholder) Profile and preferences

### State Management
- **AppStore**: Current section, tabs, and navigation state
- **UserStore**: User authentication and profile information
- **ExhibitionStore**: Team selection, game simulation, and results

## 🎨 Design System

### Color Scheme
- **Primary**: Blue tones for interactive elements
- **Secondary**: Dark grays for backgrounds and UI elements
- **Accent**: Orange tones for highlights and warnings

### Components
- **Cards**: Elevated containers with subtle borders
- **Buttons**: Primary and secondary button styles
- **Sidebar Items**: Hover states and active indicators
- **Tab Navigation**: Clean tab interface with active states

## 🔌 API Integration

The frontend is configured to work with the backend API:

- **Proxy Configuration**: `/api` routes are proxied to `http://localhost:8000`
- **Exhibition Endpoints**: 
  - `GET /api/teams` - Fetch available teams
  - `POST /api/exhibition/simulate` - Simulate exhibition game
- **Error Handling**: Graceful fallback to mock data when backend is unavailable

## 📝 Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## 🔄 Backend Integration

The frontend is designed to work with the Python Flask backend. Make sure the backend is running on `http://localhost:8000` for full functionality.

When the backend is not available, the frontend will:
- Display mock team data for development
- Show error messages for failed API calls
- Provide simulated game results using local logic

## 🎯 Next Steps

The current implementation provides the foundation for a complete football management system. Future enhancements include:

1. **Season Simulation**: Complete season management with scheduling
2. **Team Management**: Detailed roster and player management
3. **League Configuration**: Custom league rules and settings
4. **Statistics Dashboard**: Comprehensive game and season statistics
5. **User Authentication**: Real authentication system
6. **Real-time Updates**: WebSocket integration for live game simulation

## 🚀 Deployment

To build for production:

```bash
npm run build
```

The built files will be in the `dist/` directory and can be served by any static file server.

## 🛠️ Development Notes

- The application uses MobX for reactive state management
- TypeScript strict mode is enabled for better type safety
- TailwindCSS provides utility-first styling with custom Football Manager-inspired theme
- React Router handles client-side navigation
- The layout is responsive and optimized for desktop use

You are building the **React frontend** for a football simulation engine using **Vite** as the build tool and **TailwindCSS** for styling. The frontend should mirror the **Football Manager** UI style by Sports Interactive, with a professional, game-like interface optimized for user workflow.

## 🎯 Objectives

1. **Overall Layout**

   * Use a persistent **left sidebar** to navigate between core app sections:

     * Exhibition Game
     * Season Simulation
     * Team Management
     * League Management
     * User Settings
   * Use a **top header bar** for:

     * Sub-navigation tabs (depending on which main section is selected)
     * Displaying current **logged-in user info** (name, avatar placeholder, logout)

2. **Architecture**

   * Create a **React app scaffolded by Vite**.
   * Use **TailwindCSS** for utility-first styling.
   * Use **MobX** for state management:

     * One store for global app state (e.g., selected section/tab, user data)
     * Separate stores for each major module (Exhibition, Teams, etc.)

3. **Component Design**

   * Use **small, reusable components**:

     * Sidebar
     * Header
     * Tab Navigation
     * Button
     * Card
     * Form elements
     * Match Summary, Team Select, etc.
   * Use TypeScript for strict typing.

4. **Functionality Scope for v1**

   * Implement **Exhibition Game Simulation** section:

     * UI to select two teams from a dropdown or searchable list.
     * Simulate game via backend API call (exposed from our mono repo backend).
     * Display simulated result (basic summary, team stats).
   * Include placeholder views/components for other modules (season sim, teams, league) to be fleshed out later.

5. **API Integration**

   * Use async actions to fetch and post data via available API endpoints from the backend.
   * Refer to the backend directory in the mono repo for available endpoints (assume routes like `/api/exhibition/simulate`, `/api/teams`, etc.)

6. **Routing**

   * Use **React Router v6+** for page navigation.
   * Each main section (exhibition, season, team, etc.) gets its own route.
   * Tabs update based on the current main section context.

7. **Auth (Basic for now)**

   * Assume user is already authenticated for now.
   * Create a placeholder MobX store for user info (username, avatar).
   * Display this info in the header.

8. **File Structure Recommendation**

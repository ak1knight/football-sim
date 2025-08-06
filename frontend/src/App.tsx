import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { observer } from 'mobx-react-lite';
import { appStore } from './stores';
import { 
  Layout, 
  ExhibitionGame, 
  SeasonManagement, 
  TeamManagement, 
  LeagueManagement, 
  UserSettings 
} from './components';

const AppRoutes: React.FC = observer(() => {
  // Update app store when route changes
  useEffect(() => {
    const path = window.location.pathname;
    const section = path.slice(1) || 'exhibition';
    if (section !== appStore.currentSection) {
      appStore.setCurrentSection(section as any);
    }
  }, []);

  // Listen for store changes and update URL
  useEffect(() => {
    const newPath = `/${appStore.currentSection}`;
    if (window.location.pathname !== newPath) {
      window.history.pushState({}, '', newPath);
    }
  }, [appStore.currentSection]);

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/exhibition" replace />} />
        <Route path="/exhibition" element={<ExhibitionGame />} />
        <Route path="/season" element={<SeasonManagement />} />
        <Route path="/teams" element={<TeamManagement />} />
        <Route path="/league" element={<LeagueManagement />} />
        <Route path="/settings" element={<UserSettings />} />
        <Route path="*" element={<Navigate to="/exhibition" replace />} />
      </Routes>
    </Layout>
  );
});

const App: React.FC = () => {
  return (
    <Router>
      <div className="App">
        <AppRoutes />
      </div>
    </Router>
  );
};

export default App;

import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { observer } from 'mobx-react-lite';
import { StoresProvider, StoresContext } from './stores';
import { useContext } from 'react';
import {
  Layout,
  ExhibitionGame,
  TeamManagement,
  LeagueManagement,
  AppSettings,
  SeasonManagement
} from './components';


const AppRoutes: React.FC = observer(() => {
  const { appStore } = useContext(StoresContext);

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/exhibition" replace />} />
        <Route path="/exhibition" element={<ExhibitionGame />} />
        <Route path="/season" element={<SeasonManagement />} />
        <Route path="/teams" element={<TeamManagement />} />
        <Route path="/league" element={<LeagueManagement />} />
        <Route path="/settings" element={<AppSettings />} />
        <Route path="*" element={<Navigate to="/exhibition" replace />} />
      </Routes>
    </Layout>
  );
});

const App: React.FC = () => (
  <StoresProvider>
    <Router>
      <div className="App">
        <AppRoutes />
      </div>
    </Router>
  </StoresProvider>
);

export default App;

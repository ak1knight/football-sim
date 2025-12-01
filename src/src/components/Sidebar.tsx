import React from 'react';
import { observer } from 'mobx-react-lite';
import { appStore } from '../stores';
import type { Section } from '../stores';

const sidebarItems = [
  { key: 'exhibition' as Section, label: 'Exhibition Game', icon: '🏈' },
  { key: 'season' as Section, label: 'Season Simulation', icon: '📅' },
  { key: 'teams' as Section, label: 'Team Management', icon: '👥' },
  { key: 'league' as Section, label: 'League Management', icon: '🏆' },
  { key: 'settings' as Section, label: 'User Settings', icon: '⚙️' },
];

export const Sidebar: React.FC = observer(() => {
  const handleSectionClick = (section: Section) => {
    appStore.setCurrentSection(section);
  };

  return (
    <div className="w-64 bg-secondary-900 border-r border-secondary-700 flex flex-col">
      {/* Logo/Title */}
      <div className="p-6 border-b border-secondary-700">
        <h1 className="text-xl font-bold text-white">Football Sim</h1>
        <p className="text-sm text-secondary-400 mt-1">Management System</p>
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 pt-4">
        {sidebarItems.map((item) => (
          <div
            key={item.key}
            onClick={() => handleSectionClick(item.key)}
            className={`sidebar-item ${
              appStore.currentSection === item.key ? 'active' : ''
            }`}
          >
            <span className="text-xl mr-3">{item.icon}</span>
            <span className="font-medium">{item.label}</span>
          </div>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-secondary-700">
        <div className="text-xs text-secondary-500">
          Football Sim v1.0.0
        </div>
      </div>
    </div>
  );
});
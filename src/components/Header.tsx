import React from 'react';
import { observer } from 'mobx-react-lite';
import { appStore } from '../stores';

export const Header: React.FC = observer(() => {
  const handleTabClick = (tab: string) => {
    appStore.setCurrentTab(tab);
  };

  return (
    <header className="bg-secondary-800 border-b border-secondary-700 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Left side - Tab Navigation */}
        <div className="flex items-center space-x-1">
          {appStore.sectionTabs.map((tab) => (
            <button
              key={tab}
              onClick={() => handleTabClick(tab)}
              className={`tab-item ${
                appStore.currentTab === tab ? 'active' : ''
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Right side - App Title */}
        <div className="flex items-center space-x-4">
          <div className="text-sm">
            <div className="text-white font-medium">
              🏈 Football Simulation Engine
            </div>
            <div className="text-secondary-400 text-xs">
              Desktop Edition
            </div>
          </div>
        </div>
      </div>

      {/* Section Title */}
      <div className="mt-4">
        <h2 className="text-lg font-semibold text-white capitalize">
          {appStore.currentSection.replace(/([A-Z])/g, ' $1').trim()}
          {appStore.currentTab && (
            <span className="text-secondary-400 font-normal"> / {appStore.currentTab}</span>
          )}
        </h2>
      </div>
    </header>
  );
});
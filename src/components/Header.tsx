import React from 'react';
import { observer } from 'mobx-react-lite';
import { appStore } from '../stores';

export const Header: React.FC = observer(() => {
  const handleTabClick = (tab: string) => {
    appStore.setCurrentTab(tab);
  };

  return (
    <header className="">
      <div className="flex items-center justify-between bg-secondary-700 border-b border-secondary-600 px-6">
         {/* Section Title */}
      <div className="my-4 py-2">
        <h2 className="text-lg font-semibold text-white capitalize">
          {appStore.currentSection.replace(/([A-Z])/g, ' $1').trim()}
          {appStore.currentTab && (
            <span className="text-secondary-400 font-normal"> / {appStore.currentTab}</span>
          )}
        </h2>
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

      {/* Left side - Tab Navigation */}
        <div className="flex items-center space-x-1 bg-secondary-800 border-b border-secondary-700">
          {appStore.sectionTabs.map((tab) => (
            <button
              key={tab}
              onClick={() => handleTabClick(tab)}
              className={`tab-item pb-2 ${
                appStore.currentTab === tab ? 'active' : ''
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
    </header>
  );
});
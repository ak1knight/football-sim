import React from 'react';
import { observer } from 'mobx-react-lite';
import { appStore, userStore } from '../stores';

export const Header: React.FC = observer(() => {
  const handleTabClick = (tab: string) => {
    appStore.setCurrentTab(tab);
  };

  const handleLogout = () => {
    userStore.logout();
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

        {/* Right side - User Info */}
        <div className="flex items-center space-x-4">
          {/* User Avatar and Info */}
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center text-white font-medium text-sm">
              {userStore.userInitials}
            </div>
            <div className="text-sm">
              <div className="text-white font-medium">
                {userStore.displayName}
              </div>
              {userStore.user?.email && (
                <div className="text-secondary-400 text-xs">
                  {userStore.user.email}
                </div>
              )}
            </div>
          </div>

          {/* Logout Button */}
          {userStore.isAuthenticated && (
            <button
              onClick={handleLogout}
              className="text-secondary-400 hover:text-white text-sm px-3 py-1 rounded border border-secondary-600 hover:border-secondary-500 transition-colors"
            >
              Logout
            </button>
          )}
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
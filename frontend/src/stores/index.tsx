import React from 'react';
import { AppStore, appStore } from './AppStore';
import { UserStore, userStore } from './UserStore';
import { ExhibitionStore, exhibitionStore } from './ExhibitionStore';
import { SeasonStore, seasonStore } from './SeasonStore';

export { AppStore, appStore };
export { UserStore, userStore };
export { ExhibitionStore, exhibitionStore };
export { SeasonStore, seasonStore };
export type { Section } from './AppStore';
export type { User } from './UserStore';
export type { Team, GameResult } from './ExhibitionStore';

export const stores = {
  appStore,
  userStore,
  exhibitionStore,
  seasonStore,
};

export const StoresContext = React.createContext<typeof stores>(stores);

export const StoresProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <StoresContext.Provider value={stores}>{children}</StoresContext.Provider>
);
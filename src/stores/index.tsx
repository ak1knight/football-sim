import React from 'react';
import { AppStore, appStore } from './AppStore';
import { ExhibitionStore, exhibitionStore } from './ExhibitionStore';
import { SeasonStore, seasonStore } from './SeasonStore';

export { AppStore, appStore };
export { ExhibitionStore, exhibitionStore };
export { SeasonStore, seasonStore };
export type { Section } from './AppStore';
export type { Team, GameResult } from './ExhibitionStore';

export const stores = {
  appStore,
  exhibitionStore,
  seasonStore,
};

export const StoresContext = React.createContext<typeof stores>(stores);

export const StoresProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <StoresContext.Provider value={stores}>{children}</StoresContext.Provider>
);
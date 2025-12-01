import { makeAutoObservable } from 'mobx';

export type Section = 'exhibition' | 'season' | 'teams' | 'league' | 'settings';

export class AppStore {
  currentSection: Section = 'exhibition';
  currentTab: string = '';

  constructor() {
    makeAutoObservable(this);
  }

  setCurrentSection(section: Section) {
    this.currentSection = section;
    // Reset tab when changing sections
    this.currentTab = '';
  }

  setCurrentTab(tab: string) {
    this.currentTab = tab;
  }

  get sectionTabs() {
    const tabsMap: Record<Section, string[]> = {
      exhibition: ['Quick Game', 'Tournament'],
      season: ['Setup', 'Schedule', 'Standings', 'Playoffs'],
      teams: ['Roster', 'Stats', 'History'],
      league: ['Teams', 'Settings', 'Rules'],
      settings: ['Profile', 'Preferences', 'About']
    };
    
    return tabsMap[this.currentSection] || [];
  }
}

export const appStore = new AppStore();
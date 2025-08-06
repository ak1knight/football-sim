import { makeAutoObservable } from 'mobx';

export interface User {
  id: string;
  username: string;
  avatar?: string;
  email?: string;
}

export class UserStore {
  user: User | null = null;
  isAuthenticated: boolean = true; // Placeholder: assume authenticated

  constructor() {
    makeAutoObservable(this);
    // Initialize with mock user data
    this.initializeMockUser();
  }

  private initializeMockUser() {
    this.user = {
      id: '1',
      username: 'FootballManager',
      email: 'manager@football-sim.com'
    };
  }

  setUser(user: User | null) {
    this.user = user;
    this.isAuthenticated = !!user;
  }

  logout() {
    this.user = null;
    this.isAuthenticated = false;
  }

  get displayName() {
    return this.user?.username || 'Guest';
  }

  get userInitials() {
    if (!this.user?.username) return 'G';
    const names = this.user.username.split(' ');
    return names.map(name => name[0]).join('').toUpperCase().substring(0, 2);
  }
}

export const userStore = new UserStore();
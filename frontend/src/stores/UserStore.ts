import { makeAutoObservable } from 'mobx';
import { apiFetch } from '../api';

export interface User {
  id: string;
  username: string;
  avatar?: string;
  email?: string;
}

export class UserStore {
  user: User | null = null;
  isAuthenticated: boolean = false;
  jwt: string | null = null;
  error: string | null = null;

  constructor() {
    makeAutoObservable(this);
    this.loadFromStorage();
  }

  private loadFromStorage() {
    const jwt = localStorage.getItem('jwt');
    const user = localStorage.getItem('user');
    if (jwt && user) {
      this.jwt = jwt;
      this.user = JSON.parse(user);
      this.isAuthenticated = true;
    }
  }

  private saveToStorage() {
    if (this.jwt && this.user) {
      localStorage.setItem('jwt', this.jwt);
      localStorage.setItem('user', JSON.stringify(this.user));
    }
  }

  private clearStorage() {
    localStorage.removeItem('jwt');
    localStorage.removeItem('user');
  }

  setUser(user: User | null, jwt?: string | null) {
    this.user = user;
    this.isAuthenticated = !!user;
    if (jwt) {
      this.jwt = jwt;
      this.saveToStorage();
    } else if (!user) {
      this.jwt = null;
      this.clearStorage();
    }
  }

  setError(error: string | null) {
    this.error = error;
  }

  async login(username: string, password: string) {
    this.setError(null);
    try {
      const response = await apiFetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      const result = await response.json();
      if (result.success && result.token && result.user) {
        this.setUser(result.user, result.token);
        return { success: true };
      } else {
        this.setError(result.error || 'Login failed');
        this.setUser(null);
        return { success: false, error: result.error };
      }
    } catch (e) {
      this.setError('Network error');
      this.setUser(null);
      return { success: false, error: 'Network error' };
    }
  }

  async register(username: string, email: string, password: string, firstName?: string, lastName?: string) {
    this.setError(null);
    try {
      const response = await apiFetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password, first_name: firstName, last_name: lastName })
      });
      const result = await response.json();
      if (result.success) {
        // Optionally auto-login after registration
        return await this.login(username, password);
      } else {
        this.setError(result.error || 'Registration failed');
        return { success: false, error: result.error };
      }
    } catch (e) {
      this.setError('Network error');
      return { success: false, error: 'Network error' };
    }
  }

  logout() {
    this.setUser(null);
    this.clearStorage();
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
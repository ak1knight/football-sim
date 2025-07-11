/**
 * API service for communicating with the Football Simulation backend.
 */

import type { 
  TeamsResponse, 
  ExhibitionGameRequest, 
  ExhibitionGameResponse 
} from '../types/api';

const API_BASE_URL = 'http://localhost:5000/api';

class ApiService {
  private async makeRequest<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
      },
    };

    const response = await fetch(url, { ...defaultOptions, ...options });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  }

  /**
   * Get all available teams
   */
  async getTeams(): Promise<TeamsResponse> {
    return this.makeRequest<TeamsResponse>('/exhibition/teams');
  }

  /**
   * Simulate an exhibition game
   */
  async simulateExhibitionGame(request: ExhibitionGameRequest): Promise<ExhibitionGameResponse> {
    return this.makeRequest<ExhibitionGameResponse>('/exhibition/simulate', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: string; message: string }> {
    return this.makeRequest<{ status: string; message: string }>('/health');
  }
}

export const apiService = new ApiService();

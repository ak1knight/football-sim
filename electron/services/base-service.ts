import { DAOManager } from '../database/dao/dao-manager';

export abstract class BaseService {
  constructor(protected daoManager: DAOManager) {}
  
  protected handleError(error: any, operation: string): never {
    console.error(`${operation} failed:`, error);
    throw new Error(`${operation} failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }

  protected validateId(id: string, entityType: string): void {
    if (!id || typeof id !== 'string' || id.trim() === '') {
      throw new Error(`Invalid ${entityType} ID provided`);
    }
  }

  protected validateRequired(value: any, fieldName: string): void {
    if (value === undefined || value === null || (typeof value === 'string' && value.trim() === '')) {
      throw new Error(`${fieldName} is required`);
    }
  }

  protected formatResponse<T>(data: T): { success: true; data: T } {
    return { success: true, data };
  }

  protected formatError(error: Error | string): { success: false; error: string } {
    return { 
      success: false, 
      error: error instanceof Error ? error.message : error 
    };
  }
}
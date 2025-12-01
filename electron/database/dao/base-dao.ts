import Database from 'better-sqlite3';

export abstract class BaseDAO<T> {
  protected db: Database.Database;
  protected tableName: string;

  constructor(database: Database.Database, tableName: string) {
    this.db = database;
    this.tableName = tableName;
  }

  // Generic CRUD operations
  protected findById(id: string): T | undefined {
    const stmt = this.db.prepare(`SELECT * FROM ${this.tableName} WHERE id = ?`);
    const row = stmt.get(id);
    return row ? this.mapRowToEntity(row as any) : undefined;
  }

  protected findAll(limit?: number, orderBy?: string): T[] {
    let query = `SELECT * FROM ${this.tableName}`;
    
    if (orderBy) {
      query += ` ORDER BY ${orderBy}`;
    }
    
    if (limit) {
      query += ` LIMIT ?`;
    }
    
    const stmt = this.db.prepare(query);
    const rows = limit ? stmt.all(limit) : stmt.all();
    return rows.map(row => this.mapRowToEntity(row as any));
  }

  protected findWhere(whereClause: string, params: any[] = [], limit?: number): T[] {
    let query = `SELECT * FROM ${this.tableName} WHERE ${whereClause}`;
    
    if (limit) {
      query += ` LIMIT ?`;
      params.push(limit);
    }
    
    const stmt = this.db.prepare(query);
    const rows = stmt.all(...params);
    return rows.map(row => this.mapRowToEntity(row as any));
  }

  protected findOneWhere(whereClause: string, params: any[] = []): T | undefined {
    const query = `SELECT * FROM ${this.tableName} WHERE ${whereClause} LIMIT 1`;
    const stmt = this.db.prepare(query);
    const row = stmt.get(...params);
    return row ? this.mapRowToEntity(row as any) : undefined;
  }

  protected insert(entity: Partial<T & Record<string, any>>): string {
    const fields = Object.keys(entity);
    const placeholders = fields.map(() => '?').join(', ');
    const query = `INSERT INTO ${this.tableName} (${fields.join(', ')}) VALUES (${placeholders})`;
    
    const stmt = this.db.prepare(query);
    const values = Object.values(entity);
    const result = stmt.run(...values);
    
    // Return the ID (assuming it's the first field or lastInsertRowid for auto-increment)
    if (entity.id) {
      return entity.id as string;
    }
    return result.lastInsertRowid.toString();
  }

  protected insertMany(entities: Array<Partial<T & Record<string, any>>>): number {
    if (entities.length === 0) return 0;
    
    const fields = Object.keys(entities[0]);
    const placeholders = fields.map(() => '?').join(', ');
    const query = `INSERT INTO ${this.tableName} (${fields.join(', ')}) VALUES (${placeholders})`;
    
    const stmt = this.db.prepare(query);
    
    const transaction = this.db.transaction((entities: any[]) => {
      for (const entity of entities) {
        const values = fields.map(field => entity[field]);
        stmt.run(...values);
      }
    });
    
    transaction(entities);
    return entities.length;
  }

  protected update(id: string, updates: Partial<T & Record<string, any>>): boolean {
    const fields = Object.keys(updates);
    const setClause = fields.map(field => `${field} = ?`).join(', ');
    const query = `UPDATE ${this.tableName} SET ${setClause} WHERE id = ?`;
    
    const stmt = this.db.prepare(query);
    const values = [...Object.values(updates), id];
    const result = stmt.run(...values);
    
    return result.changes > 0;
  }

  protected updateWhere(whereClause: string, updates: Partial<T & Record<string, any>>, params: any[] = []): number {
    const fields = Object.keys(updates);
    const setClause = fields.map(field => `${field} = ?`).join(', ');
    const query = `UPDATE ${this.tableName} SET ${setClause} WHERE ${whereClause}`;
    
    const stmt = this.db.prepare(query);
    const values = [...Object.values(updates), ...params];
    const result = stmt.run(...values);
    
    return result.changes;
  }

  protected delete(id: string): boolean {
    const stmt = this.db.prepare(`DELETE FROM ${this.tableName} WHERE id = ?`);
    const result = stmt.run(id);
    return result.changes > 0;
  }

  protected deleteWhere(whereClause: string, params: any[] = []): number {
    const query = `DELETE FROM ${this.tableName} WHERE ${whereClause}`;
    const stmt = this.db.prepare(query);
    const result = stmt.run(...params);
    return result.changes;
  }

  protected deleteAll(): number {
    const stmt = this.db.prepare(`DELETE FROM ${this.tableName}`);
    const result = stmt.run();
    return result.changes;
  }

  protected count(whereClause?: string, params: any[] = []): number {
    let query = `SELECT COUNT(*) as count FROM ${this.tableName}`;
    
    if (whereClause) {
      query += ` WHERE ${whereClause}`;
    }
    
    const stmt = this.db.prepare(query);
    const result = whereClause ? stmt.get(...params) : stmt.get();
    return (result as { count: number }).count;
  }

  protected exists(whereClause: string, params: any[] = []): boolean {
    const query = `SELECT 1 FROM ${this.tableName} WHERE ${whereClause} LIMIT 1`;
    const stmt = this.db.prepare(query);
    const result = stmt.get(...params);
    return result !== undefined;
  }

  // Utility method for generating UUIDs (simple implementation)
  protected generateId(prefix?: string): string {
    const timestamp = Date.now().toString(36);
    const random = Math.random().toString(36).substring(2);
    const id = `${timestamp}${random}`;
    return prefix ? `${prefix}_${id}` : id;
  }

  // Utility method for JSON handling
  protected parseJsonField(value: string | null): any {
    if (!value) return null;
    try {
      return JSON.parse(value);
    } catch (error) {
      console.warn(`Failed to parse JSON field: ${value}`);
      return null;
    }
  }

  protected stringifyJsonField(value: any): string {
    if (value === null || value === undefined) return '{}';
    try {
      return JSON.stringify(value);
    } catch (error) {
      console.warn('Failed to stringify JSON field:', value);
      return '{}';
    }
  }

  // Abstract method to be implemented by concrete DAOs
  protected abstract mapRowToEntity(row: any): T;

  // Optional: Override for custom entity to row mapping
  protected mapEntityToRow(entity: T): Record<string, any> {
    return entity as any;
  }

  // Transaction helpers
  protected transaction<R>(callback: () => R): R {
    const transaction = this.db.transaction(callback);
    return transaction();
  }

  // Raw query execution for complex operations
  public executeQuery(query: string, params: any[] = []): any[] {
    const stmt = this.db.prepare(query);
    return stmt.all(...params);
  }

  public executeSingle(query: string, params: any[] = []): any {
    const stmt = this.db.prepare(query);
    return stmt.get(...params);
  }

  public executeUpdate(query: string, params: any[] = []): { changes: number; lastInsertRowid: number } {
    const stmt = this.db.prepare(query);
    const result = stmt.run(...params);
    return {
      changes: result.changes,
      lastInsertRowid: typeof result.lastInsertRowid === 'bigint' ? Number(result.lastInsertRowid) : result.lastInsertRowid
    };
  }

  // Public methods for DAO Manager
  public countRecords(whereClause?: string, params: any[] = []): number {
    return this.count(whereClause, params);
  }

  public deleteRecord(id: string): boolean {
    return this.delete(id);
  }
}
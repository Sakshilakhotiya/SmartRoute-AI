import Database from 'better-sqlite3'; import fs from 'node:fs'; import path from 'node:path';
const dir=path.resolve('data');fs.mkdirSync(dir,{recursive:true});
export const db=new Database(path.join(dir,'smartroute.sqlite'));
db.pragma('journal_mode = WAL');db.pragma('foreign_keys = ON');
db.exec(`CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,email TEXT NOT NULL UNIQUE,password_hash TEXT NOT NULL,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS saved_routes(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,origin TEXT NOT NULL,destination TEXT NOT NULL,vehicle TEXT NOT NULL,priority TEXT NOT NULL,preference TEXT NOT NULL,distance_km REAL NOT NULL,estimated_cost REAL NOT NULL,route_snapshot TEXT NOT NULL,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS route_history(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,origin TEXT NOT NULL,destination TEXT NOT NULL,vehicle TEXT NOT NULL,preference TEXT NOT NULL,distance_km REAL NOT NULL,estimated_cost REAL NOT NULL,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX IF NOT EXISTS idx_saved_user_date ON saved_routes(user_id,created_at DESC);CREATE INDEX IF NOT EXISTS idx_history_user_date ON route_history(user_id,created_at DESC);`);

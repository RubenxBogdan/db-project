import sqlite3
import os
from datetime import datetime

DB_FILE = 'nba_stats.db'

# Register converters for date/datetime types
def convert_date(val):
    """Convert stored date string back to datetime object."""
    try:
        return datetime.fromisoformat(val.decode('utf-8'))
    except (ValueError, AttributeError):
        return val.decode('utf-8') if isinstance(val, bytes) else val

# Register converters for both DATE and DATETIME type names
sqlite3.register_adapter(datetime, lambda val: val.isoformat())
sqlite3.register_converter("DATE", convert_date)
sqlite3.register_converter("DATETIME", convert_date)

def get_conn():
    """Get a database connection."""
    conn = sqlite3.connect(DB_FILE, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn

def db_read(sql, params=None, single=False):
    """
    Execute a SELECT query and return results.

    Args:
        sql: SQL query string
        params: Tuple of parameters for the query
        single: If True, returns a single dict or None. If False, returns a list of dicts.

    Returns:
        Single dict or list of dicts
    """
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())

        # Get column names from description
        columns = [desc[0] for desc in cur.description] if cur.description else []

        if single:
            row = cur.fetchone()
            if row:
                # Convert sqlite3.Row to dict and handle date columns
                result = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    # Check if this looks like a date string and convert it
                    if isinstance(value, str):
                        try:
                            # Try to parse as date
                            result[col] = datetime.fromisoformat(value)
                        except ValueError:
                            result[col] = value
                    else:
                        result[col] = value
                return result
            return None
        else:
            rows = cur.fetchall()
            results = []
            for row in rows:
                result = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    if isinstance(value, str):
                        try:
                            result[col] = datetime.fromisoformat(value)
                        except ValueError:
                            result[col] = value
                    else:
                        result[col] = value
                results.append(result)
            return results
    finally:
        conn.close()

def db_write(sql, params=None):
    """
    Execute an INSERT, UPDATE, or DELETE query.
    
    Args:
        sql: SQL query string
        params: Tuple of parameters for the query
    
    Returns:
        The rowid of the last modified row (for INSERT)
    """
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()

def init_db():
    """Initialize the database with the required tables."""
    conn = get_conn()
    try:
        cur = conn.cursor()
        
        # Create Teams table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                city TEXT NOT NULL,
                conference TEXT NOT NULL CHECK(conference IN ('East', 'West'))
            )
        ''')
        
        # Create Players table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                position TEXT NOT NULL,
                birth_date DATE,
                current_team_id INTEGER,
                FOREIGN KEY (current_team_id) REFERENCES teams(id)
            )
        ''')
        
        # Create Games table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                home_team_id INTEGER NOT NULL,
                away_team_id INTEGER NOT NULL,
                home_score INTEGER DEFAULT 0,
                away_score INTEGER DEFAULT 0,
                FOREIGN KEY (home_team_id) REFERENCES teams(id),
                FOREIGN KEY (away_team_id) REFERENCES teams(id),
                CHECK (home_team_id != away_team_id)
            )
        ''')
        
        # Create PlayerStatistics table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS player_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                game_id INTEGER NOT NULL,
                points INTEGER DEFAULT 0,
                rebounds INTEGER DEFAULT 0,
                assists INTEGER DEFAULT 0,
                minutes_played INTEGER DEFAULT 0,
                steals INTEGER DEFAULT 0,
                blocks INTEGER DEFAULT 0,
                turnovers INTEGER DEFAULT 0,
                FOREIGN KEY (player_id) REFERENCES players(id),
                FOREIGN KEY (game_id) REFERENCES games(id)
            )
        ''')
        
        # Create TeamHistory table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS team_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                team_id INTEGER NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE,
                FOREIGN KEY (player_id) REFERENCES players(id),
                FOREIGN KEY (team_id) REFERENCES teams(id)
            )
        ''')
        
        # Create Users table for authentication
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        print("Database initialized successfully!")
    finally:
        conn.close()

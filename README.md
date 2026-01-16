# NBA Statistics Tracker

A Flask web application for tracking NBA teams, players, games, and player statistics. This application implements 5 use cases for managing basketball data.

## Features

- **Use Case 1: Update Games** - Add new game results and scores
- **Use Case 2: Update Player Statistics** - Record individual player performance in games
- **Use Case 3: Inspect Player Statistics** - View detailed player stats and career history
- **Use Case 4: Former Teams** - Track player team history and transfers
- **Use Case 5: Team Roster** - View current team lineups

## Requirements

- Python 3.8+
- Flask
- Flask-Login

## Installation

1. Clone or navigate to the project directory:
   ```bash
   cd nba_stats_app
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. Start the Flask development server:
   ```bash
   python app.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

3. Register a new account or login
4. Click "Init DB" in the navigation bar to initialize the database tables
5. Click "Seed DB" to add sample data

## Project Structure

```
nba_stats_app/
├── app.py              # Main Flask application with routes
├── db.py               # Database helper functions (sqlite3)
├── auth.py             # Authentication module (Flask-Login)
├── requirements.txt    # Python dependencies
├── static/
│   └── css/
│       └── style.css   # Custom styles (NBA colors)
└── templates/
    ├── base.html       # Base template with navigation
    ├── index.html      # Dashboard
    ├── login.html      # Login form
    ├── register.html   # Registration form
    ├── teams.html      # List of teams
    ├── team_detail.html # Team roster (Use Case 5)
    ├── add_team.html   # Add team form
    ├── players.html    # List of players
    ├── player_detail.html # Player statistics (Use Case 3)
    ├── add_player.html # Add player form
    ├── team_history.html # Team history (Use Case 4)
    ├── games.html      # List of games
    ├── add_game.html   # Add game form (Use Case 1)
    ├── game_detail.html # Game details
    ├── add_game_stats.html # Add player stats (Use Case 2)
    ├── 404.html        # Custom 404 page
    └── 500.html        # Custom 500 page
```

## Database Schema

The application uses SQLite with the following tables:

1. **teams** - NBA team information (name, city, conference)
2. **players** - Player information (name, position, birth date, current team)
3. **games** - Game results (date, teams, scores)
4. **player_statistics** - Individual game statistics (points, rebounds, assists, etc.)
5. **team_history** - Player team history (previous teams, dates)
6. **users** - User accounts for authentication

## Database Helper Functions

The `db.py` module provides helper functions for database operations:

- `get_conn()` - Get a database connection
- `db_read(sql, params, single)` - Execute SELECT query and return results
- `db_write(sql, params)` - Execute INSERT, UPDATE, or DELETE query
- `init_db()` - Initialize database with all tables

## Authentication

The application uses Flask-Login for user authentication:

- `register` - Create a new user account
- `login` - User login
- `logout` - User logout

Routes for adding/modifying data require authentication.

## Technologies Used

- **Backend**: Python, Flask
- **Database**: SQLite with raw sqlite3
- **Authentication**: Flask-Login
- **Frontend**: HTML5, CSS3, Bootstrap 5 (via CDN)

## License

This project is for educational purposes.

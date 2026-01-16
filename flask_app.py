"""
NBA Statistics Tracker Flask Application

A web application for tracking NBA teams, players, games, and player statistics.
Implements 5 use cases for managing basketball data.
Uses sqlite3 directly with helper functions from db.py.
"""

from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from datetime import datetime
from db import db_read, db_write, init_db
from auth import User, login_manager, register_user, authenticate
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Custom template filter for date formatting
@app.template_filter('format_date')
def format_date(value, format_str='%B %d, %Y'):
    """Format a date string or datetime object."""
    if value is None:
        return ''
    if isinstance(value, str):
        # Try to parse the string as a date
        try:
            from datetime import datetime
            return datetime.fromisoformat(value).strftime(format_str)
        except (ValueError, AttributeError):
            return value
    else:
        # It's already a datetime object
        return value.strftime(format_str)

# Initialize Flask-Login
login_manager.init_app(app)
login_manager.login_view = 'login'


# ============== Helper Functions ==============

def get_teams():
    """Get all teams."""
    return db_read("SELECT * FROM teams ORDER BY name")

def get_team(team_id):
    """Get a single team by ID."""
    return db_read("SELECT * FROM teams WHERE id = ?", (team_id,), single=True)

def get_players():
    """Get all players."""
    return db_read("SELECT p.*, t.city, t.name as team_name FROM players p LEFT JOIN teams t ON p.current_team_id = t.id ORDER BY p.name")

def get_player(player_id):
    """Get a single player by ID."""
    return db_read("SELECT p.*, t.city, t.name as team_name FROM players p LEFT JOIN teams t ON p.current_team_id = t.id WHERE p.id = ?", (player_id,), single=True)

def get_games():
    """Get all games."""
    return db_read("""
        SELECT g.*, 
               ht.city as home_city, ht.name as home_name,
               at.city as away_city, at.name as away_name
        FROM games g
        JOIN teams ht ON g.home_team_id = ht.id
        JOIN teams at ON g.away_team_id = at.id
        ORDER BY g.date DESC
    """)

def get_game(game_id):
    """Get a single game by ID."""
    return db_read("""
        SELECT g.*, 
               ht.city as home_city, ht.name as home_name,
               at.city as away_city, at.name as away_name
        FROM games g
        JOIN teams ht ON g.home_team_id = ht.id
        JOIN teams at ON g.away_team_id = at.id
        WHERE g.id = ?
    """, (game_id,), single=True)

def get_player_stats(player_id):
    """Get all statistics for a player."""
    return db_read("""
        SELECT ps.*, g.date, g.home_score, g.away_score,
               ht.name as home_team, at.name as away_team
        FROM player_statistics ps
        JOIN games g ON ps.game_id = g.id
        JOIN teams ht ON g.home_team_id = ht.id
        JOIN teams at ON g.away_team_id = at.id
        WHERE ps.player_id = ?
        ORDER BY g.date DESC
    """, (player_id,))

def get_game_stats(game_id):
    """Get all player statistics for a game."""
    return db_read("""
        SELECT ps.*, p.name as player_name, p.position, t.city, t.name as team_name
        FROM player_statistics ps
        JOIN players p ON ps.player_id = p.id
        LEFT JOIN teams t ON p.current_team_id = t.id
        WHERE ps.game_id = ?
    """, (game_id,))

def get_team_history(player_id):
    """Get team history for a player."""
    return db_read("""
        SELECT th.*, t.city, t.name
        FROM team_history th
        JOIN teams t ON th.team_id = t.id
        WHERE th.player_id = ?
        ORDER BY th.start_date DESC
    """, (player_id,))

def calculate_player_averages(player_id):
    """Calculate career averages for a player."""
    stats = db_read("""
        SELECT AVG(points) as avg_points, AVG(rebounds) as avg_rebounds, 
               AVG(assists) as avg_assists, COUNT(*) as games_played
        FROM player_statistics WHERE player_id = ?
    """, (player_id,), single=True)
    return stats


# ============== Routes ==============

@app.route("/")
def index():
    """Dashboard view showing overview of NBA statistics."""
    teams = get_teams()
    players = db_read("SELECT * FROM players")
    games = get_games()
    
    total_teams = len(teams)
    total_players = len(players)
    total_games = len(games)
    
    recent_games = games[:10] if games else []
    
    return render_template("index.html", 
                         teams=teams,
                         total_teams=total_teams,
                         total_players=total_players,
                         total_games=total_games,
                         recent_games=recent_games)


# ============== Authentication Routes ==============

@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration."""
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        
        if not username or not password:
            flash("Bitte Benutzername und Passwort eingeben.", "error")
        elif register_user(username, password):
            flash("Registrierung erfolgreich! Bitte einloggen.", "success")
            return redirect(url_for("login"))
        else:
            flash("Benutzername existiert bereits.", "error")
    
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """User login."""
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        
        user = authenticate(username, password)
        if user:
            login_user(user)
            flash(f"Willkommen, {user.username}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("index"))
        else:
            flash("Ungültiger Benutzername oder Passwort.", "error")
    
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """User logout."""
    logout_user()
    flash("Du wurdest abgemeldet.", "info")
    return redirect(url_for("index"))


# ============== Team Routes ==============

@app.route("/teams")
def teams_list():
    """List all teams."""
    teams = get_teams()
    return render_template("teams.html", teams=teams)


@app.route("/teams/add", methods=["GET", "POST"])
@login_required
def add_team():
    """Add new team."""
    if request.method == "POST":
        name = request.form["name"].strip()
        city = request.form["city"].strip()
        conference = request.form["conference"]
        
        if name and city and conference:
            db_write("INSERT INTO teams (name, city, conference) VALUES (?, ?, ?)", 
                    (name, city, conference))
            flash("Team erfolgreich hinzugefügt!", "success")
            return redirect(url_for("teams_list"))
        else:
            flash("Bitte alle Felder ausfüllen.", "error")
    
    return render_template("add_team.html")


@app.route("/teams/<int:team_id>")
def team_detail(team_id):
    """Use Case 5: View Team Roster."""
    team = get_team(team_id)
    if not team:
        abort(404)
    
    players = db_read("SELECT * FROM players WHERE current_team_id = ?", (team_id,))
    
    return render_template("team_detail.html", team=team, players=players)


# ============== Player Routes ==============

@app.route("/players")
def players_list():
    """List all players."""
    players = get_players()
    return render_template("players.html", players=players)


@app.route("/players/add", methods=["GET", "POST"])
@login_required
def add_player():
    """Add new player."""
    teams = get_teams()
    
    if request.method == "POST":
        name = request.form["name"].strip()
        position = request.form["position"]
        birth_date = request.form.get("birth_date")
        current_team_id = request.form.get("current_team_id")
        
        if name and position:
            if current_team_id:
                db_write("INSERT INTO players (name, position, birth_date, current_team_id) VALUES (?, ?, ?, ?)",
                        (name, position, birth_date, current_team_id))
            else:
                db_write("INSERT INTO players (name, position, birth_date) VALUES (?, ?, ?)",
                        (name, position, birth_date))
            flash("Spieler erfolgreich hinzugefügt!", "success")
            return redirect(url_for("players_list"))
        else:
            flash("Bitte Name und Position eingeben.", "error")
    
    return render_template("add_player.html", teams=teams)


@app.route("/players/<int:player_id>")
def player_detail(player_id):
    """Use Case 3: Inspect Player Statistics."""
    player = get_player(player_id)
    if not player:
        abort(404)
    
    statistics = get_player_stats(player_id)
    team_history = get_team_history(player_id)
    averages = calculate_player_averages(player_id)
    
    return render_template("player_detail.html", 
                         player=player,
                         statistics=statistics,
                         team_history=team_history,
                         averages=averages)


@app.route("/players/<int:player_id>/history", methods=["GET", "POST"])
@login_required
def add_team_history(player_id):
    """Use Case 4: View/Add Former Teams."""
    player = get_player(player_id)
    if not player:
        abort(404)
    
    teams = get_teams()
    team_history = get_team_history(player_id)
    
    if request.method == "POST":
        team_id = request.form["team_id"]
        start_date = request.form["start_date"]
        end_date = request.form.get("end_date")
        
        if team_id and start_date:
            db_write("INSERT INTO team_history (player_id, team_id, start_date, end_date) VALUES (?, ?, ?, ?)",
                    (player_id, team_id, start_date, end_date))
            
            # Update player's current team if no end date
            if not end_date:
                db_write("UPDATE players SET current_team_id = ? WHERE id = ?", (team_id, player_id))
            
            flash("Team-Historie erfolgreich hinzugefügt!", "success")
            return redirect(url_for("player_detail", player_id=player_id))
    
    return render_template("team_history.html", player=player, teams=teams, team_history=team_history)


# ============== Game Routes ==============

@app.route("/games")
def games_list():
    """List all games."""
    games = get_games()
    return render_template("games.html", games=games)


@app.route("/games/add", methods=["GET", "POST"])
@login_required
def add_game():
    """Use Case 1: Update Games - Add new game data."""
    teams = get_teams()
    
    if request.method == "POST":
        date = request.form["date"]
        home_team_id = request.form["home_team_id"]
        away_team_id = request.form["away_team_id"]
        home_score = request.form["home_score"]
        away_score = request.form["away_score"]
        
        if date and home_team_id and away_team_id and home_score and away_score:
            if home_team_id == away_team_id:
                flash("Heim- und Auswärtsteam müssen unterschiedlich sein.", "error")
            else:
                db_write("""
                    INSERT INTO games (date, home_team_id, away_team_id, home_score, away_score) 
                    VALUES (?, ?, ?, ?, ?)
                """, (date, home_team_id, away_team_id, home_score, away_score))
                flash("Spiel erfolgreich hinzugefügt!", "success")
                return redirect(url_for("games_list"))
        else:
            flash("Bitte alle Felder ausfüllen.", "error")
    
    return render_template("add_game.html", teams=teams)


@app.route("/games/<int:game_id>")
def game_detail(game_id):
    """View game details and statistics."""
    game = get_game(game_id)
    if not game:
        abort(404)
    
    statistics = get_game_stats(game_id)
    
    return render_template("game_detail.html", game=game, statistics=statistics)


@app.route("/games/<int:game_id>/stats", methods=["GET", "POST"])
@login_required
def add_game_stats(game_id):
    """Use Case 2: Update Player Statistics - Add stats for a specific game."""
    game = get_game(game_id)
    if not game:
        abort(404)
    
    # Get players from both teams
    home_players = db_read("SELECT * FROM players WHERE current_team_id = ?", (game["home_team_id"],))
    away_players = db_read("SELECT * FROM players WHERE current_team_id = ?", (game["away_team_id"],))
    all_players = home_players + away_players
    
    if request.method == "POST":
        player_id = request.form["player_id"]
        points = request.form["points"]
        rebounds = request.form["rebounds"]
        assists = request.form["assists"]
        minutes = request.form["minutes"]
        steals = request.form.get("steals", 0)
        blocks = request.form.get("blocks", 0)
        turnovers = request.form.get("turnovers", 0)
        
        if player_id and points:
            db_write("""
                INSERT INTO player_statistics 
                (player_id, game_id, points, rebounds, assists, minutes_played, steals, blocks, turnovers)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (player_id, game_id, points, rebounds, assists, minutes, steals, blocks, turnovers))
            flash("Spieler-Statistiken erfolgreich hinzugefügt!", "success")
            return redirect(url_for("game_detail", game_id=game_id))
        else:
            flash("Bitte alle erforderlichen Felder ausfüllen.", "error")
    
    return render_template("add_game_stats.html", game=game, players=all_players)


# ============== Utility Routes ==============

@app.route("/init-db")
def init_database():
    """Initialize database with tables."""
    init_db()
    flash("Datenbank erfolgreich initialisiert!", "success")
    return redirect(url_for("index"))


@app.route("/seed-db")
def seed_database():
    """Add sample data to the database."""
    # Check if data already exists
    existing = db_read("SELECT COUNT(*) as count FROM teams")
    if existing and existing[0]["count"] > 0:
        flash("Datenbank enthält bereits Daten.", "info")
        return redirect(url_for("index"))
    
    # Create sample teams
    teams_data = [
        ('Lakers', 'Los Angeles', 'West'),
        ('Celtics', 'Boston', 'East'),
        ('Warriors', 'Golden State', 'West'),
        ('Bulls', 'Chicago', 'East'),
        ('Heat', 'Miami', 'East')
    ]
    
    for name, city, conference in teams_data:
        db_write("INSERT INTO teams (name, city, conference) VALUES (?, ?, ?)", (name, city, conference))
    
    # Create sample players
    players_data = [
        ('LeBron James', 'SF', '1990-12-30', 1),
        ('Anthony Davis', 'PF', '1993-03-11', 1),
        ('Jayson Tatum', 'SF', '1998-03-03', 2),
        ('Jaylen Brown', 'SG', '1996-10-24', 2),
        ('Stephen Curry', 'PG', '1988-03-14', 3),
        ('Klay Thompson', 'SG', '1990-02-08', 3),
        ('Michael Jordan', 'SG', '1963-02-17', 4),
        ('Scottie Pippen', 'SF', '1965-09-25', 4),
        ('Jimmy Butler', 'SF', '1989-09-14', 5),
        ('Bam Adebayo', 'C', '1997-07-18', 5)
    ]
    
    for name, position, birth_date, team_id in players_data:
        db_write("INSERT INTO players (name, position, birth_date, current_team_id) VALUES (?, ?, ?, ?)",
                (name, position, birth_date, team_id))
    
    # Create sample game
    db_write("""
        INSERT INTO games (date, home_team_id, away_team_id, home_score, away_score)
        VALUES ('2025-01-15', 1, 2, 118, 112)
    """)
    
    # Create sample stats
    for player_id in range(1, 6):
        db_write("""
            INSERT INTO player_statistics 
            (player_id, game_id, points, rebounds, assists, minutes_played, steals, blocks, turnovers)
            VALUES (?, 1, 20, 5, 5, 30, 1, 1, 2)
        """, (player_id,))
    
    flash("Beispieldaten erfolgreich hinzugefügt!", "success")
    return redirect(url_for("index"))


# ============== Error Handlers ==============

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


# ============== App Start ==============

if __name__ == "__main__":
    # Initialize database on first run
    if not os.path.exists('nba_stats.db'):
        init_db()
    app.run(debug=True)

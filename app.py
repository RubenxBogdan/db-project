from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nba_stats.db'
app.config['SECRET_KEY'] = 'nba_pro_secret'
db = SQLAlchemy(app)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    team = db.Column(db.String(100), nullable=False)
    points = db.Column(db.Float, default=0.0)
    history = db.Column(db.Text, default="")

@app.route('/')
def index():
    players = Player.query.all()
    return render_template('index.html', players=players)

@app.route('/inspect', methods=['POST'])
def inspect():
    search_name = request.form.get('name')
    player = Player.query.filter_by(name=search_name).first()
    if not player:
        flash(f"Dieser Spieler '{search_name}' ist unbekannt, moechten Sie für ihn Daten eintragen?")
        return redirect(url_for('index'))
    return render_template('index.html', inspected_player=player, players=Player.query.all())

@app.route('/add', methods=['POST'])
def add_player():
    name = request.form.get('name')
    team = request.form.get('team')
    history = request.form.get('history')
    new_p = Player(name=name, team=team, history=history)
    db.session.add(new_p)
    db.session.commit()
    return redirect(url_for('index'))
@app.route('/team/<team_name>')
def team_roster(team_name):
    players = Player.query.filter_by(team=team_name).all()
    return render_template('index.html', players=players, title=f"Kader: {team_name}")

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# Professional database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nba_stats.db'
app.config['SECRET_KEY'] = 'nba_secure_key_2025'
db = SQLAlchemy(app)

# Database Model reflecting your Use Cases
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    team = db.Column(db.String(100), nullable=False)
    points = db.Column(db.Float, default=0.0)
    rebounds = db.Column(db.Float, default=0.0)
    history = db.Column(db.Text, default="") # For Use Case 4: Former Teams

# Use Case 1 & 2: Updating Game and Player Stats [cite: 2, 4]
@app.route('/update', methods=['POST'])
def update():
    name = request.form.get('name')
    pts = float(request.form.get('points', 0))
    reb = float(request.form.get('rebounds', 0))
    
    player = Player.query.filter_by(name=name).first()
    if player:
        # Update existing player stats [cite: 2]
        player.points = pts
        player.rebounds = reb
        db.session.commit()
    else:
        # If player unknown, create new (Use Case 3 Alternative Flow) 
        new_player = Player(name=name, team="Free Agent", points=pts, rebounds=reb)
        db.session.add(new_player)
        db.session.commit()
    return redirect(url_for('index'))

# Use Case 3, 4, & 5: Inspection and Rosters [cite: 6, 8, 10]
@app.route('/')
def index():
    players = Player.query.all()
    return render_template('index.html', players=players)

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Automatically creates your database tables
    app.run(debug=True)

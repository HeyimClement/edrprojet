from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from utils.suricata import SuricataLogParser
import logging
import os

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialisation du parser Suricata
suricata_parser = SuricataLogParser()

# Simulation d'une base utilisateur simple
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    # Récupérer les statistiques
    stats = suricata_parser.get_statistics()
    logger.debug(f"Stats générées: {stats}")
    
    return render_template('dashboard.html', 
                         stats=stats,
                         alerts=stats['recent_alerts'])

@app.route('/api/alerts')
@login_required
def get_alerts():
    """API endpoint pour récupérer les alertes en temps réel."""
    stats = suricata_parser.get_statistics()
    return jsonify(stats)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'password':
            user = User(1)
            login_user(user)
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Identifiants invalides")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 
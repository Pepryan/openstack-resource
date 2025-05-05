from flask import Flask
from flask_login import LoginManager
import config
from models import User
from routes import blueprints
from datetime import timedelta

# Initialize Flask app
app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Configure session settings
app.config['SESSION_PERMANENT'] = config.SESSION_PERMANENT
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=config.PERMANENT_SESSION_LIFETIME_DAYS)

# Configure Flask-Login remember cookie settings
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=config.PERMANENT_SESSION_LIFETIME_DAYS)
app.config['REMEMBER_COOKIE_REFRESH_EACH_REQUEST'] = True
app.config['REMEMBER_COOKIE_SECURE'] = True
app.config['REMEMBER_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_SAMESITE'] = 'Lax'

# Configure session cookie settings
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Register blueprints
for blueprint in blueprints:
    app.register_blueprint(blueprint)

@login_manager.user_loader
def load_user(user_id):
    """
    Load user by ID

    Args:
        user_id (str): User ID

    Returns:
        User: User object if found, None otherwise
    """
    return User.get_user(user_id)

if __name__ == '__main__':
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
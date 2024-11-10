import os
from flask import Blueprint, Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from dotenv import load_dotenv
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)

# Secret key loaded from env
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Password Encryption
bcrypt = Bcrypt(app)

# Login Manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Enable CORS for all routes
# Requires for Swagger docs
CORS(app)

# APIs
from .api import api_bp
app.register_blueprint(api_bp, url_prefix='/api')

# Swagger UI setup
SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'  # Path to your swagger.json file

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "User API",  
        'docExpansion': 'none',
        'jsonEditor': True,
        'operationsSorter': 'alpha'}
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


# Import routes
from app import routes
from app import routes_auth
from app import routes_user
from app import routes_post

# Admin
from app import routes_admin
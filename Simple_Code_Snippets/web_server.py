import os
import secrets
import logging
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)  # Securely generated secret key
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')  # Use environment variable for DB URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = secrets.token_hex(32) # Securely generated JWT secret key
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600  # Token expires in 1 hour

db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")


# Logging Configuration
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


# Authentication Decorator
def admin_required():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user = get_jwt_identity()
            user = User.query.filter_by(username=current_user).first()
            if not user or user.username != 'admin':  # Basic admin check - enhance as needed
                return jsonify({"msg": "Admin access required"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Routes
@app.route('/')
def index():
    logger.info("Index page accessed")
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password or not email:
        return jsonify({"msg": "Missing username or password or email"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "Username already exists"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Email already exists"}), 400

    new_user = User(username=username, email=email)
    new_user.set_password(password)

    try:
        db.session.add(new_user)
        db.session.commit()
        logger.info(f"User {username} registered successfully")
        return jsonify({"msg": "User created successfully"}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating user: {e}")
        return jsonify({"msg": "Error creating user"}), 500


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=username)
        logger.info(f"User {username} logged in successfully")
        return jsonify(access_token=access_token), 200
    else:
        logger.warning(f"Login failed for user {username}")
        return jsonify({"msg": "Invalid credentials"}), 401

@app.route('/profile')
@jwt_required()
def profile():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    if user:
        return jsonify({"username": user.username, "email": user.email}), 200
    else:
        return jsonify({"msg": "User not found"}), 404


@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@app.route('/admin')
@jwt_required()
@admin_required()
def admin():
    return jsonify(message='Admin access granted!'), 200

@app.route('/api/data', methods=['GET'])
@jwt_required()
def get_data():
    data = {"message": "This is some protected data"}
    return jsonify(data), 200


@app.route('/api/data', methods=['POST'])
@jwt_required()
def create_data():
    data = request.get_json()
    # Process the data (e.g., store in the database)
    logger.info(f"Received data: {data}")
    return jsonify({"message": "Data created successfully", "data": data}), 201

@app.route('/api/data/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_data(item_id):
    data = request.get_json()
    # Update the item with the given ID in the database
    logger.info(f"Updating data with ID {item_id} with data: {data}")
    return jsonify({"message": f"Data with ID {item_id} updated successfully", "data": data}), 200

@app.route('/api/data/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_data(item_id):
    # Delete the item with the given ID from the database
    logger.info(f"Deleting data with ID {item_id}")
    return jsonify({"message": f"Data with ID {item_id} deleted successfully"}), 200

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# Websocket events
@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')
    emit('message', {'data': 'Connected to the server!'})

@socketio.on('message')
def handle_message(data):
    logger.info(f'Received message: {data}')
    emit('message', {'data': data['data']}, broadcast=True)


# Error handling
@app.errorhandler(404)
def not_found_error(error):
    logger.warning(f"404 error: {error}")
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback() # Rollback in case the error was database-related
    logger.error(f"500 error: {error}")
    return render_template('500.html'), 500


if __name__ == '__main__':
    # Create the database tables if they don't exist
    with app.app_context():
        db.create_all()
        # Create an admin user if one doesn't exist
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', email='admin@example.com')
            admin_user.set_password('admin')  # VERY INSECURE DEFAULT PASSWORD - CHANGE IMMEDIATELY!
            db.session.add(admin_user)
            db.session.commit()
            logger.info("Created default admin user")

    # Run the SocketIO app
    socketio.run(app, debug=True, host='0.0.0.0')
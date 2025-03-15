from flask import Flask
from flask_cors import CORS
from datetime import timedelta
import os
from dotenv import load_dotenv
from extensions import db, jwt

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure maximum content length for file uploads (10MB)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

# Configure CORS
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"], 
                                "supports_credentials": True,
                                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                                "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"],
                                "expose_headers": ["Content-Type", "Authorization"],
                                "max_age": 86400}})

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USER', 'root')}:{os.getenv('DB_PASSWORD', '')}@{os.getenv('DB_HOST', 'localhost')}/{os.getenv('DB_NAME', 'lab_scheduling_system')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure JWT
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# Initialize extensions with app
db.init_app(app)
jwt.init_app(app)

# Register blueprints
def register_blueprints():
    from routes.auth_routes import auth_bp
    from routes.user_routes import user_bp
    from routes.schedule_routes import schedule_bp
    from routes.notification_routes import notification_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(schedule_bp, url_prefix='/api/schedules')
    app.register_blueprint(notification_bp, url_prefix='/api/notifications')

# Register blueprints
with app.app_context():
    register_blueprints()

if __name__ == '__main__':
    with app.app_context():
        # Import models here to avoid circular imports
        from models import User, Role, Permission, Semester, Course, Section, LabRoom, Schedule, Notification, ProfilePic
        db.create_all()  # Create database tables
    app.run(debug=True, host='0.0.0.0', port=5000) 
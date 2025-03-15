# Fixing Circular Imports in Flask Applications

This document explains how we fixed the circular import issue in the Lab Class Scheduling System backend.

## The Problem

Circular imports occur when two or more modules import each other, directly or indirectly. In our case, the circular import was happening between:

1. `app.py` - Imports `auth_bp` from `routes/auth_routes.py`
2. `routes/auth_routes.py` - Imports `User` and `Role` from `models.py`
3. `models.py` - Imports `db` from `app.py`

This creates a circular dependency that Python can't resolve, resulting in the error:

```
ImportError: cannot import name 'auth_bp' from partially initialized module 'routes.auth_routes' (most likely due to a circular import)
```

## The Solution

We resolved this issue by:

1. Creating a separate `extensions.py` file to initialize Flask extensions without the app
2. Updating all files to import from `extensions.py` instead of `app.py`
3. Initializing the extensions with the app in `app.py`

### Step 1: Create extensions.py

```python
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# Initialize extensions without app
db = SQLAlchemy()
jwt = JWTManager()
```

### Step 2: Update app.py

```python
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
CORS(app, resources={r"/*": {"origins": "*"}})

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
        from models import User, Role, Permission, Semester, Course, Section, LabRoom, Schedule, Notification
        db.create_all()  # Create database tables
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### Step 3: Update models.py

```python
from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Model definitions...
```

### Step 4: Update route files

Update all route files to import `db` from `extensions.py` instead of `app.py`:

```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Role
from extensions import db
# Rest of the file...
```

## Best Practices to Avoid Circular Imports

1. **Use the Application Factory Pattern**: Create a function that returns a Flask application instance
2. **Separate Extensions**: Initialize extensions without the app and then initialize them with the app later
3. **Lazy Imports**: Import modules inside functions instead of at the module level
4. **Restructure Your Code**: Sometimes the best solution is to reorganize your code to avoid circular dependencies

## References

- [Flask Documentation - Application Factories](https://flask.palletsprojects.com/en/2.3.x/patterns/appfactories/)
- [Flask Documentation - Extensions](https://flask.palletsprojects.com/en/2.3.x/extensions/)
- [Python Documentation - Circular Imports](https://docs.python.org/3/faq/programming.html#what-are-the-best-practices-for-using-import-in-a-module) 
from app import app
from models import User
from werkzeug.security import generate_password_hash, check_password_hash

def verify_user(id_or_email, password):
    with app.app_context():
        # Check if input is email or student ID
        is_email = '@' in id_or_email
        
        # Find user by email or student ID
        if is_email:
            user = User.query.filter_by(email=id_or_email).first()
        else:
            user = User.query.filter_by(student_id=id_or_email).first()
        
        if not user:
            print(f"User with {id_or_email} not found in database")
            return False
        
        # Check password
        if user.verify_password(password):
            print(f"Password verification successful for {user.email}")
            return True
        else:
            print(f"Password verification failed for {user.email}")
            return False

def list_users():
    with app.app_context():
        users = User.query.all()
        print(f"Total users in database: {len(users)}")
        for user in users:
            print(f"ID: {user.student_id}, Email: {user.email}, Name: {user.first_name} {user.last_name}")

if __name__ == "__main__":
    # List all users
    list_users()
    
    # Test admin credentials
    print("\nTesting admin credentials:")
    verify_user("admin@uic.edu.ph", "admin123")
    
    # Test academic coordinator credentials
    print("\nTesting academic coordinator credentials:")
    verify_user("acadcoor@uic.edu.ph", "acadcoor123")
    
    # Test student credentials
    print("\nTesting student credentials:")
    verify_user("student@uic.edu.ph", "student123") 
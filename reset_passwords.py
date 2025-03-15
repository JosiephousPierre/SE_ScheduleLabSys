from app import app
from models import User
from extensions import db
from werkzeug.security import generate_password_hash

def reset_passwords():
    with app.app_context():
        # Get all users
        users = User.query.all()
        print(f"Found {len(users)} users in database")
        
        # Reset passwords
        for user in users:
            original_hash = user.password_hash
            
            if user.email == "admin@uic.edu.ph":
                user.password = "admin123"
                print(f"Reset password for admin: {user.email}")
            
            elif user.email == "acadcoor@uic.edu.ph":
                user.password = "acadcoor123"
                print(f"Reset password for academic coordinator: {user.email}")
            
            elif user.email == "dean@uic.edu.ph":
                user.password = "dean123"
                print(f"Reset password for dean: {user.email}")
            
            elif user.email == "faculty@uic.edu.ph":
                user.password = "faculty123"
                print(f"Reset password for faculty: {user.email}")
            
            elif user.email == "student@uic.edu.ph":
                user.password = "student123"
                print(f"Reset password for student: {user.email}")
            
            # Print hash change
            print(f"  - Old hash: {original_hash}")
            print(f"  - New hash: {user.password_hash}")
            print(f"  - Hash changed: {original_hash != user.password_hash}")
        
        # Commit changes
        db.session.commit()
        print("All passwords have been reset successfully!")

def force_reset_all_passwords():
    """Force reset all passwords by directly setting the password hash"""
    with app.app_context():
        # Get all users
        users = User.query.all()
        
        # Reset passwords with direct hash setting
        for user in users:
            if user.email == "admin@uic.edu.ph":
                password = "admin123"
            elif user.email == "acadcoor@uic.edu.ph":
                password = "acadcoor123"
            elif user.email == "dean@uic.edu.ph":
                password = "dean123"
            elif user.email == "faculty@uic.edu.ph":
                password = "faculty123"
            elif user.email == "student@uic.edu.ph":
                password = "student123"
            else:
                password = "password123"
            
            # Directly set the password hash
            user.password_hash = generate_password_hash(password)
            print(f"Force reset password for {user.email} to '{password}'")
        
        # Commit changes
        db.session.commit()
        print("All passwords have been force reset successfully!")

if __name__ == "__main__":
    print("=== Regular Password Reset ===")
    reset_passwords()
    
    print("\n=== Force Password Reset ===")
    force_reset_all_passwords() 
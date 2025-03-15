from werkzeug.security import generate_password_hash

def generate_hash(password):
    """Generate a password hash using Werkzeug's generate_password_hash function."""
    return generate_password_hash(password)

if __name__ == "__main__":
    # Default passwords for the system
    passwords = {
        "admin": "admin123",
        "acadcoor": "acadcoor123",
        "dean": "dean123",
        "faculty": "faculty123",
        "student": "student123"
    }
    
    print("Generated password hashes for SQL import:")
    print("----------------------------------------")
    
    for user, password in passwords.items():
        hashed = generate_hash(password)
        print(f"User: {user}")
        print(f"Password: {password}")
        print(f"Hash: {hashed}")
        print(f"SQL: INSERT INTO users (student_id, email, password_hash, first_name, last_name) VALUES ('STUDENT_ID', '{user}@uic.edu.ph', '{hashed}', 'First Name', 'Last Name');")
        print("----------------------------------------") 
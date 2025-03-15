import requests
import json

def test_login(id_or_email, password):
    url = "http://localhost:5000/api/auth/login"
    
    # Prepare request data
    data = {
        "id_or_email": id_or_email,
        "password": password
    }
    
    # Send request
    response = requests.post(url, json=data)
    
    # Print results
    print(f"Testing login for {id_or_email}:")
    print(f"  Status code: {response.status_code}")
    
    if response.status_code == 200:
        print("  Login successful!")
        # Print user info
        user_data = response.json().get('user', {})
        print(f"  User: {user_data.get('first_name')} {user_data.get('last_name')}")
        print(f"  Roles: {user_data.get('roles', [])}")
    else:
        print(f"  Login failed: {response.json().get('error', 'Unknown error')}")
    
    print()  # Empty line for readability
    
    return response.status_code == 200

def main():
    print("=== Testing Login API ===\n")
    
    # Test all user accounts
    users = [
        {"id_or_email": "admin@uic.edu.ph", "password": "admin123", "role": "Admin"},
        {"id_or_email": "acadcoor@uic.edu.ph", "password": "acadcoor123", "role": "Academic Coordinator"},
        {"id_or_email": "dean@uic.edu.ph", "password": "dean123", "role": "Dean"},
        {"id_or_email": "faculty@uic.edu.ph", "password": "faculty123", "role": "Faculty"},
        {"id_or_email": "student@uic.edu.ph", "password": "student123", "role": "Student"},
    ]
    
    success_count = 0
    
    for user in users:
        if test_login(user["id_or_email"], user["password"]):
            success_count += 1
    
    # Print summary
    print(f"Login test summary: {success_count}/{len(users)} successful logins")

if __name__ == "__main__":
    main() 
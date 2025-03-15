from app import app
from extensions import db
import pymysql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    # Get database connection details from environment variables
    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD', '')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_name = os.getenv('DB_NAME', 'lab_scheduling_system')
    
    # Connect to the database
    connection = pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )
    
    try:
        with connection.cursor() as cursor:
            # Check if the classification column already exists
            cursor.execute("SHOW COLUMNS FROM users LIKE 'classification'")
            result = cursor.fetchone()
            
            # If the column doesn't exist, add it
            if not result:
                print("Adding classification column to users table...")
                cursor.execute("ALTER TABLE users ADD COLUMN classification VARCHAR(50)")
                connection.commit()
                print("Classification column added successfully!")
            else:
                print("Classification column already exists.")
    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    with app.app_context():
        run_migration() 
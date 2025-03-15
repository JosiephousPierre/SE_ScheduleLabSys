# Connecting Frontend to Backend

This document explains how to connect the Vue.js frontend to the Flask backend for the Lab Class Scheduling System.

## Setup Overview

1. The frontend is built with Vue.js and runs on port 3000
2. The backend is built with Flask and runs on port 5000
3. API requests from the frontend are proxied to the backend
4. Authentication is handled using JWT tokens

## Running the Application

### Start the Backend

1. Make sure you have all the required Python packages installed:
   ```
   pip install -r requirements.txt
   ```

2. Initialize the database (if not already done):
   ```
   python init_db.py
   ```

3. Start the Flask server:
   ```
   python run.py
   ```
   The backend will run on http://localhost:5000

### Start the Frontend

1. Navigate to the frontend directory:
   ```
   cd FrontEnd-LabClass-Scheduling-System-
   ```

2. Install dependencies (if not already done):
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm run dev
   ```
   The frontend will run on http://localhost:3000

## Authentication Flow

1. **Login**: Users enter their ID/email and password on the login page
   - The frontend sends a POST request to `/api/auth/login`
   - The backend validates credentials and returns tokens
   - Tokens are stored in localStorage

2. **Registration**: New users can sign up on the registration page
   - The frontend sends a POST request to `/api/auth/register`
   - The backend creates a new user and returns tokens
   - Tokens are stored in localStorage

3. **Token Refresh**: When the access token expires
   - The frontend sends a POST request to `/api/auth/refresh` with the refresh token
   - The backend validates the refresh token and returns a new access token
   - The new access token is stored in localStorage

4. **Protected Routes**: For authenticated users only
   - The frontend includes the access token in the Authorization header
   - The backend validates the token and allows/denies access

## API Services

The frontend uses the following services to communicate with the backend:

1. **api.js**: Base API configuration with Axios
   - Sets up the base URL
   - Handles token inclusion in requests
   - Manages token refresh on 401 errors

2. **auth.js**: Authentication-related API calls
   - Login
   - Registration
   - Token refresh
   - User profile

## Default User Accounts

The system comes with pre-configured user accounts for testing:

1. **Admin**
   - Email: admin@uic.edu.ph
   - ID: 2200001843
   - Password: admin123

2. **Academic Coordinator**
   - Email: acadcoor@uic.edu.ph
   - ID: 2200012453
   - Password: acadcoor123

3. **Dean**
   - Email: dean@uic.edu.ph
   - ID: 2200453671
   - Password: dean123

4. **Faculty**
   - Email: faculty@uic.edu.ph
   - ID: 2209869313
   - Password: faculty123

5. **Student**
   - Email: student@uic.edu.ph
   - ID: 2200123456
   - Password: student123

## Troubleshooting

1. **CORS Issues**
   - Ensure the backend CORS configuration includes your frontend origin
   - Check that the correct headers are being allowed

2. **Authentication Errors**
   - Verify that tokens are being properly stored in localStorage
   - Check that the Authorization header is correctly formatted

3. **Database Connection**
   - Ensure your MySQL server is running
   - Verify the database credentials in the .env file 
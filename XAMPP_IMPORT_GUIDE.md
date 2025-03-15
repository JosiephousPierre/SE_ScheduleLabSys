# How to Import the SQL File into XAMPP

This guide will walk you through the process of importing the `lab_scheduling_system.sql` file into your XAMPP MySQL database.

## Prerequisites

- XAMPP installed on your computer
- The `lab_scheduling_system.sql` file downloaded to your computer

## Steps to Import the SQL File

### 1. Start XAMPP

1. Open the XAMPP Control Panel
2. Start the Apache and MySQL services by clicking the "Start" buttons next to them
3. Wait until both services show a green status

### 2. Access phpMyAdmin

1. Click on the "Admin" button next to MySQL in the XAMPP Control Panel
   - Alternatively, open your web browser and navigate to `http://localhost/phpmyadmin/`
2. phpMyAdmin should open in your web browser

### 3. Create a New Database (Optional)

The SQL script will create the database automatically, but you can also create it manually:

1. In phpMyAdmin, click on "New" in the left sidebar
2. Enter "lab_scheduling_system" as the database name
3. Select "utf8mb4_general_ci" as the collation
4. Click "Create"

### 4. Import the SQL File

#### Method 1: Using the Import Tab

1. If you created the database manually, select "lab_scheduling_system" from the left sidebar
2. Click on the "Import" tab at the top of the page
3. Click "Choose File" and select the `lab_scheduling_system.sql` file from your computer
4. Scroll down and click the "Import" button at the bottom of the page

#### Method 2: Using the SQL Tab

1. If you created the database manually, select "lab_scheduling_system" from the left sidebar
2. Click on the "SQL" tab at the top of the page
3. Open the `lab_scheduling_system.sql` file in a text editor
4. Copy all the content from the file
5. Paste the content into the SQL query box
6. Click the "Go" button to execute the SQL commands

### 5. Verify the Import

After the import is complete, you should see:

1. The "lab_scheduling_system" database in the left sidebar
2. Several tables inside the database (users, roles, permissions, etc.)
3. Data populated in these tables

## Troubleshooting

### Import Timeout

If you encounter a timeout error during import:

1. Open the `php.ini` file in your XAMPP installation directory (usually in the `php` folder)
2. Find and increase the values for:
   - `max_execution_time`
   - `max_input_time`
   - `memory_limit`
3. Save the file and restart Apache

### SQL Error

If you encounter SQL errors during import:

1. Check the error message for details
2. Common issues include:
   - Syntax errors in the SQL file
   - Incompatible MySQL version
   - Existing tables with the same name

## Next Steps

After successfully importing the database:

1. Configure your Python Flask backend to connect to this database
2. Update the `.env` file with your database credentials if needed
3. Run your backend application

## Default User Credentials

The database comes with these pre-configured users:

1. **System Administrator**
   - Email: admin@uic.edu.ph
   - Password: admin123
   - ID: 2200001843

2. **Academic Coordinator**
   - Email: acadcoor@uic.edu.ph
   - Password: acadcoor123
   - ID: 2200012453

3. **Dean**
   - Email: dean@uic.edu.ph
   - Password: dean123
   - ID: 2200453671

4. **Faculty**
   - Email: faculty@uic.edu.ph
   - Password: faculty123
   - ID: 2209869313

5. **Student**
   - Email: student@uic.edu.ph
   - Password: student123
   - ID: 2200123456 
-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS lab_scheduling_system;
USE lab_scheduling_system;

-- Drop tables if they exist to avoid conflicts
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS schedules;
DROP TABLE IF EXISTS sections;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS lab_rooms;
DROP TABLE IF EXISTS semesters;
DROP TABLE IF EXISTS role_permissions;
DROP TABLE IF EXISTS user_roles;
DROP TABLE IF EXISTS permissions;
DROP TABLE IF EXISTS roles;
DROP TABLE IF EXISTS users;

-- Create users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20) UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create roles table
CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255)
);

-- Create permissions table
CREATE TABLE permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255)
);

-- Create user_roles association table
CREATE TABLE user_roles (
    user_id INT NOT NULL,
    role_id INT NOT NULL,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
);

-- Create role_permissions association table
CREATE TABLE role_permissions (
    role_id INT NOT NULL,
    permission_id INT NOT NULL,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
);

-- Create semesters table
CREATE TABLE semesters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    school_year VARCHAR(20) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create lab_rooms table
CREATE TABLE lab_rooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    capacity INT NOT NULL,
    description VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE
);

-- Create courses table
CREATE TABLE courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    units INT NOT NULL
);

-- Create sections table
CREATE TABLE sections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    program VARCHAR(50) NOT NULL,
    year_level INT NOT NULL
);

-- Create schedules table
CREATE TABLE schedules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    semester_id INT NOT NULL,
    course_id INT NOT NULL,
    section_id INT NOT NULL,
    lab_room_id INT NOT NULL,
    instructor_id INT NOT NULL,
    day_of_week VARCHAR(10) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_lab BOOLEAN DEFAULT TRUE,
    created_by INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (semester_id) REFERENCES semesters(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (section_id) REFERENCES sections(id) ON DELETE CASCADE,
    FOREIGN KEY (lab_room_id) REFERENCES lab_rooms(id) ON DELETE CASCADE,
    FOREIGN KEY (instructor_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
);

-- Create notifications table
CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Insert permissions
INSERT INTO permissions (name, description) VALUES
('full_scheduling_control', 'Can create, update, and delete schedules'),
('approval_oversight', 'Can approve or reject schedules'),
('view_schedules', 'Can view schedules'),
('system_management', 'Can manage system settings and users');

-- Insert roles
INSERT INTO roles (name, description) VALUES
('System Administrator', 'System administrator with full access'),
('Academic Coordinator', 'Academic coordinator responsible for scheduling'),
('Dean', 'Dean with approval and oversight capabilities'),
('Faculty/Staff', 'Faculty or staff member'),
('Student', 'Student with view-only access');

-- Assign permissions to roles
-- System Administrator has all permissions
INSERT INTO role_permissions (role_id, permission_id) VALUES
(1, 1), -- System Administrator - full_scheduling_control
(1, 2), -- System Administrator - approval_oversight
(1, 3), -- System Administrator - view_schedules
(1, 4); -- System Administrator - system_management

-- Academic Coordinator has scheduling and viewing permissions
INSERT INTO role_permissions (role_id, permission_id) VALUES
(2, 1), -- Academic Coordinator - full_scheduling_control
(2, 3); -- Academic Coordinator - view_schedules

-- Dean has approval and viewing permissions
INSERT INTO role_permissions (role_id, permission_id) VALUES
(3, 2), -- Dean - approval_oversight
(3, 3); -- Dean - view_schedules

-- Faculty/Staff has viewing permissions
INSERT INTO role_permissions (role_id, permission_id) VALUES
(4, 3); -- Faculty/Staff - view_schedules

-- Student has viewing permissions
INSERT INTO role_permissions (role_id, permission_id) VALUES
(5, 3); -- Student - view_schedules

-- Insert default users with hashed passwords
-- These are Werkzeug-generated password hashes compatible with Flask-based authentication
INSERT INTO users (student_id, email, password_hash, first_name, last_name) VALUES
('2200001843', 'admin@uic.edu.ph', 'pbkdf2:sha256:260000$7EhtGYKc$d5c795dfd3a49c1c1a8af3a3b23146590e8a2b9c2f9a52aa0d7a8397ec6a5fd5', 'Admin', 'User'),
('2200012453', 'acadcoor@uic.edu.ph', 'pbkdf2:sha256:260000$Hl9Yw0Iy$c9e8c9f4a4e1e3e5e3e5e3e5e3e5e3e5e3e5e3e5e3e5e3e5e3e5e3e5e3e5e3e5', 'Academic', 'Coordinator'),
('2200453671', 'dean@uic.edu.ph', 'pbkdf2:sha256:260000$7EhtGYKc$d5c795dfd3a49c1c1a8af3a3b23146590e8a2b9c2f9a52aa0d7a8397ec6a5fd5', 'Dean', 'User'),
('2209869313', 'faculty@uic.edu.ph', 'pbkdf2:sha256:260000$7EhtGYKc$d5c795dfd3a49c1c1a8af3a3b23146590e8a2b9c2f9a52aa0d7a8397ec6a5fd5', 'Faculty', 'User'),
('2200123456', 'student@uic.edu.ph', 'pbkdf2:sha256:260000$7EhtGYKc$d5c795dfd3a49c1c1a8af3a3b23146590e8a2b9c2f9a52aa0d7a8397ec6a5fd5', 'Student', 'User');

-- Assign roles to users
INSERT INTO user_roles (user_id, role_id) VALUES
(1, 1), -- Admin - System Administrator
(2, 2), -- Academic Coordinator - Academic Coordinator
(3, 3), -- Dean - Dean
(4, 4), -- Faculty - Faculty/Staff
(5, 5); -- Student - Student

-- Insert lab rooms
INSERT INTO lab_rooms (name, capacity, description) VALUES
('L201', 30, 'Computer Laboratory 201'),
('L202', 30, 'Computer Laboratory 202'),
('L203', 30, 'Computer Laboratory 203'),
('L204', 30, 'Computer Laboratory 204'),
('L205', 30, 'Computer Laboratory 205'),
('IOT', 20, 'IOT Laboratory');

-- Insert courses
INSERT INTO courses (code, name, description, units) VALUES
('IT101', 'Introduction to Programming', 'Basic programming concepts and problem-solving techniques', 3),
('IT102', 'Object-Oriented Programming', 'Object-oriented programming concepts and design patterns', 3),
('IT103', 'Data Structures and Algorithms', 'Fundamental data structures and algorithm analysis', 3),
('IT104', 'Database Management Systems', 'Database design, implementation, and management', 3),
('IT105', 'Web Development', 'Web technologies, frameworks, and best practices', 3),
('CS101', 'Computer Science Fundamentals', 'Introduction to computer science principles', 3),
('CS102', 'Computer Architecture', 'Computer organization and architecture', 3),
('CS103', 'Operating Systems', 'Operating system concepts and design', 3);

-- Insert sections
INSERT INTO sections (name, program, year_level) VALUES
('1A', 'BSIT', 1),
('1B', 'BSIT', 1),
('1A', 'BSCS', 1),
('2A', 'BSIT', 2),
('2B', 'BSIT', 2),
('2A', 'BSCS', 2),
('3A', 'BSIT', 3),
('3B', 'BSIT', 3),
('3A', 'BSCS', 3),
('4A', 'BSIT', 4),
('4B', 'BSIT', 4),
('4A', 'BSCS', 4);

-- Insert semesters (using current year)
SET @current_year = YEAR(CURDATE());
INSERT INTO semesters (name, school_year, start_date, end_date, is_active) VALUES
('1st Semester', CONCAT(@current_year, '-', @current_year + 1), CONCAT(@current_year, '-08-01'), CONCAT(@current_year, '-12-20'), TRUE),
('2nd Semester', CONCAT(@current_year, '-', @current_year + 1), CONCAT(@current_year + 1, '-01-10'), CONCAT(@current_year + 1, '-05-31'), FALSE);

-- Create sample schedules
INSERT INTO schedules (semester_id, course_id, section_id, lab_room_id, instructor_id, day_of_week, start_time, end_time, is_lab, created_by) VALUES
(1, 1, 1, 1, 4, 'Monday', '08:00:00', '10:00:00', TRUE, 2),
(1, 2, 4, 2, 4, 'Tuesday', '10:00:00', '12:00:00', TRUE, 2),
(1, 3, 7, 3, 4, 'Wednesday', '13:00:00', '15:00:00', TRUE, 2);

-- Create sample notifications
INSERT INTO notifications (user_id, title, message, is_read) VALUES
(4, 'New Schedule Assigned', 'You have been assigned to teach IT101 for BSIT-1A in L201 on Monday from 08:00 to 10:00.', FALSE),
(4, 'New Schedule Assigned', 'You have been assigned to teach IT102 for BSIT-2A in L202 on Tuesday from 10:00 to 12:00.', FALSE),
(4, 'New Schedule Assigned', 'You have been assigned to teach IT103 for BSIT-3A in L203 on Wednesday from 13:00 to 15:00.', FALSE),
(2, 'System Notification', 'Welcome to the Lab Class Scheduling System! You can now start creating schedules.', FALSE),
(3, 'System Notification', 'Welcome to the Lab Class Scheduling System! You can now review and approve schedules.', FALSE),
(5, 'System Notification', 'Welcome to the Lab Class Scheduling System! You can now view your class schedules.', FALSE); 
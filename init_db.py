from app import app
from extensions import db
from models import User, Role, Permission, LabRoom, Course, Section, Semester
from datetime import datetime, date
import os

def init_db():
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if data already exists
        if Role.query.count() > 0:
            print("Database already initialized. Skipping...")
            return
        
        # Create permissions
        permissions = [
            Permission(name='full_scheduling_control', description='Can create, update, and delete schedules'),
            Permission(name='approval_oversight', description='Can approve or reject schedules'),
            Permission(name='view_schedules', description='Can view schedules'),
            Permission(name='system_management', description='Can manage system settings and users')
        ]
        
        for permission in permissions:
            db.session.add(permission)
        
        # Create roles
        roles = [
            Role(name='System Administrator', description='System administrator with full access'),
            Role(name='Academic Coordinator', description='Academic coordinator responsible for scheduling'),
            Role(name='Dean', description='Dean with approval and oversight capabilities'),
            Role(name='Faculty/Staff', description='Faculty or staff member'),
            Role(name='Student', description='Student with view-only access')
        ]
        
        for role in roles:
            db.session.add(role)
        
        # Commit to get IDs
        db.session.commit()
        
        # Assign permissions to roles
        admin_role = Role.query.filter_by(name='System Administrator').first()
        acad_coor_role = Role.query.filter_by(name='Academic Coordinator').first()
        dean_role = Role.query.filter_by(name='Dean').first()
        faculty_role = Role.query.filter_by(name='Faculty/Staff').first()
        student_role = Role.query.filter_by(name='Student').first()
        
        full_scheduling = Permission.query.filter_by(name='full_scheduling_control').first()
        approval = Permission.query.filter_by(name='approval_oversight').first()
        view = Permission.query.filter_by(name='view_schedules').first()
        system_mgmt = Permission.query.filter_by(name='system_management').first()
        
        # System Administrator has all permissions
        admin_role.permissions.extend([full_scheduling, approval, view, system_mgmt])
        
        # Academic Coordinator has scheduling and viewing permissions
        acad_coor_role.permissions.extend([full_scheduling, view])
        
        # Dean has approval and viewing permissions
        dean_role.permissions.extend([approval, view])
        
        # Faculty/Staff has viewing permissions
        faculty_role.permissions.append(view)
        
        # Student has viewing permissions
        student_role.permissions.append(view)
        
        # Create default admin user
        admin_user = User(
            email='admin@uic.edu.ph',
            student_id='2200001843',
            first_name='Admin',
            last_name='User'
        )
        admin_user.password = 'admin123'  # This will be hashed
        admin_user.roles.append(admin_role)
        
        # Create default academic coordinator
        acad_coor_user = User(
            email='acadcoor@uic.edu.ph',
            student_id='2200012453',
            first_name='Academic',
            last_name='Coordinator'
        )
        acad_coor_user.password = 'acadcoor123'  # This will be hashed
        acad_coor_user.roles.append(acad_coor_role)
        
        # Create default dean
        dean_user = User(
            email='dean@uic.edu.ph',
            student_id='2200453671',
            first_name='Dean',
            last_name='User'
        )
        dean_user.password = 'dean123'  # This will be hashed
        dean_user.roles.append(dean_role)
        
        # Create default faculty
        faculty_user = User(
            email='faculty@uic.edu.ph',
            student_id='2209869313',
            first_name='Faculty',
            last_name='User'
        )
        faculty_user.password = 'faculty123'  # This will be hashed
        faculty_user.roles.append(faculty_role)
        
        # Create default student
        student_user = User(
            email='student@uic.edu.ph',
            student_id='2200123456',
            first_name='Student',
            last_name='User'
        )
        student_user.password = 'student123'  # This will be hashed
        student_user.roles.append(student_role)
        
        # Add users to database
        db.session.add_all([admin_user, acad_coor_user, dean_user, faculty_user, student_user])
        
        # Create lab rooms
        lab_rooms = [
            LabRoom(name='L201', capacity=30, description='Computer Laboratory 201'),
            LabRoom(name='L202', capacity=30, description='Computer Laboratory 202'),
            LabRoom(name='L203', capacity=30, description='Computer Laboratory 203'),
            LabRoom(name='L204', capacity=30, description='Computer Laboratory 204'),
            LabRoom(name='L205', capacity=30, description='Computer Laboratory 205'),
            LabRoom(name='IOT', capacity=20, description='IOT Laboratory')
        ]
        
        db.session.add_all(lab_rooms)
        
        # Create courses
        courses = [
            Course(code='IT101', name='Introduction to Programming', units=3),
            Course(code='IT102', name='Object-Oriented Programming', units=3),
            Course(code='IT103', name='Data Structures and Algorithms', units=3),
            Course(code='IT104', name='Database Management Systems', units=3),
            Course(code='IT105', name='Web Development', units=3),
            Course(code='CS101', name='Computer Science Fundamentals', units=3),
            Course(code='CS102', name='Computer Architecture', units=3),
            Course(code='CS103', name='Operating Systems', units=3)
        ]
        
        db.session.add_all(courses)
        
        # Create sections
        sections = [
            Section(name='1A', program='BSIT', year_level=1),
            Section(name='1B', program='BSIT', year_level=1),
            Section(name='1A', program='BSCS', year_level=1),
            Section(name='2A', program='BSIT', year_level=2),
            Section(name='2B', program='BSIT', year_level=2),
            Section(name='2A', program='BSCS', year_level=2),
            Section(name='3A', program='BSIT', year_level=3),
            Section(name='3B', program='BSIT', year_level=3),
            Section(name='3A', program='BSCS', year_level=3),
            Section(name='4A', program='BSIT', year_level=4),
            Section(name='4B', program='BSIT', year_level=4),
            Section(name='4A', program='BSCS', year_level=4)
        ]
        
        db.session.add_all(sections)
        
        # Create semesters
        current_year = datetime.now().year
        semesters = [
            Semester(
                name='1st Semester',
                school_year=f'{current_year}-{current_year+1}',
                start_date=date(current_year, 8, 1),
                end_date=date(current_year, 12, 20),
                is_active=True
            ),
            Semester(
                name='2nd Semester',
                school_year=f'{current_year}-{current_year+1}',
                start_date=date(current_year+1, 1, 10),
                end_date=date(current_year+1, 5, 31),
                is_active=False
            )
        ]
        
        db.session.add_all(semesters)
        
        # Commit all changes
        db.session.commit()
        
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db() 
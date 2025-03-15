from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from models import User, Schedule, Semester, Course, Section, LabRoom, Notification
from extensions import db
from datetime import datetime, time
from functools import wraps

schedule_bp = Blueprint('schedules', __name__)

# Custom decorator to check if user has scheduling permissions
def scheduling_permission_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user or not (user.has_role('Academic Coordinator') or user.has_role('System Administrator')):
                return jsonify({'error': 'Scheduling permission required'}), 403
            
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e)}), 401
    
    return wrapper

# Custom JWT required decorator with better error handling
def jwt_required_custom(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e)}), 401
    
    return wrapper

@schedule_bp.route('/', methods=['GET'])
@jwt_required_custom
def get_all_schedules():
    # Get query parameters
    semester_id = request.args.get('semester_id')
    day_of_week = request.args.get('day_of_week')
    section_id = request.args.get('section_id')
    lab_room_id = request.args.get('lab_room_id')
    
    # Start with base query
    query = Schedule.query
    
    # Apply filters if provided
    if semester_id:
        # Handle the 'new' special case
        if semester_id == 'new':
            return jsonify([]), 200
        query = query.filter_by(semester_id=semester_id)
    
    if day_of_week:
        query = query.filter_by(day_of_week=day_of_week)
    
    if section_id:
        query = query.filter_by(section_id=section_id)
    
    if lab_room_id:
        query = query.filter_by(lab_room_id=lab_room_id)
    
    # Execute query
    schedules = query.all()
    
    return jsonify([schedule.to_dict() for schedule in schedules]), 200

@schedule_bp.route('/<int:schedule_id>', methods=['GET'])
@jwt_required_custom
def get_schedule(schedule_id):
    schedule = Schedule.query.get(schedule_id)
    
    if not schedule:
        return jsonify({'error': 'Schedule not found'}), 404
    
    return jsonify(schedule.to_dict()), 200

@schedule_bp.route('/', methods=['POST'])
@jwt_required_custom
@scheduling_permission_required
def create_schedule():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['semester_id', 'course_id', 'section_id', 'lab_room_id', 
                       'instructor_id', 'day_of_week', 'start_time', 'end_time', 'is_lab']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Parse time strings to time objects
    try:
        start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        end_time = datetime.strptime(data['end_time'], '%H:%M').time()
    except ValueError:
        return jsonify({'error': 'Invalid time format. Use HH:MM format.'}), 400
    
    # Validate time range
    if start_time >= end_time:
        return jsonify({'error': 'Start time must be before end time'}), 400
    
    # Check for schedule conflicts
    conflicts = Schedule.query.filter_by(
        semester_id=data['semester_id'],
        day_of_week=data['day_of_week'],
        lab_room_id=data['lab_room_id']
    ).all()
    
    for conflict in conflicts:
        if (start_time < conflict.end_time and end_time > conflict.start_time):
            return jsonify({
                'error': 'Schedule conflict detected',
                'conflicting_schedule': conflict.to_dict()
            }), 409
    
    # Check for section conflicts (same section scheduled at the same time)
    section_conflicts = Schedule.query.filter_by(
        semester_id=data['semester_id'],
        day_of_week=data['day_of_week'],
        section_id=data['section_id']
    ).all()
    
    for conflict in section_conflicts:
        if (start_time < conflict.end_time and end_time > conflict.start_time):
            return jsonify({
                'error': 'Section schedule conflict detected',
                'conflicting_schedule': conflict.to_dict()
            }), 409
    
    # Check for instructor conflicts (same instructor scheduled at the same time)
    instructor_conflicts = Schedule.query.filter_by(
        semester_id=data['semester_id'],
        day_of_week=data['day_of_week'],
        instructor_id=data['instructor_id']
    ).all()
    
    for conflict in instructor_conflicts:
        if (start_time < conflict.end_time and end_time > conflict.start_time):
            return jsonify({
                'error': 'Instructor schedule conflict detected',
                'conflicting_schedule': conflict.to_dict()
            }), 409
    
    # Create new schedule
    current_user_id = get_jwt_identity()
    
    new_schedule = Schedule(
        semester_id=data['semester_id'],
        course_id=data['course_id'],
        section_id=data['section_id'],
        lab_room_id=data['lab_room_id'],
        instructor_id=data['instructor_id'],
        day_of_week=data['day_of_week'],
        start_time=start_time,
        end_time=end_time,
        is_lab=data['is_lab'],
        created_by=current_user_id
    )
    
    db.session.add(new_schedule)
    
    # Create notification for the instructor
    instructor = User.query.get(data['instructor_id'])
    course = Course.query.get(data['course_id'])
    section = Section.query.get(data['section_id'])
    lab_room = LabRoom.query.get(data['lab_room_id'])
    
    if instructor and course and section and lab_room:
        notification = Notification(
            user_id=instructor.id,
            title='New Schedule Assigned',
            message=f"You have been assigned to teach {course.code} for {section.program}-{section.name} in {lab_room.name} on {data['day_of_week']} from {data['start_time']} to {data['end_time']}."
        )
        db.session.add(notification)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Schedule created successfully',
        'schedule': new_schedule.to_dict()
    }), 201

@schedule_bp.route('/<int:schedule_id>', methods=['PUT'])
@jwt_required_custom
@scheduling_permission_required
def update_schedule(schedule_id):
    schedule = Schedule.query.get(schedule_id)
    
    if not schedule:
        return jsonify({'error': 'Schedule not found'}), 404
    
    data = request.get_json()
    
    # Update fields if provided
    if 'course_id' in data:
        schedule.course_id = data['course_id']
    
    if 'section_id' in data:
        schedule.section_id = data['section_id']
    
    if 'lab_room_id' in data:
        schedule.lab_room_id = data['lab_room_id']
    
    if 'instructor_id' in data:
        schedule.instructor_id = data['instructor_id']
    
    if 'day_of_week' in data:
        schedule.day_of_week = data['day_of_week']
    
    if 'start_time' in data:
        try:
            schedule.start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        except ValueError:
            return jsonify({'error': 'Invalid start time format. Use HH:MM format.'}), 400
    
    if 'end_time' in data:
        try:
            schedule.end_time = datetime.strptime(data['end_time'], '%H:%M').time()
        except ValueError:
            return jsonify({'error': 'Invalid end time format. Use HH:MM format.'}), 400
    
    if 'is_lab' in data:
        schedule.is_lab = data['is_lab']
    
    # Validate time range
    if schedule.start_time >= schedule.end_time:
        return jsonify({'error': 'Start time must be before end time'}), 400
    
    # Check for schedule conflicts (excluding this schedule)
    conflicts = Schedule.query.filter(
        Schedule.id != schedule_id,
        Schedule.semester_id == schedule.semester_id,
        Schedule.day_of_week == schedule.day_of_week,
        Schedule.lab_room_id == schedule.lab_room_id
    ).all()
    
    for conflict in conflicts:
        if (schedule.start_time < conflict.end_time and schedule.end_time > conflict.start_time):
            return jsonify({
                'error': 'Schedule conflict detected',
                'conflicting_schedule': conflict.to_dict()
            }), 409
    
    # Check for section conflicts
    section_conflicts = Schedule.query.filter(
        Schedule.id != schedule_id,
        Schedule.semester_id == schedule.semester_id,
        Schedule.day_of_week == schedule.day_of_week,
        Schedule.section_id == schedule.section_id
    ).all()
    
    for conflict in section_conflicts:
        if (schedule.start_time < conflict.end_time and schedule.end_time > conflict.start_time):
            return jsonify({
                'error': 'Section schedule conflict detected',
                'conflicting_schedule': conflict.to_dict()
            }), 409
    
    # Check for instructor conflicts
    instructor_conflicts = Schedule.query.filter(
        Schedule.id != schedule_id,
        Schedule.semester_id == schedule.semester_id,
        Schedule.day_of_week == schedule.day_of_week,
        Schedule.instructor_id == schedule.instructor_id
    ).all()
    
    for conflict in instructor_conflicts:
        if (schedule.start_time < conflict.end_time and schedule.end_time > conflict.start_time):
            return jsonify({
                'error': 'Instructor schedule conflict detected',
                'conflicting_schedule': conflict.to_dict()
            }), 409
    
    # Create notification for the instructor if instructor changed
    if 'instructor_id' in data and data['instructor_id'] != schedule.instructor_id:
        instructor = User.query.get(data['instructor_id'])
        course = Course.query.get(schedule.course_id)
        section = Section.query.get(schedule.section_id)
        lab_room = LabRoom.query.get(schedule.lab_room_id)
        
        if instructor and course and section and lab_room:
            notification = Notification(
                user_id=instructor.id,
                title='Schedule Assignment',
                message=f"You have been assigned to teach {course.code} for {section.program}-{section.name} in {lab_room.name} on {schedule.day_of_week} from {schedule.start_time.strftime('%H:%M')} to {schedule.end_time.strftime('%H:%M')}."
            )
            db.session.add(notification)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Schedule updated successfully',
        'schedule': schedule.to_dict()
    }), 200

@schedule_bp.route('/<int:schedule_id>', methods=['DELETE'])
@jwt_required_custom
@scheduling_permission_required
def delete_schedule(schedule_id):
    schedule = Schedule.query.get(schedule_id)
    
    if not schedule:
        return jsonify({'error': 'Schedule not found'}), 404
    
    # Create notification for the instructor
    instructor = User.query.get(schedule.instructor_id)
    course = Course.query.get(schedule.course_id)
    section = Section.query.get(schedule.section_id)
    
    if instructor and course and section:
        notification = Notification(
            user_id=instructor.id,
            title='Schedule Cancelled',
            message=f"Your schedule for {course.code} with {section.program}-{section.name} on {schedule.day_of_week} from {schedule.start_time.strftime('%H:%M')} to {schedule.end_time.strftime('%H:%M')} has been cancelled."
        )
        db.session.add(notification)
    
    db.session.delete(schedule)
    db.session.commit()
    
    return jsonify({'message': 'Schedule deleted successfully'}), 200

@schedule_bp.route('/semesters', methods=['GET'])
@jwt_required_custom
def get_all_semesters():
    semesters = Semester.query.all()
    return jsonify([semester.to_dict() for semester in semesters]), 200

@schedule_bp.route('/semesters', methods=['POST'])
@jwt_required_custom
@scheduling_permission_required
def create_semester():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'school_year', 'start_date', 'end_date']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Parse date strings to date objects
    try:
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD format.'}), 400
    
    # Validate date range
    if start_date >= end_date:
        return jsonify({'error': 'Start date must be before end date'}), 400
    
    # Create new semester
    new_semester = Semester(
        name=data['name'],
        school_year=data['school_year'],
        start_date=start_date,
        end_date=end_date,
        is_active=data.get('is_active', True)
    )
    
    db.session.add(new_semester)
    db.session.commit()
    
    return jsonify({
        'message': 'Semester created successfully',
        'semester': new_semester.to_dict()
    }), 201

@schedule_bp.route('/courses', methods=['GET'])
@jwt_required_custom
def get_all_courses():
    # Check if code parameter is provided
    code = request.args.get('code')
    
    if code:
        # Find course by code
        course = Course.query.filter_by(code=code).first()
        
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        return jsonify(course.to_dict()), 200
    
    # Get all courses
    courses = Course.query.all()
    return jsonify([course.to_dict() for course in courses]), 200

@schedule_bp.route('/courses', methods=['POST'])
@jwt_required_custom
@scheduling_permission_required
def create_course():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['code', 'name', 'units']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Check if course code already exists
    if Course.query.filter_by(code=data['code']).first():
        return jsonify({'error': 'Course code already exists'}), 400
    
    # Create new course
    new_course = Course(
        code=data['code'],
        name=data['name'],
        description=data.get('description', ''),
        units=data['units']
    )
    
    db.session.add(new_course)
    db.session.commit()
    
    return jsonify({
        'message': 'Course created successfully',
        'course': new_course.to_dict()
    }), 201

@schedule_bp.route('/sections', methods=['GET'])
@jwt_required_custom
def get_all_sections():
    # Check if program and name parameters are provided
    program = request.args.get('program')
    name = request.args.get('name')
    
    if program and name:
        # Find section by program and name
        section = Section.query.filter_by(program=program, name=name).first()
        
        if not section:
            return jsonify({'error': 'Section not found'}), 404
        
        return jsonify(section.to_dict()), 200
    
    # Get all sections
    sections = Section.query.all()
    return jsonify([section.to_dict() for section in sections]), 200

@schedule_bp.route('/sections', methods=['POST'])
@jwt_required_custom
@scheduling_permission_required
def create_section():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'program', 'year_level']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Create new section
    new_section = Section(
        name=data['name'],
        program=data['program'],
        year_level=data['year_level']
    )
    
    db.session.add(new_section)
    db.session.commit()
    
    return jsonify({
        'message': 'Section created successfully',
        'section': new_section.to_dict()
    }), 201

@schedule_bp.route('/lab-rooms', methods=['GET'])
@jwt_required_custom
def get_all_lab_rooms():
    # Check if name parameter is provided
    name = request.args.get('name')
    
    if name:
        # Find lab room by name
        lab_room = LabRoom.query.filter_by(name=name).first()
        
        if not lab_room:
            return jsonify({'error': 'Lab room not found'}), 404
        
        return jsonify(lab_room.to_dict()), 200
    
    # Get all lab rooms
    lab_rooms = LabRoom.query.all()
    return jsonify([lab_room.to_dict() for lab_room in lab_rooms]), 200

@schedule_bp.route('/lab-rooms', methods=['POST'])
@jwt_required_custom
@scheduling_permission_required
def create_lab_room():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'capacity']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Check if lab room name already exists
    if LabRoom.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Lab room name already exists'}), 400
    
    # Create new lab room
    new_lab_room = LabRoom(
        name=data['name'],
        capacity=data['capacity'],
        description=data.get('description', ''),
        is_active=data.get('is_active', True)
    )
    
    db.session.add(new_lab_room)
    db.session.commit()
    
    return jsonify({
        'message': 'Lab room created successfully',
        'lab_room': new_lab_room.to_dict()
    }), 201 
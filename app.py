#app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Class, Attendance
from flask import jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import send_file
from exports import generate_class_attendance_pdf, generate_student_attendance_pdf




app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['EMAIL_SENDER'] = 'edunet657@gmail.com'  # Replace with your email
app.config['EMAIL_PASSWORD'] = 'yakb ysyg ogkm aoqz'  # Replace with your email password or app password
from datetime import datetime



db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        print(f"[DEBUG] Register attempt: name={name}, email={email}, role={role}")

        try:
            user = User.query.filter_by(email=email).first()
            if user:
                if request.headers.get('Accept') == 'application/json':
                    return jsonify({'error': 'Email already exists'}), 400
                flash('Email already exists')
                return redirect(url_for('register'))

            new_user = User(name=name, email=email, password=generate_password_hash(password, method='sha256'), role=role)
            db.session.add(new_user)
            db.session.commit()

            if request.headers.get('Accept') == 'application/json':
                return jsonify({'message': 'Registration successful'}), 200

            flash('Registration successful')
            return redirect(url_for('login'))
        except Exception as e:
            print(f"[ERROR] Registration error: {e}")
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'error': 'Server error'}), 500
            flash('Server error')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print(f"[DEBUG] Login attempt: email={email}")

        try:
            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                if request.headers.get('Accept') == 'application/json':
                    return jsonify({'message': 'Login successful'}), 200
                return redirect(url_for('dashboard'))

            if request.headers.get('Accept') == 'application/json':
                return jsonify({'error': 'Invalid email or password'}), 401
            flash('Invalid email or password')
        except Exception as e:
            print(f"[ERROR] Login error: {e}")
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'error': 'Server error'}), 500
            flash('Server error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'teacher':
        classes = Class.query.filter_by(teacher_id=current_user.id).all()
        return render_template('dashboard.html', classes=classes)
    else:
        return redirect(url_for('student_dashboard'))


# --- API endpoints for React frontend ---
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
    return response


@app.route('/api/classes')
@login_required
def api_classes():
    # Returns classes for the current user (teacher sees their classes)
    if current_user.role == 'teacher':
        classes = Class.query.filter_by(teacher_id=current_user.id).all()
    else:
        classes = current_user.classes

    result = []
    for c in classes:
        result.append({
            'id': c.id,
            'name': c.name,
            'students': [{'id': s.id, 'name': s.name, 'email': s.email} for s in c.students]
        })
    return jsonify(result)


@app.route('/api/student_dashboard')
@login_required
def api_student_dashboard():
    if current_user.role != 'student':
        return jsonify({'error': 'Only students'}), 403

    classes = [{'id': c.id, 'name': c.name} for c in current_user.classes]
    attendance_records = Attendance.query.filter_by(student_id=current_user.id).all()
    records = [{'date': r.date.strftime('%Y-%m-%d'), 'class_name': r.class_.name, 'status': r.status} for r in attendance_records]

    total = len(attendance_records)
    present = sum(1 for r in attendance_records if r.status == 'present')
    absent = total - present
    rate = (present / total) * 100 if total > 0 else 0

    return jsonify({
        'classes': classes,
        'attendance_records': records,
        'stats': {'total': total, 'present': present, 'absent': absent, 'rate': rate}
    })


@app.route('/api/attendance_history/<int:class_id>')
@login_required
def api_attendance_history(class_id):
    # Only teachers for this class or students in it should access — keep simple for demo
    class_obj = Class.query.get_or_404(class_id)
    attendance_records = Attendance.query.filter_by(class_id=class_id).all()

    # aggregate per student
    student_stats = []
    for student in class_obj.students:
        student_records = [r for r in attendance_records if r.student_id == student.id]
        absent_count = sum(1 for r in student_records if r.status == 'absent')
        present_count = sum(1 for r in student_records if r.status == 'present')
        rate = (present_count / len(student_records) * 100) if student_records else 0
        records = [{'date': r.date.strftime('%Y-%m-%d'), 'status': r.status} for r in student_records]
        student_stats.append({
            'id': student.id,
            'name': student.name,
            'absent_count': absent_count,
            'present_count': present_count,
            'attendance_rate': rate,
            'records': records
        })

    return jsonify(student_stats)


@app.route('/api/class/<int:class_id>')
@login_required
def api_class_detail(class_id):
    class_obj = Class.query.get_or_404(class_id)
    data = {
        'id': class_obj.id,
        'name': class_obj.name,
        'students': [{'id': s.id, 'name': s.name, 'email': s.email} for s in class_obj.students]
    }
    return jsonify(data)


@app.route('/api/mark_attendance/<int:class_id>', methods=['POST'])
@login_required
def api_mark_attendance(class_id):
    # Expect JSON payload: { date: 'YYYY-MM-DD', records: [{student_id: x, status: 'present'|'absent'}] }
    payload = request.get_json()
    if not payload:
        return jsonify({'error': 'Invalid JSON'}), 400

    date_str = payload.get('date')
    records = payload.get('records', [])
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.today()
    except Exception:
        return jsonify({'error': 'Invalid date'}), 400

    for r in records:
        student_id = r.get('student_id')
        status = r.get('status')
        if student_id is None or status not in ('present', 'absent'):
            continue
        attendance = Attendance(class_id=class_id, student_id=student_id, status=status, attendance_date=date_obj)
        db.session.add(attendance)

    db.session.commit()
    return jsonify({'message': 'Attendance saved'}), 200


@app.route('/debug/session')
def debug_session():
    if current_user.is_authenticated:
        return jsonify({'authenticated': True, 'user': {'id': current_user.id, 'email': current_user.email, 'name': current_user.name, 'role': current_user.role}})
    return jsonify({'authenticated': False})


class_stack = []

@app.route('/create_class', methods=['GET', 'POST'])
@login_required
def create_class():
    if current_user.role != 'teacher':
        flash('Only teachers can create classes')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        class_name = request.form['class_name']
        new_class = Class(name=class_name, teacher_id=current_user.id)
        class_stack.append(new_class)
        
        while class_stack:
            class_to_save = class_stack.pop()
            db.session.add(class_to_save)
        
        db.session.commit()
        flash('Class created successfully')
        return redirect(url_for('dashboard'))
    
    return render_template('create_class.html')

@app.route('/student_dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        flash('Only students can access this dashboard')
        return redirect(url_for('dashboard'))
    
    # Get all classes the student is enrolled in
    classes = current_user.classes
    
    # Get attendance records for the student
    attendance_records = Attendance.query.filter_by(student_id=current_user.id).all()
    
    # Calculate attendance statistics
    total_classes = len(attendance_records)
    present_count = sum(1 for record in attendance_records if record.status == 'present')
    absent_count = total_classes - present_count
    attendance_rate = (present_count / total_classes) * 100 if total_classes > 0 else 0
    
    return render_template('student_dashboard.html', 
                           classes=classes, 
                           attendance_records=attendance_records,
                           total_classes=total_classes,
                           present_count=present_count,
                           absent_count=absent_count,
                           attendance_rate=attendance_rate)

@app.route('/export/student_attendance/<int:student_id>')
@login_required
def export_student_attendance(student_id):
    if current_user.role != 'student' and current_user.id != student_id:
        flash('You can only export your own attendance records')
        return redirect(url_for('student_dashboard'))
    
    attendance_records = Attendance.query.filter_by(student_id=student_id).all()
    pdf_file = generate_student_attendance_pdf(
        current_user.name, 
        student_id, 
        attendance_records
    )
    
    return send_file(
        pdf_file,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'attendance_{current_user.name}.pdf'
    )

@app.route('/add_student/<int:class_id>', methods=['POST'])
@login_required
def add_student(class_id):
    if current_user.role != 'teacher':
        flash('Only teachers can add students')
        return redirect(url_for('dashboard'))
    
    student_email = request.form['student_email']
    student = User.query.filter_by(email=student_email, role='student').first()
    
    if not student:
        flash('Student not found')
        return redirect(url_for('dashboard'))
    
    class_obj = Class.query.get(class_id)
    if student not in class_obj.students:
        class_obj.students.append(student)
        db.session.commit()
        flash('Student added to class')
    else:
        flash('Student already in class')
    
    return redirect(url_for('dashboard'))

from collections import deque
from threading import Thread
import mailer
import os
try:
    from redis import Redis
    from rq import Queue
    redis_conn = Redis(host=os.environ.get('REDIS_HOST','localhost'), port=int(os.environ.get('REDIS_PORT','6379')))
    rq_queue = Queue('default', connection=redis_conn)
except Exception:
    redis_conn = None
    rq_queue = None

attendance_queue = deque()

@app.route('/mark_attendance/<int:class_id>', methods=['GET', 'POST'])
@login_required
def mark_attendance(class_id):
    if current_user.role != 'teacher':
        flash('Only teachers can mark attendance')
        return redirect(url_for('dashboard'))
    
    class_obj = Class.query.get(class_id)
    
    if request.method == 'POST':
        date_str = request.form['date']
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')  # Convert string to datetime object
        absent_students = []
        for student in class_obj.students:
            status = request.form.get(f'status_{student.id}')
            attendance = Attendance(
                class_id=class_id,
                student_id=student.id,
                status=status,
                attendance_date=date_obj  # Make sure this matches the model field
            )
            attendance_queue.append(attendance)
            if status == 'absent':
                absent_students.append(student)        
        while attendance_queue:
            attendance = attendance_queue.popleft()
            db.session.add(attendance)
        
        db.session.commit()
        
        # Send emails to absent students (do this asynchronously so request isn't blocked)
        for student in absent_students:
            try:
                if rq_queue:
                    # If RQ is configured, keep previous behavior (queue a job that will call mailer.send_email_sendgrid)
                    rq_queue.enqueue('mailer.send_email_sendgrid', student.email, f"Absence Notification - {class_obj.name}", f"You were marked absent for {class_obj.name} on {date_str}.")
                else:
                    # Use the centralized simple SMTP mailer in a background thread to avoid blocking the request
                    Thread(target=mailer.send_absence_email_simple, args=(student.email, class_obj.name, date_str), daemon=True).start()
            except Exception as e:
                app.logger.error(f"Failed to enqueue/send email for {student.email}: {e}")
        
        flash('Attendance marked successfully and absence emails sent')
        return redirect(url_for('dashboard'))
    
    return render_template('mark_attendance.html', class_obj=class_obj)
# Email sending is handled by mailer.send_absence_email_simple in background threads when RQ is not configured.


@app.route('/remove_student/<int:class_id>/<int:student_id>', methods=['POST'])
@login_required
def remove_student(class_id, student_id):
    if current_user.role != 'teacher':
        flash('Only teachers can remove students')
        return redirect(url_for('dashboard'))
    
    class_obj = Class.query.get(class_id)
    student = User.query.get(student_id)
    
    if class_obj and student and student in class_obj.students:
        class_obj.students.remove(student)
        db.session.commit()
        flash('Student removed from class')
    else:
        flash('Student or class not found')
    
    return redirect(url_for('dashboard'))



@app.route('/attendance_history/<int:class_id>')
@login_required
def attendance_history(class_id):
    if current_user.role != 'teacher':
        flash('Only teachers can view attendance history')
        return redirect(url_for('dashboard'))
    
    class_obj = Class.query.get(class_id)
    sort_by = request.args.get('sort_by', 'date')  # Default sort by date
    
    # Get all attendance records for the class
    attendance_records = Attendance.query.filter_by(class_id=class_id).all()
    
    # Create a dictionary to store student attendance statistics
    student_stats = {}
    for student in class_obj.students:
        student_records = [r for r in attendance_records if r.student_id == student.id]
        absent_count = sum(1 for r in student_records if r.status == 'absent')
        present_count = sum(1 for r in student_records if r.status == 'present')
        attendance_rate = (present_count / len(student_records) * 100) if student_records else 0
        
        student_stats[student.id] = {
            'name': student.name,
            'absent_count': absent_count,
            'present_count': present_count,
            'attendance_rate': attendance_rate,
            'records': student_records
        }
    
    # Sort the statistics based on selected criteria
    if sort_by == 'absent':
        sorted_stats = dict(sorted(student_stats.items(), 
                                 key=lambda x: x[1]['absent_count'], 
                                 reverse=True))
    elif sort_by == 'present':
        sorted_stats = dict(sorted(student_stats.items(), 
                                 key=lambda x: x[1]['present_count'], 
                                 reverse=True))
    elif sort_by == 'rate':
        sorted_stats = dict(sorted(student_stats.items(), 
                                 key=lambda x: x[1]['attendance_rate'], 
                                 reverse=True))
    else:  # sort by name
        sorted_stats = dict(sorted(student_stats.items(), 
                                 key=lambda x: x[1]['name']))
    
    return render_template('attendance_history.html', 
                         class_obj=class_obj,
                         student_stats=sorted_stats,
                         sort_by=sort_by)

@app.route('/export/class_attendance/<int:class_id>')
@login_required
def export_class_attendance(class_id):
    if current_user.role != 'teacher':
        flash('Only teachers can export class attendance')
        return redirect(url_for('dashboard'))
    
    class_obj = Class.query.get_or_404(class_id)
    attendance_records = Attendance.query.filter_by(class_id=class_id).all()
    
    pdf_file = generate_class_attendance_pdf(
        class_obj.name,
        class_id,
        attendance_records
    )
    
    return send_file(
        pdf_file,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'class_attendance_{class_obj.name}.pdf'
    )


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False, port=5001)


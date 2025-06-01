from flask import Flask, render_template, request, redirect, flash, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"  

# SQLite DB setup
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = generate_password_hash("admin123")

# Database model for admission form
class Admission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    child_name = db.Column(db.String(100), nullable=False)
    child_age = db.Column(db.Integer, nullable=False)
    program = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text)
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Pending')  # Status: Pending, Approved, Rejected

# Create the database (only once)
def create_db():
    with app.app_context():
        db.create_all()

# ------------------ ROUTES ------------------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/programs')
def programs():
    return render_template('programs.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# ------------------ ADMISSION FORM ------------------

@app.route('/admission', methods=['GET', 'POST'])
def admission():
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']
            child_name = request.form['child_name']
            child_age = int(request.form['child_age'])
            program = request.form['program']
            message = request.form.get('message', '')

            if child_age < 2 or child_age > 6:
                flash("Child age must be between 2 and 6 years", "error")
                return redirect('/admission')

            new_entry = Admission(
                name=name,
                email=email,
                phone=phone,
                child_name=child_name,
                child_age=child_age,
                program=program,
                message=message
            )

            db.session.add(new_entry)
            db.session.commit()
            flash("✅ Admission form submitted successfully!", "success")
            return redirect('/')
        
        except Exception as e:
            db.session.rollback()
            flash(f"❌ Error: {str(e)}", "error")
            return redirect('/admission')

    programs = ['Play Group (2-3 years)', 'Nursery (3-4 years)', 'LKG (4-5 years)', 'UKG (5-6 years)']
    return render_template('admission.html', programs=programs)

# ------------------ ADMIN LOGIN & LOGOUT ------------------

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD, password):
            session['admin_logged_in'] = True
            flash("Welcome, Admin!", "success")
            return redirect(url_for('admin_dashboard'))
        else:
            flash("❌ Invalid credentials", "error")

    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash("Logged out successfully", "info")
    return redirect(url_for('home'))

# ------------------ ADMIN DASHBOARD ------------------

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    admissions = Admission.query.order_by(Admission.submission_date.desc()).all()
    return render_template('admin_dashboard.html', admissions=admissions)

# ------------------ ADMIN ACTIONS ------------------

@app.route('/admin/update_status/<int:id>', methods=['POST'])
def update_status(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    entry = Admission.query.get_or_404(id)
    new_status = request.form['status']

    if new_status in ['Pending', 'Approved', 'Rejected']:
        entry.status = new_status
        db.session.commit()
        flash(f"Status updated to {new_status} for {entry.child_name}", "success")
    else:
        flash("Invalid status value", "error")

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete/<int:id>')
def delete_admission(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    entry = Admission.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()
    flash(f"Deleted admission for {entry.child_name}", "success")
    return redirect(url_for('admin_dashboard'))

# ------------------ START APP ------------------

if __name__ == '__main__':
    create_db()
    app.run(debug=True)


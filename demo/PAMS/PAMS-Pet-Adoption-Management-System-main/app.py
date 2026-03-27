"""
app.py — PAMS (Pet Adoption Management System)
Flask application with CRUD, search/filter, admin auth, CSV export, flash messages.
"""

import csv
import hashlib
import io
import re
from datetime import date
from functools import wraps

from flask import (Flask, render_template, request, redirect, url_for,
                   flash, session, Response, g)

from database import init_db, get_db_connection

# ── App setup ────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = "pams-dev-secret-change-in-prod"   # use os.environ in production

# Initialise DB on first startup
with app.app_context():
    init_db()


# ── DB connection per request ────────────────────────────────────────────────
def get_db():
    if 'db' not in g:
        g.db = get_db_connection()
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


# ── Helpers ───────────────────────────────────────────────────────────────────
def admin_required(f):
    """Decorator: redirect to login if not authenticated."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash("Please log in to access the admin panel.", "warning")
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated


def validate_email(email: str) -> bool:
    return bool(re.match(r'^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$', email))

def validate_phone(phone: str) -> bool:
    return bool(re.match(r'^[\d\s\-\+\(\)]{7,15}$', phone))


# ── Public routes ─────────────────────────────────────────────────────────────

@app.route('/')
def home():
    db = get_db()
    stats = {
        'total':    db.execute("SELECT COUNT(*) FROM Pets").fetchone()[0],
        'available':db.execute("SELECT COUNT(*) FROM Pets WHERE status='Available'").fetchone()[0],
        'adopted':  db.execute("SELECT COUNT(*) FROM Pets WHERE status='Adopted'").fetchone()[0],
        'pending':  db.execute("SELECT COUNT(*) FROM Adoption_Requests WHERE status='Pending'").fetchone()[0],
    }
    recent = db.execute(
        "SELECT * FROM Pets WHERE status='Available' ORDER BY added_on DESC LIMIT 3"
    ).fetchall()
    return render_template('home.html', stats=stats, recent=recent)


@app.route('/pets')
def pets():
    db = get_db()
    species_filter = request.args.get('species', '').strip()
    search_query   = request.args.get('q', '').strip()
    gender_filter  = request.args.get('gender', '').strip()

    sql    = "SELECT * FROM Pets WHERE status='Available'"
    params = []

    if species_filter:
        sql += " AND species = ?"
        params.append(species_filter)
    if gender_filter:
        sql += " AND gender = ?"
        params.append(gender_filter)
    if search_query:
        sql += " AND (name LIKE ? OR breed LIKE ? OR description LIKE ?)"
        like = f"%{search_query}%"
        params.extend([like, like, like])

    sql += " ORDER BY added_on DESC"
    pets_list = db.execute(sql, params).fetchall()

    species_list = [r[0] for r in db.execute(
        "SELECT DISTINCT species FROM Pets WHERE status='Available' ORDER BY species"
    ).fetchall()]

    return render_template('pets.html', pets=pets_list,
                           species_list=species_list,
                           active_species=species_filter,
                           active_gender=gender_filter,
                           search_query=search_query)


@app.route('/pet/<int:pet_id>')
def pet_detail(pet_id):
    db  = get_db()
    pet = db.execute("SELECT * FROM Pets WHERE pet_id = ?", (pet_id,)).fetchone()
    if not pet:
        flash("Pet not found.", "danger")
        return redirect(url_for('pets'))
    return render_template('pet_detail.html', pet=pet)


@app.route('/adopt/<int:pet_id>', methods=['GET', 'POST'])
def adopt(pet_id):
    db  = get_db()
    pet = db.execute("SELECT * FROM Pets WHERE pet_id = ? AND status='Available'",
                     (pet_id,)).fetchone()
    if not pet:
        flash("This pet is no longer available for adoption.", "warning")
        return redirect(url_for('pets'))

    if request.method == 'POST':
        name    = request.form.get('name',    '').strip()
        email   = request.form.get('email',   '').strip()
        phone   = request.form.get('phone',   '').strip()
        address = request.form.get('address', '').strip()
        notes   = request.form.get('notes',   '').strip()

        errors = []
        if not name:    errors.append("Name is required.")
        if not email or not validate_email(email):
            errors.append("A valid email address is required.")
        if phone and not validate_phone(phone):
            errors.append("Phone number format is invalid.")
        if not address: errors.append("Address is required.")

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template('adopt.html', pet=pet, pet_id=pet_id)

        try:
            # Upsert user by email (re-use existing record if exists)
            db.execute(
                "INSERT OR IGNORE INTO Users (name, email, phone, address) VALUES (?,?,?,?)",
                (name, email, phone, address)
            )
            db.execute(
                "UPDATE Users SET name=?, phone=?, address=? WHERE email=?",
                (name, phone, address, email)
            )
            user_id = db.execute(
                "SELECT user_id FROM Users WHERE email=?", (email,)
            ).fetchone()['user_id']

            # Check for duplicate request
            existing = db.execute(
                "SELECT request_id FROM Adoption_Requests WHERE user_id=? AND pet_id=?",
                (user_id, pet_id)
            ).fetchone()
            if existing:
                flash("You have already submitted a request for this pet.", "warning")
                return redirect(url_for('pets'))

            db.execute(
                "INSERT INTO Adoption_Requests (user_id, pet_id, request_date, notes) VALUES (?,?,?,?)",
                (user_id, pet_id, str(date.today()), notes)
            )
            db.execute("UPDATE Pets SET status='Pending' WHERE pet_id=?", (pet_id,))
            db.commit()
            flash(f"🎉 Your adoption request for {pet['name']} has been submitted!", "success")
            return redirect(url_for('home'))

        except Exception as e:
            db.rollback()
            flash(f"An error occurred: {str(e)}", "danger")

    return render_template('adopt.html', pet=pet, pet_id=pet_id)


# ── Admin auth ────────────────────────────────────────────────────────────────

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        db = get_db()
        admin = db.execute(
            "SELECT * FROM Admin WHERE username=? AND password=?",
            (username, pwd_hash)
        ).fetchone()
        if admin:
            session['admin_logged_in'] = True
            session['admin_username']  = username
            flash(f"Welcome back, {username}!", "success")
            return redirect(url_for('admin_dashboard'))
        flash("Invalid credentials.", "danger")
    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('home'))


# ── Admin panel ───────────────────────────────────────────────────────────────

@app.route('/admin')
@admin_required
def admin_dashboard():
    db = get_db()
    stats = {
        'total':     db.execute("SELECT COUNT(*) FROM Pets").fetchone()[0],
        'available': db.execute("SELECT COUNT(*) FROM Pets WHERE status='Available'").fetchone()[0],
        'pending_r': db.execute("SELECT COUNT(*) FROM Adoption_Requests WHERE status='Pending'").fetchone()[0],
        'adopted':   db.execute("SELECT COUNT(*) FROM Pets WHERE status='Adopted'").fetchone()[0],
        'users':     db.execute("SELECT COUNT(*) FROM Users").fetchone()[0],
    }
    recent_requests = db.execute('''
        SELECT ar.request_id, ar.request_date, ar.status,
               u.name AS user_name, u.email,
               p.name AS pet_name, p.species
        FROM Adoption_Requests ar
        JOIN Users u ON ar.user_id = u.user_id
        JOIN Pets  p ON ar.pet_id  = p.pet_id
        ORDER BY ar.request_date DESC
        LIMIT 5
    ''').fetchall()
    return render_template('admin_dashboard.html', stats=stats, recent_requests=recent_requests)


@app.route('/admin/pets')
@admin_required
def admin_pets():
    db = get_db()
    all_pets = db.execute("SELECT * FROM Pets ORDER BY added_on DESC").fetchall()
    return render_template('admin_pets.html', pets=all_pets)


@app.route('/admin/add_pet', methods=['GET', 'POST'])
@admin_required
def add_pet():
    if request.method == 'POST':
        name        = request.form.get('name',        '').strip()
        species     = request.form.get('species',     '').strip()
        breed       = request.form.get('breed',       '').strip()
        age         = request.form.get('age',         '').strip()
        gender      = request.form.get('gender',      '').strip()
        description = request.form.get('description', '').strip()
        image_url   = request.form.get('image_url',   '').strip()

        errors = []
        if not name:    errors.append("Pet name is required.")
        if not species: errors.append("Species is required.")
        if age and not age.isdigit():
            errors.append("Age must be a positive number.")

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template('add_pet.html', form=request.form)

        db = get_db()
        db.execute(
            "INSERT INTO Pets (name, species, breed, age, gender, description, image_url) VALUES (?,?,?,?,?,?,?)",
            (name, species, breed, int(age) if age else None,
             gender, description, image_url or '/static/img/default_pet.png')
        )
        db.commit()
        flash(f"✅ {name} has been added to the system.", "success")
        return redirect(url_for('admin_pets'))

    return render_template('add_pet.html', form={})


@app.route('/admin/edit_pet/<int:pet_id>', methods=['GET', 'POST'])
@admin_required
def edit_pet(pet_id):
    db  = get_db()
    pet = db.execute("SELECT * FROM Pets WHERE pet_id=?", (pet_id,)).fetchone()
    if not pet:
        flash("Pet not found.", "danger")
        return redirect(url_for('admin_pets'))

    if request.method == 'POST':
        name        = request.form.get('name', '').strip()
        species     = request.form.get('species', '').strip()
        breed       = request.form.get('breed', '').strip()
        age         = request.form.get('age', '').strip()
        gender      = request.form.get('gender', '').strip()
        description = request.form.get('description', '').strip()
        status      = request.form.get('status', 'Available')
        image_url   = request.form.get('image_url', '').strip()

        db.execute('''
            UPDATE Pets SET name=?, species=?, breed=?, age=?, gender=?,
                            description=?, status=?, image_url=?
            WHERE pet_id=?
        ''', (name, species, breed,
              int(age) if age else None,
              gender, description, status,
              image_url or '/static/img/default_pet.png',
              pet_id))
        db.commit()
        flash(f"✅ {name}'s details updated.", "success")
        return redirect(url_for('admin_pets'))

    return render_template('edit_pet.html', pet=pet)


@app.route('/admin/delete_pet/<int:pet_id>', methods=['POST'])
@admin_required
def delete_pet(pet_id):
    db = get_db()
    pet = db.execute("SELECT name FROM Pets WHERE pet_id=?", (pet_id,)).fetchone()
    if pet:
        db.execute("DELETE FROM Pets WHERE pet_id=?", (pet_id,))
        db.commit()
        flash(f"🗑️ {pet['name']} has been removed.", "info")
    return redirect(url_for('admin_pets'))


@app.route('/admin/requests')
@admin_required
def admin_requests():
    db     = get_db()
    status = request.args.get('status', '')
    sql    = '''
        SELECT ar.request_id, ar.request_date, ar.status, ar.notes,
               u.name AS user_name, u.email, u.phone,
               p.name AS pet_name, p.species, p.pet_id
        FROM Adoption_Requests ar
        JOIN Users u ON ar.user_id = u.user_id
        JOIN Pets  p ON ar.pet_id  = p.pet_id
    '''
    params = []
    if status:
        sql += " WHERE ar.status = ?"
        params.append(status)
    sql += " ORDER BY ar.request_date DESC"
    requests_list = db.execute(sql, params).fetchall()
    return render_template('admin_requests.html', requests=requests_list, active_status=status)


@app.route('/admin/update_request/<int:request_id>', methods=['POST'])
@admin_required
def update_request(request_id):
    new_status = request.form.get('status')
    if new_status not in ('Approved', 'Rejected', 'Pending'):
        flash("Invalid status.", "danger")
        return redirect(url_for('admin_requests'))

    db  = get_db()
    req = db.execute(
        "SELECT pet_id FROM Adoption_Requests WHERE request_id=?", (request_id,)
    ).fetchone()
    if not req:
        flash("Request not found.", "danger")
        return redirect(url_for('admin_requests'))

    db.execute("UPDATE Adoption_Requests SET status=? WHERE request_id=?",
               (new_status, request_id))

    # Sync pet status
    if new_status == 'Approved':
        db.execute("UPDATE Pets SET status='Adopted' WHERE pet_id=?", (req['pet_id'],))
    elif new_status == 'Rejected':
        db.execute("UPDATE Pets SET status='Available' WHERE pet_id=?", (req['pet_id'],))
    elif new_status == 'Pending':
        db.execute("UPDATE Pets SET status='Pending' WHERE pet_id=?", (req['pet_id'],))

    db.commit()
    flash(f"Request #{request_id} marked as {new_status}.", "success")
    return redirect(url_for('admin_requests'))


# ── Data Export ───────────────────────────────────────────────────────────────

@app.route('/admin/export/pets')
@admin_required
def export_pets_csv():
    db   = get_db()
    rows = db.execute("SELECT pet_id, name, species, breed, age, gender, status, added_on FROM Pets").fetchall()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Species', 'Breed', 'Age', 'Gender', 'Status', 'Added On'])
    writer.writerows([list(r) for r in rows])
    return Response(output.getvalue(), mimetype='text/csv',
                    headers={"Content-Disposition": "attachment;filename=pets_export.csv"})


@app.route('/admin/export/requests')
@admin_required
def export_requests_csv():
    db   = get_db()
    rows = db.execute('''
        SELECT ar.request_id, u.name, u.email, u.phone,
               p.name, p.species, ar.request_date, ar.status, ar.notes
        FROM Adoption_Requests ar
        JOIN Users u ON ar.user_id = u.user_id
        JOIN Pets  p ON ar.pet_id  = p.pet_id
        ORDER BY ar.request_date DESC
    ''').fetchall()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Request ID', 'Adopter Name', 'Email', 'Phone',
                     'Pet Name', 'Species', 'Date', 'Status', 'Notes'])
    writer.writerows([list(r) for r in rows])
    return Response(output.getvalue(), mimetype='text/csv',
                    headers={"Content-Disposition": "attachment;filename=adoption_requests.csv"})


# ── Error handlers ────────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


if __name__ == "__main__":
    app.run(debug=True)

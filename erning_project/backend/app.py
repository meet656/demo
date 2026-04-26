"""
Local Service Finder - Backend API
====================================
Flask REST API for managing local service providers in Ahmedabad.
Supports CRUD operations, search, filtering, ratings, and admin authentication.
"""

from flask import Flask, request, jsonify, g, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import hashlib
import secrets
from functools import wraps
import bcrypt
import jwt
import datetime

# Resolve the frontend directory (sibling to backend)
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend')

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)  # Enable CORS for frontend-backend communication


# Serve frontend pages
@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.route('/admin.html')
def serve_admin():
    return send_from_directory(FRONTEND_DIR, 'admin.html')


@app.route('/login.html')
def serve_login():
    return send_from_directory(FRONTEND_DIR, 'login.html')


@app.route('/signup.html')
def serve_signup():
    return send_from_directory(FRONTEND_DIR, 'signup.html')


@app.route('/forgot.html')
def serve_forgot():
    return send_from_directory(FRONTEND_DIR, 'forgot.html')


@app.route('/reset.html')
def serve_reset():
    return send_from_directory(FRONTEND_DIR, 'reset.html')


@app.route('/profile.html')
def serve_profile():
    return send_from_directory(FRONTEND_DIR, 'profile.html')


# --- Configuration ---
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')

# JWT Config
app.config['SECRET_KEY'] = secrets.token_hex(32)
blacklisted_tokens = set()


# =====================
# DATABASE HELPERS
# =====================

def get_db():
    """Get database connection for current request context."""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # Return rows as dictionaries
    return g.db


@app.teardown_appcontext
def close_db(exception):
    """Close database connection when request ends."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Initialize database tables and seed sample data."""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row

    # Create users table
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            reset_token TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create service_contacts table
    db.execute('''
        CREATE TABLE IF NOT EXISTS service_contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            service_id INTEGER NOT NULL,
            contact_type TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
        )
    ''')

    # Create services table
    db.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            location TEXT NOT NULL,
            area TEXT DEFAULT 'Navrangpura',
            category TEXT NOT NULL,
            is_premium INTEGER DEFAULT 0,
            rating REAL DEFAULT 0,
            rating_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create ratings table for individual ratings
    db.execute('''
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_id INTEGER NOT NULL,
            rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
        )
    ''')

    # Check if sample data exists
    count = db.execute('SELECT COUNT(*) FROM services').fetchone()[0]

    if count == 0:
        # Seed sample data for Ahmedabad service providers
        sample_services = [
            # Electricians
            ('Rajesh Electricals', '9876543210', 'Near Navrangpura Cross Roads', 'Navrangpura', 'Electrician', 1, 4.5, 12),
            ('Patel Electric Works', '9876543211', 'Opposite Satellite Tower', 'Satellite', 'Electrician', 0, 4.0, 8),
            ('Sharma Electrical Services', '9876543212', 'CG Road, Near Municipal Market', 'CG Road', 'Electrician', 0, 3.5, 5),
            ('Om Electricals', '9876543213', 'Near Vastrapur Lake', 'Vastrapur', 'Electrician', 0, 4.2, 15),
            ('Shree Krishna Electric', '9876543214', 'SG Highway, Near Iscon Mall', 'SG Highway', 'Electrician', 1, 4.8, 22),

            # Plumbers
            ('Ahmedabad Plumbing Solutions', '9876543215', 'Near Maninagar Railway Station', 'Maninagar', 'Plumber', 1, 4.7, 18),
            ('Quick Fix Plumbers', '9876543216', 'Paldi Cross Roads', 'Paldi', 'Plumber', 0, 3.8, 7),
            ('Reliable Plumbing Works', '9876543217', 'Bopal Circle, Near D-Mart', 'Bopal', 'Plumber', 0, 4.1, 10),
            ('Jain Plumbing Services', '9876543218', 'Thaltej Cross Roads', 'Thaltej', 'Plumber', 0, 4.3, 9),
            ('Narmada Plumbing Co.', '9876543219', 'Prahlad Nagar, Near Honest Restaurant', 'Prahlad Nagar', 'Plumber', 1, 4.6, 20),

            # Tutors
            ('Genius Academy', '9876543220', 'Near Gujarat University', 'Navrangpura', 'Tutor', 1, 4.9, 30),
            ('Bright Future Classes', '9876543221', 'Satellite Road, Above SBI Bank', 'Satellite', 'Tutor', 0, 4.0, 11),
            ('Excel Tuition Centre', '9876543222', 'Chandkheda, Near PDPU', 'Chandkheda', 'Tutor', 0, 3.9, 6),
            ('Vidya Mandir Classes', '9876543223', 'Gota, Near Shilaj Circle', 'Gota', 'Tutor', 0, 4.4, 14),
            ('IQ Hub Coaching', '9876543224', 'Bodakdev, Near Judges Bungalow', 'Bodakdev', 'Tutor', 1, 4.7, 25),
            ('Maths Master Tuition', '9876543225', 'Ellis Bridge, Near Parimal Garden', 'Ellis Bridge', 'Tutor', 0, 4.2, 8),

            # Extra providers
            ('Power Plus Electricals', '9876543226', 'Shahibaug, Near Circuit House', 'Shahibaug', 'Electrician', 0, 3.7, 4),
            ('Aqua Plumbing Works', '9876543227', 'Nikol, Near BRTS Stand', 'Nikol', 'Plumber', 0, 3.5, 3),
            ('Smart Study Hub', '9876543228', 'Naranpura, Near Vishwakunj', 'Naranpura', 'Tutor', 0, 4.1, 7),
            ('City Light Electricians', '9876543229', 'Ambawadi, Near Panchwati', 'Ambawadi', 'Electrician', 0, 4.0, 6),
        ]

        db.executemany('''
            INSERT INTO services (name, phone, location, area, category, is_premium, rating, rating_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_services)

        # Seed ratings for existing services
        import random
        for i in range(1, 21):
            service = sample_services[i - 1]
            avg_rating = service[6]
            count = service[7]
            for _ in range(count):
                # Generate ratings around the average
                r = max(1, min(5, round(avg_rating + random.uniform(-1, 1))))
                db.execute('INSERT INTO ratings (service_id, rating) VALUES (?, ?)', (i, r))

    db.commit()
    db.close()


# =====================
# AUTH HELPERS
# =====================

def require_admin(f):
    """Decorator to protect admin-only endpoints."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token or token in blacklisted_tokens:
            return jsonify({'error': 'Unauthorized. Please login as admin.'}), 401
            
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            if data.get('role') != 'admin':
                return jsonify({'error': 'Access Denied. Admin privileges required.'}), 403
            g.current_user = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired. Please log in again.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token. Please log in again.'}), 401
            
        return f(*args, **kwargs)
    return decorated


def require_user(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token or token in blacklisted_tokens:
            return jsonify({'error': 'Unauthorized. Please log in.'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            g.current_user = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired. Please log in again.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token. Please log in again.'}), 401
            
        return f(*args, **kwargs)
    return decorated


def optional_user(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        g.current_user = None
        if token and token not in blacklisted_tokens:
            try:
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
                g.current_user = data['user_id']
            except:
                pass
        return f(*args, **kwargs)
    return decorated


# =====================
# USER AUTH ENDPOINTS
# =====================

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not name or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400

    if email == "admin@gmail.com":
        return jsonify({'error': 'Cannot register with this email.'}), 400

    db = get_db()
    
    # Check if email exists
    existing = db.execute('SELECT id FROM users WHERE email = ?', [email]).fetchone()
    if existing:
        return jsonify({'error': 'Email already registered'}), 400

    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    db.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', [name, email, hashed_pw])
    db.commit()
    
    return jsonify({'message': 'User registered successfully!'}), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    remember = data.get('remember', False)

    if email == "admin@gmail.com" and password == "admin123":
        user_id = 0
        name = "Admin User"
        role = "admin"
    else:
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email = ?', [email]).fetchone()

        if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return jsonify({'error': 'Invalid email or password'}), 401
            
        user_id = user['id']
        name = user['name']
        role = "user"

    expiry_days = 7 if remember else 1
    token = jwt.encode({
        'user_id': user_id,
        'role': role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=expiry_days)
    }, app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({
        'token': token,
        'user': {'id': user_id, 'name': name, 'email': email, 'role': role},
        'message': 'Login successful!'
    })


@app.route('/api/auth/logout', methods=['POST'])
@require_user
def logout():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    blacklisted_tokens.add(token)
    return jsonify({'message': 'Logged out successfully!'})


@app.route('/api/auth/me', methods=['GET'])
@require_user
def get_me():
    db = get_db()
    user = db.execute('SELECT id, name, email FROM users WHERE id = ?', [g.current_user]).fetchone()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(dict(user))


@app.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email', '').strip()
    
    db = get_db()
    user = db.execute('SELECT id FROM users WHERE email = ?', [email]).fetchone()
    
    if not user:
        return jsonify({'error': 'Email not found'}), 404
        
    reset_token = secrets.token_hex(16)
    db.execute('UPDATE users SET reset_token = ? WHERE email = ?', [reset_token, email])
    db.commit()
    
    # In a real app, send this via email. For demo, return it.
    return jsonify({
        'message': 'Reset token generated (simulated email)',
        'reset_token': reset_token
    })


@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('token', '')
    new_password = data.get('password', '')
    
    if not token or not new_password:
        return jsonify({'error': 'Token and new password are required'}), 400
        
    db = get_db()
    user = db.execute('SELECT id FROM users WHERE reset_token = ?', [token]).fetchone()
    
    if not user:
        return jsonify({'error': 'Invalid or expired reset token'}), 400
        
    hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    db.execute('UPDATE users SET password = ?, reset_token = NULL WHERE id = ?', [hashed_pw, user['id']])
    db.commit()
    
    return jsonify({'message': 'Password reset successfully!'})


# =====================
# USER PROFILE ENDPOINTS
# =====================

@app.route('/api/profile/<int:user_id>', methods=['GET'])
@require_user
def get_user_profile(user_id):
    if g.current_user != user_id and g.current_user != 0:
        return jsonify({'error': 'Unauthorized access to profile'}), 403
        
    db = get_db()
    
    if user_id == 0:
        user = {'id': 0, 'name': 'Admin User', 'email': 'admin@gmail.com', 'role': 'admin'}
    else:
        user_row = db.execute('SELECT id, name, email FROM users WHERE id = ?', [user_id]).fetchone()
        if not user_row:
            return jsonify({'error': 'User not found'}), 404
        user = dict(user_row)
        user['role'] = 'user'
        
    return jsonify(user)


@app.route('/api/user-activity/<int:user_id>', methods=['GET'])
@require_user
def get_user_activity(user_id):
    if g.current_user != user_id and g.current_user != 0:
        return jsonify({'error': 'Unauthorized access to activity'}), 403
        
    db = get_db()
    
    # Get all contacted services with their details
    contacts = db.execute('''
        SELECT c.id, c.contact_type, c.timestamp, s.id as service_id, s.name as service_name, s.category, s.phone
        FROM service_contacts c
        JOIN services s ON c.service_id = s.id
        WHERE c.user_id = ?
        ORDER BY c.timestamp DESC
    ''', [user_id]).fetchall()
    
    activity_list = [dict(row) for row in contacts]
    
    return jsonify({
        'activities': activity_list,
        'total_contacts': len(activity_list)
    })


@app.route('/api/track-contact', methods=['POST'])
@require_user
def track_contact():
    data = request.get_json()
    service_id = data.get('service_id')
    contact_type = data.get('contact_type')
    
    if not service_id or not contact_type:
        return jsonify({'error': 'Missing service_id or contact_type'}), 400
        
    db = get_db()
    db.execute('''
        INSERT INTO service_contacts (user_id, service_id, contact_type)
        VALUES (?, ?, ?)
    ''', [g.current_user, service_id, contact_type])
    db.commit()
    
    return jsonify({'message': 'Contact tracked successfully'})


# =====================
# SERVICE ENDPOINTS
# =====================

@app.route('/api/services', methods=['GET'])
def get_services():
    """
    Get all service providers.
    Supports query params: search, area, category
    Premium providers are always sorted to the top.
    """
    db = get_db()
    query = 'SELECT * FROM services WHERE 1=1'
    params = []

    # Filter by search term (name or location)
    search = request.args.get('search', '').strip()
    if search:
        query += ' AND (name LIKE ? OR location LIKE ? OR area LIKE ?)'
        search_term = f'%{search}%'
        params.extend([search_term, search_term, search_term])

    # Filter by area
    area = request.args.get('area', '').strip()
    if area:
        query += ' AND area = ?'
        params.append(area)

    # Filter by category
    category = request.args.get('category', '').strip()
    if category:
        query += ' AND category = ?'
        params.append(category)

    # Premium first, then by rating descending
    query += ' ORDER BY is_premium DESC, rating DESC'

    services = db.execute(query, params).fetchall()
    result = [dict(row) for row in services]

    return jsonify(result)


@app.route('/api/services/<category>', methods=['GET'])
def get_services_by_category(category):
    """Get service providers filtered by category."""
    db = get_db()
    query = 'SELECT * FROM services WHERE category = ? ORDER BY is_premium DESC, rating DESC'
    services = db.execute(query, [category]).fetchall()
    result = [dict(row) for row in services]
    return jsonify(result)


@app.route('/api/services/detail/<int:service_id>', methods=['GET'])
def get_service_detail(service_id):
    """Get a single service provider by ID."""
    db = get_db()
    service = db.execute('SELECT * FROM services WHERE id = ?', [service_id]).fetchone()
    if service is None:
        return jsonify({'error': 'Service not found'}), 404
    return jsonify(dict(service))


@app.route('/api/areas', methods=['GET'])
def get_areas():
    """Get list of all unique areas in the database."""
    db = get_db()
    areas = db.execute('SELECT DISTINCT area FROM services ORDER BY area').fetchall()
    result = [row['area'] for row in areas]
    return jsonify(result)


# =====================
# ADMIN CRUD ENDPOINTS
# =====================

@app.route('/api/add-service', methods=['POST'])
@require_admin
def add_service():
    """Add a new service provider (admin only)."""
    data = request.get_json()

    # Validate required fields
    required = ['name', 'phone', 'location', 'category']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'Missing required field: {field}'}), 400

    db = get_db()
    db.execute('''
        INSERT INTO services (name, phone, location, area, category, is_premium)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', [
        data['name'],
        data['phone'],
        data['location'],
        data.get('area', 'Navrangpura'),
        data['category'],
        int(data.get('is_premium', 0))
    ])
    db.commit()

    return jsonify({'message': 'Service provider added successfully!'}), 201


@app.route('/api/update-service/<int:service_id>', methods=['PUT'])
@require_admin
def update_service(service_id):
    """Update an existing service provider (admin only)."""
    data = request.get_json()
    db = get_db()

    # Check if service exists
    service = db.execute('SELECT * FROM services WHERE id = ?', [service_id]).fetchone()
    if service is None:
        return jsonify({'error': 'Service not found'}), 404

    db.execute('''
        UPDATE services SET
            name = ?,
            phone = ?,
            location = ?,
            area = ?,
            category = ?,
            is_premium = ?
        WHERE id = ?
    ''', [
        data.get('name', service['name']),
        data.get('phone', service['phone']),
        data.get('location', service['location']),
        data.get('area', service['area']),
        data.get('category', service['category']),
        int(data.get('is_premium', service['is_premium'])),
        service_id
    ])
    db.commit()

    return jsonify({'message': 'Service provider updated successfully!'})


@app.route('/api/delete-service/<int:service_id>', methods=['DELETE'])
@require_admin
def delete_service(service_id):
    """Delete a service provider (admin only)."""
    db = get_db()

    service = db.execute('SELECT * FROM services WHERE id = ?', [service_id]).fetchone()
    if service is None:
        return jsonify({'error': 'Service not found'}), 404

    db.execute('DELETE FROM services WHERE id = ?', [service_id])
    db.execute('DELETE FROM ratings WHERE service_id = ?', [service_id])
    db.commit()

    return jsonify({'message': 'Service provider deleted successfully!'})


# =====================
# RATING ENDPOINTS
# =====================

@app.route('/api/rate-service/<int:service_id>', methods=['POST'])
@require_user
def rate_service(service_id):
    """
    Submit a rating for a service provider.
    Accepts: { "rating": 1-5 }
    Updates the average rating on the service.
    """
    data = request.get_json()
    rating = data.get('rating')

    if not rating or rating < 1 or rating > 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400

    db = get_db()

    # Check if service exists
    service = db.execute('SELECT * FROM services WHERE id = ?', [service_id]).fetchone()
    if service is None:
        return jsonify({'error': 'Service not found'}), 404

    # Insert individual rating
    db.execute('INSERT INTO ratings (service_id, rating) VALUES (?, ?)', [service_id, rating])

    # Recalculate average rating
    result = db.execute('''
        SELECT AVG(rating) as avg_rating, COUNT(*) as total
        FROM ratings WHERE service_id = ?
    ''', [service_id]).fetchone()

    # Update service with new average
    db.execute('''
        UPDATE services SET rating = ROUND(?, 1), rating_count = ? WHERE id = ?
    ''', [result['avg_rating'], result['total'], service_id])

    db.commit()

    return jsonify({
        'message': 'Rating submitted successfully!',
        'new_rating': round(result['avg_rating'], 1),
        'total_ratings': result['total']
    })


# =====================
# APP STARTUP
# =====================

if __name__ == '__main__':
    print("[*] Initializing Local Service Finder API...")
    init_db()
    print("[OK] Database initialized with sample data")
    print("[>>] Server starting at http://localhost:5000")
    print("[KEY] Admin credentials: admin / admin123")
    app.run(debug=True, port=5000)

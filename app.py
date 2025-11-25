from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__, static_folder='Static', static_url_path='/static')

# In production, set the secret key securely via environment variables
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_secret_key_change_in_production")

# MongoDB Connection - Lazy connection pattern for serverless environments
# Use environment variable for connection string, fallback to localhost for development
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "halltek_auth_db")

# Global variables to store MongoDB connection (initialized lazily)
_client = None
_db = None
_users = None

def get_mongodb_client():
    """Get or create MongoDB client connection"""
    global _client
    if _client is None:
        try:
            # For serverless, use shorter connection timeout
            _client = MongoClient(
                MONGODB_URI,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=5000
            )
            # Test connection
            _client.admin.command('ping')
        except Exception as e:
            print(f"MongoDB connection error: {e}")
            raise
    return _client

def get_users_collection():
    """Get users collection, creating indexes if needed"""
    global _db, _users
    if _users is None:
        try:
            client = get_mongodb_client()
            _db = client[DATABASE_NAME]
            _users = _db["users"]
            # Create indexes on first access (idempotent - safe to call multiple times)
            _users.create_index("username", unique=True)
            _users.create_index("email", unique=True)
        except Exception as e:
            print(f"MongoDB collection access error: {e}")
            raise
    return _users

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about', endpoint='about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Username and password are required.', 'danger')
        else:
            try:
                users = get_users_collection()
                # Try to find user by username or email
                user = users.find_one({'$or': [{'username': username}, {'email': username}]})
                
                if user and check_password_hash(user.get('password', ''), password):
                    session['username'] = user.get('username')
                    session['email'] = user.get('email')
                    flash('Login successful!', 'success')
                    return redirect(url_for('home'))
                else:
                    flash('Invalid username/email or password', 'danger')
            except Exception as e:
                flash('Database connection error. Please try again later.', 'danger')
                print(f"Login error: {e}")
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
        elif len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
        else:
            try:
                users = get_users_collection()
                if users.find_one({'username': username}):
                    flash('Username already exists. Please choose another.', 'danger')
                elif users.find_one({'email': email}):
                    flash('Email already registered. Please use a different email or login.', 'danger')
                else:
                    hashed_password = generate_password_hash(password)
                    user_data = {
                        'username': username,
                        'email': email,
                        'password': hashed_password
                    }
                    users.insert_one(user_data)
                    flash('Registration successful! Please log in.', 'success')
                    return redirect(url_for('login'))
            except Exception as e:
                flash('Database connection error. Please try again later.', 'danger')
                print(f"Registration error: {e}")
    
    return render_template('register.html')

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        username_or_email = request.form.get('username', '').strip()
        new_password = request.form.get('new_password', '')
        
        if not username_or_email or not new_password:
            flash('Username/Email and new password are required.', 'danger')
        elif len(new_password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
        else:
            try:
                users = get_users_collection()
                # Find user by username or email
                user = users.find_one({'$or': [{'username': username_or_email}, {'email': username_or_email}]})
                
                if user:
                    hashed_password = generate_password_hash(new_password)
                    users.update_one(
                        {'$or': [{'username': username_or_email}, {'email': username_or_email}]},
                        {'$set': {'password': hashed_password}}
                    )
                    flash('Password reset successful! Please log in with your new password.', 'success')
                    return redirect(url_for('login'))
                else:
                    flash('Username or email not found.', 'danger')
            except Exception as e:
                flash('Database connection error. Please try again later.', 'danger')
                print(f"Password reset error: {e}")
    
    return render_template('forgot.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    else:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)

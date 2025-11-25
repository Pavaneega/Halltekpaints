from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__, static_folder='Static', static_url_path='/static')

# In production, set the secret key securely via environment variables
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_secret_key_change_in_production")

# MongoDB Connection
try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["halltek_auth_db"]
    users = db["users"]
    # Create index on username and email for faster lookups
    users.create_index("username", unique=True)
    users.create_index("email", unique=True)
except Exception as e:
    print(f"MongoDB connection error: {e}")
    print("Make sure MongoDB is running on localhost:27017")

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
            # Try to find user by username or email
            user = users.find_one({'$or': [{'username': username}, {'email': username}]})
            
            if user and check_password_hash(user.get('password', ''), password):
                session['username'] = user.get('username')
                session['email'] = user.get('email')
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid username/email or password', 'danger')
    
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
        elif users.find_one({'username': username}):
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

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os
from pathlib import Path

# Get the directory where this file is located
BASE_DIR = Path(__file__).parent.absolute()

from typing import Any

# Use absolute paths for templates and static files (required for Vercel serverless)
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / 'templates'),
    static_folder=str(BASE_DIR / 'Static'),
    static_url_path='/Static'
)

# In production, set the secret key securely via environment variables
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_secret_key_change_in_production")

# Admin credentials (can be overridden via env variables)
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin@halltek")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Halltek#Admin123")

# MongoDB Connection - Lazy connection pattern for serverless environments
# Use environment variable for connection string, fallback to localhost for development
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "halltek_auth_db")

# Global variables to store MongoDB connection (initialized lazily)
_client = None
_db = None
_users = None
_products_collection = None


@app.after_request
def add_cors_headers(response):
    """
    Add CORS headers so that the frontend running on 127.0.0.1:5500
    can call this backend on 127.0.0.1:5000.
    """
    response.headers['Access-Control-Allow-Origin'] = 'http://127.0.0.1:5500'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

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


def get_products_collection():
    """Get products collection (lazily initialized)."""
    global _db, _products_collection
    if _products_collection is None:
        try:
            client = get_mongodb_client()
            _db = client[DATABASE_NAME]
            _products_collection = _db["products"]
            _products_collection.create_index("name")
        except Exception as e:
            print(f"MongoDB products collection error: {e}")
            raise
    return _products_collection


def serialize_product(doc):
    """Convert Mongo product document to JSON-serializable dict."""
    if not doc:
        return {}
    return {
        "id": str(doc.get("_id", "")),
        "name": doc.get("name", "Untitled Product"),
        "description": doc.get("description", "No description provided."),
        "price": doc.get("price", 0),
        "image": doc.get("image") or "",
        "font_family": doc.get("font_family") or ""
    }

@app.route('/')
@app.route('/index.html')
def home():
    return render_template('index.html')

@app.route('/about', endpoint='about')
@app.route('/about.html')
def about():
    return render_template('about.html')


@app.route('/products', endpoint='products')
@app.route('/products.html')
def products():
    return render_template('products.html')


@app.route('/rewards', endpoint='rewards')
@app.route('/rewards.html')
def rewards():
    return render_template('rewards.html')


@app.route('/login', methods=['GET', 'POST'])
@app.route('/login.html', methods=['GET', 'POST'])
def login():
    """
    Login route that supports:
    - Admin env credentials (ADMIN_USERNAME / ADMIN_PASSWORD)
    - Normal users stored in MongoDB (username or email, field 'password')
    - Optional ?next=/some/path redirect after login
    """
    next_url = request.args.get('next') or request.form.get('next') or url_for('dashboard')

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Username and password required.', 'warning')
            return redirect(url_for('login', next=next_url))

        # 1) Admin fast-path using env credentials (does NOT require DB user)
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['username'] = ADMIN_USERNAME
            session['email'] = ''
            session['is_admin'] = True
            flash('Logged in as admin.', 'success')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect(url_for('admin_products_page'))

        # 2) Normal user from MongoDB (username OR email)
        users = get_users_collection()
        user = users.find_one({'$or': [{'username': username}, {'email': username}]})

        stored_hash = ''
        if user:
            # Support both legacy 'password' field and potential 'password_hash'
            stored_hash = user.get('password') or user.get('password_hash', '')

        if user and stored_hash and check_password_hash(stored_hash, password):
            session['username'] = user.get('username')
            session['email'] = user.get('email')
            session['is_admin'] = user.get('username') == ADMIN_USERNAME or user.get('email') == ADMIN_USERNAME
            flash('Logged in successfully.', 'success')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect(url_for('dashboard'))

        flash('Invalid username/email or password.', 'danger')
        return redirect(url_for('login', next=next_url))

    # GET
    return render_template('login.html', next=next_url)

@app.route('/register', methods=['GET', 'POST'])
@app.route('/register.html', methods=['GET', 'POST'])
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


 # Admin Product Management Routes
@app.route('/admin/products')
@app.route('/admin/product.html')
def admin_products_page():
    """Render admin product management page"""
    if not session.get('is_admin'):
        flash('Admin access required.', 'danger')
        return redirect(url_for('login'))
    return render_template('admin/product.html')

# API Routes for CRUD operations
from bson import ObjectId
from werkzeug.utils import secure_filename

# Configure upload folder
UPLOAD_FOLDER = BASE_DIR / 'Static' / 'uploads' / 'products'
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products"""
    try:
        products_collection = get_products_collection()
        products = list(products_collection.find())
        # Convert ObjectId to string
        for product in products:
            product['_id'] = str(product['_id'])
        return jsonify(products), 200
    except Exception as e:
        print(f"Error fetching products: {e}")
        return jsonify({'error': 'Error fetching products'}), 500

@app.route('/api/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get single product by ID"""
    try:
        products_collection = get_products_collection()
        product = products_collection.find_one({'_id': ObjectId(product_id)})
        if product:
            product['_id'] = str(product['_id'])
            return jsonify(product), 200
        return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        print(f"Error fetching product: {e}")
        return jsonify({'error': 'Error fetching product'}), 500

@app.route('/api/products', methods=['POST'])
def create_product():
    """Create new product"""
    try:
        products_collection = get_products_collection()
        
        # Get form data
        name = request.form.get('name')
        price = request.form.get('price')
        description = request.form.get('description', '')
        font_family = request.form.get('font_family', 'Inter')
        
        if not name or not price:
            return jsonify({'error': 'Name and price are required'}), 400
        
        # Handle image upload
        image_url = request.form.get('image_url', '')
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to avoid conflicts
                import time
                filename = f"{int(time.time())}_{filename}"
                filepath = UPLOAD_FOLDER / filename
                file.save(str(filepath))
                image_url = f"/Static/uploads/products/{filename}"
        
        # Handle custom font upload
        font_url = ''
        if 'custom_font' in request.files:
            font_file = request.files['custom_font']
            if font_file and font_file.filename:
                font_filename = secure_filename(font_file.filename)
                import time
                font_filename = f"{int(time.time())}_{font_filename}"
                font_path = UPLOAD_FOLDER / 'fonts'
                font_path.mkdir(exist_ok=True)
                font_filepath = font_path / font_filename
                font_file.save(str(font_filepath))
                font_url = f"/Static/uploads/products/fonts/{font_filename}"
        
        # Create product document
        product = {
            'name': name,
            'price': float(price),
            'description': description,
            'image': image_url,
            'font_family': font_family,
            'custom_font': font_url
        }
        
        result = products_collection.insert_one(product)
        product['_id'] = str(result.inserted_id)
        
        return jsonify(product), 201
    except Exception as e:
        print(f"Error creating product: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<product_id>', methods=['PUT'])
def update_product(product_id):
    """Update existing product"""
    try:
        products_collection = get_products_collection()
        
        # Get form data
        name = request.form.get('name')
        price = request.form.get('price')
        description = request.form.get('description', '')
        font_family = request.form.get('font_family', 'Inter')
        
        if not name or not price:
            return jsonify({'error': 'Name and price are required'}), 400
        
        # Get existing product
        existing_product = products_collection.find_one({'_id': ObjectId(product_id)})
        if not existing_product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Handle image upload
        image_url = request.form.get('image_url', existing_product.get('image', ''))
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                import time
                filename = f"{int(time.time())}_{filename}"
                filepath = UPLOAD_FOLDER / filename
                file.save(str(filepath))
                image_url = f"/Static/uploads/products/{filename}"
        
        # Handle custom font upload
        font_url = existing_product.get('custom_font', '')
        if 'custom_font' in request.files:
            font_file = request.files['custom_font']
            if font_file and font_file.filename:
                font_filename = secure_filename(font_file.filename)
                import time
                font_filename = f"{int(time.time())}_{font_filename}"
                font_path = UPLOAD_FOLDER / 'fonts'
                font_path.mkdir(exist_ok=True)
                font_filepath = font_path / font_filename
                font_file.save(str(font_filepath))
                font_url = f"/Static/uploads/products/fonts/{font_filename}"
        
        # Update product document
        update_data = {
            'name': name,
            'price': float(price),
            'description': description,
            'image': image_url,
            'font_family': font_family,
            'custom_font': font_url
        }
        
        products_collection.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': update_data}
        )
        
        update_data['_id'] = product_id
        return jsonify(update_data), 200
    except Exception as e:
        print(f"Error updating product: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete product"""
    try:
        products_collection = get_products_collection()
        result = products_collection.delete_one({'_id': ObjectId(product_id)})
        
        if result.deleted_count > 0:
            return jsonify({'message': 'Product deleted successfully'}), 200
        return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        print(f"Error deleting product: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/session', methods=['GET'])
def api_session():
    """Return current login state"""
    return jsonify({
        'authenticated': 'username' in session,
        'username': session.get('username'),
        'email': session.get('email'),
        'is_admin': session.get('is_admin', False)
    })

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)


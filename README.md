# Halltek Paints

A Flask-based web application for Halltek Paints with user authentication and dashboard functionality.

## Features

- **User Authentication**
  - User registration with username, email, and password
  - Login with username or email
  - Password reset functionality
  - Secure password hashing using Werkzeug
  - Session management

- **Dashboard**
  - Protected dashboard accessible only to authenticated users
  - User session tracking

- **Database**
  - MongoDB integration for user data storage
  - Unique indexes on username and email for data integrity

## Requirements

- Python 3.7+
- MongoDB (running on localhost:27017)
- Flask 3.0.0
- PyMongo 4.6.0
- Werkzeug 3.0.1

## Installation

1. **Clone the repository** (or navigate to the project directory)

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv env
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```bash
     env\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source env/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Start MongoDB**:
   Make sure MongoDB is installed and running on `localhost:27017`

## Configuration

### Environment Variables

For production, set the following environment variable:

- `FLASK_SECRET_KEY`: A secure secret key for Flask sessions (defaults to a dev key if not set)

Example:
```bash
export FLASK_SECRET_KEY="your-secret-key-here"
```

On Windows PowerShell:
```powershell
$env:FLASK_SECRET_KEY="your-secret-key-here"
```

### MongoDB Configuration

The application connects to MongoDB at `mongodb://localhost:27017/` by default. The database name is `halltek_auth_db`.

To change the MongoDB connection, modify the connection string in `app.py`:
```python
client = MongoClient("mongodb://localhost:27017/")
```

## Usage

1. **Start the Flask application**:
   ```bash
   python app.py
   ```

2. **Access the application**:
   Open your browser and navigate to `http://localhost:5000`

3. **Available Routes**:
   - `/` - Home page
   - `/login` - User login page
   - `/register` - User registration page
   - `/forgot` - Password reset page
   - `/dashboard` - User dashboard (requires authentication)
   - `/logout` - Logout and clear session

## Project Structure

```
halltekpaints/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── env/                  # Virtual environment (not tracked in git)
├── templates/            # HTML templates
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── forgot.html
│   └── dashboard.html
└── Static/               # Static files
    ├── css/
    │   └── style.css
    ├── image/
    │   └── [various images]
    └── js/
```

## Security Notes

- **Development Mode**: The application runs in debug mode by default. Disable debug mode in production.
- **Secret Key**: Always set a secure `FLASK_SECRET_KEY` in production environments.
- **Password Security**: Passwords are hashed using Werkzeug's password hashing utilities.
- **Session Security**: User sessions are managed securely using Flask sessions.

## Development

The application runs with `debug=True` by default. To run in production:

1. Set `debug=False` in `app.py`
2. Set a secure `FLASK_SECRET_KEY` environment variable
3. Use a production WSGI server (e.g., Gunicorn, uWSGI)

## Troubleshooting

### MongoDB Connection Error

If you see "MongoDB connection error":
- Ensure MongoDB is installed and running
- Check that MongoDB is accessible on `localhost:27017`
- Verify MongoDB service is started

### Port Already in Use

If port 5000 is already in use, you can change it in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

## License

This project is proprietary software for Halltek Paints.


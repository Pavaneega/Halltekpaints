import sys
import os

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app import app
    # This is the entry point for Vercel serverless functions
    # Vercel expects a WSGI application
    handler = app
except Exception as e:
    # Log the error for debugging
    print(f"Error importing app: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    raise


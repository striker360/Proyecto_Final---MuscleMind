
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import uvicorn
import os
from dotenv import load_dotenv

# Explicitly load environment variables
load_dotenv()

# The current directory is already in PYTHONPATH if you run from the project root.

# Print environment information before starting
print("\n=== Starting MuscleMind - Mente muscular in development mode ===")

# Explicitly check environment variables
database_url = os.environ.get("DATABASE_URL")
if database_url:
    print(f"* DATABASE_URL variable detected: {database_url[:20]}...")
    
    # Check if asyncpg is installed
    try:
        import asyncpg
        _ = asyncpg.__version__  # Access asyncpg to avoid "not accessed" warning
        print("* AsyncPG is installed. PostgreSQL will be used.")
        
        # Check if the URL has SSL configuration
        if "sslmode=require" not in database_url:
            print("* WARNING: The URL does not specify sslmode=require, which is usually required for Neon DB.")
            
        # Check local configuration
        try:
            import importlib.util
            local_settings_path = os.path.join(os.path.dirname(__file__), "app", "local_settings.py")
            spec = importlib.util.spec_from_file_location("local_settings", local_settings_path)
            local_settings = importlib.util.module_from_spec(spec)
            sys.modules["local_settings"] = local_settings
            spec.loader.exec_module(local_settings)
            if getattr(local_settings, "FORCE_SQLITE", False):
                print("* NOTE: FORCE_SQLITE is enabled in local_settings.py - SQLite will be used instead of PostgreSQL")
        except Exception:
            pass
    except ImportError:
        print("* WARNING: DATABASE_URL is defined but asyncpg is not installed.")
        print("* Local SQLite will be used. To use PostgreSQL, install asyncpg:")
        print("* pip install asyncpg")
else:
    print("* DATABASE_URL not detected. Using local SQLite for development.")

# Check for conflicting environment variables
for key in os.environ:
    if "DB" in key.upper() or "SQL" in key.upper() or "POSTGRES" in key.upper():
        if key != "DATABASE_URL":
            print(f"* Possible conflicting environment variable detected: {key}")

print("==========================================\n")

if __name__ == "__main__":
    # Configure Uvicorn options for development
    uvicorn.run(
        "app.main:app",
        host="localhost",
        port=8000,
        reload=True,  # Automatic reload when files change
        log_level="info"
    )
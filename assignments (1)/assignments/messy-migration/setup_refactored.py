#!/usr/bin/env python3
"""
Setup script for the refactored user management application.
This script helps migrate from the old application to the new secure version.
"""

import os
import sys
import sqlite3
from werkzeug.security import generate_password_hash

def create_new_database():
    """Create the new database with proper schema"""
    print("Creating new database with secure schema...")
    
    # Import the refactored app to create tables
    try:
        from app_refactored import app, db, User
        
        with app.app_context():
            db.create_all()
            print("✓ Database created successfully")
            return True
    except ImportError as e:
        print(f"Error: Could not import refactored app: {e}")
        print("Make sure app_refactored.py exists and all dependencies are installed")
        return False

def migrate_existing_data():
    """Migrate data from old database to new secure database"""
    print("Migrating existing data...")
    
    try:
        # Connect to old database
        old_conn = sqlite3.connect('users.db')
        old_cursor = old_conn.cursor()
        
        # Check if old database exists and has data
        old_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not old_cursor.fetchone():
            print("No existing users table found. Starting fresh.")
            return True
        
        # Get existing users
        old_cursor.execute("SELECT id, name, email, password FROM users")
        old_users = old_cursor.fetchall()
        
        if not old_users:
            print("No existing users found. Starting fresh.")
            return True
        
        print(f"Found {len(old_users)} existing users to migrate...")
        
        # Import the new app
        from app_refactored import app, db, User
        
        with app.app_context():
            migrated_count = 0
            for old_user in old_users:
                try:
                    # Hash the old password (if it was plain text)
                    password_hash = generate_password_hash(old_user[3])
                    
                    # Create new user with hashed password
                    new_user = User(
                        id=old_user[0],
                        name=old_user[1],
                        email=old_user[2],
                        password_hash=password_hash
                    )
                    
                    db.session.add(new_user)
                    migrated_count += 1
                    
                except Exception as e:
                    print(f"Warning: Could not migrate user {old_user[1]}: {e}")
                    continue
            
            db.session.commit()
            print(f"✓ Successfully migrated {migrated_count} users")
        
        old_conn.close()
        return True
        
    except Exception as e:
        print(f"Error during migration: {e}")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_refactored.txt"])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False
    except FileNotFoundError:
        print("Error: pip not found. Please install dependencies manually:")
        print("pip install -r requirements_refactored.txt")
        return False

def main():
    """Main setup function"""
    print("=" * 50)
    print("Setting up Refactored User Management Application")
    print("=" * 50)
    print()
    
    # Check if refactored app exists
    if not os.path.exists("app_refactored.py"):
        print("Error: app_refactored.py not found!")
        print("Please ensure the refactored application file exists.")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("Failed to install dependencies. Please install manually.")
        sys.exit(1)
    
    # Create new database
    if not create_new_database():
        print("Failed to create database.")
        sys.exit(1)
    
    # Migrate existing data
    migrate_existing_data()
    
    print()
    print("=" * 50)
    print("Setup completed successfully!")
    print("=" * 50)
    print()
    print("To run the refactored application:")
    print("python app_refactored.py")
    print()
    print("To test the application:")
    print("python test_refactored.py")
    print()
    print("The application will be available at: http://localhost:5000")
    print()
    print("Key improvements:")
    print("- SQL injection protection")
    print("- Password hashing")
    print("- Input validation")
    print("- Proper error handling")
    print("- Secure responses (no password exposure)")
    print("- Environment-based configuration")

if __name__ == "__main__":
    main() 
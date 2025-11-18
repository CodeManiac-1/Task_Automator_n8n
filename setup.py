#!/usr/bin/env python3
"""
Setup script for Task Automator project
"""

import os
import subprocess
import sys

def run_command(command, cwd=None):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, cwd=cwd)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{command}': {e}")
        print(f"Error output: {e.stderr}")
        return None

def setup_python_backend():
    """Setup the Python backend"""
    print("Setting up Python backend...")
    
    # Install Python dependencies
    print("Installing Python dependencies...")
    result = run_command("pip install -r requirements.txt")
    if result is None:
        print("Failed to install Python dependencies")
        return False
    
    print("Python backend setup completed!")
    return True

def setup_dashboard_backend():
    """Setup the dashboard backend"""
    print("Setting up dashboard backend...")
    
    # Install Node.js dependencies
    print("Installing dashboard backend dependencies...")
    result = run_command("npm install", cwd="dashboard/backend")
    if result is None:
        print("Failed to install dashboard backend dependencies")
        return False
    
    print("Dashboard backend setup completed!")
    return True

def setup_dashboard_frontend():
    """Setup the dashboard frontend"""
    print("Setting up dashboard frontend...")
    
    # Install Node.js dependencies
    print("Installing dashboard frontend dependencies...")
    result = run_command("npm install", cwd="dashboard/frontend")
    if result is None:
        print("Failed to install dashboard frontend dependencies")
        return False
    
    print("Dashboard frontend setup completed!")
    return True

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = ".env"
    if not os.path.exists(env_file):
        print("Creating .env file...")
        env_content = """# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Database Configuration
DATABASE_URL=sqlite:///./task_automator.db

# CORS Configuration
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("Created .env file. Please update it with your OpenAI API key.")
    else:
        print(".env file already exists.")

def main():
    """Main setup function"""
    print("Setting up Task Automator project...")
    
    # Create .env file
    create_env_file()
    
    # Setup Python backend
    if not setup_python_backend():
        print("Failed to setup Python backend")
        sys.exit(1)
    
    # Setup dashboard backend
    if not setup_dashboard_backend():
        print("Failed to setup dashboard backend")
        sys.exit(1)
    
    # Setup dashboard frontend
    if not setup_dashboard_frontend():
        print("Failed to setup dashboard frontend")
        sys.exit(1)
    
    print("\nSetup completed successfully!")
    print("\nNext steps:")
    print("1. Update .env file with your OpenAI API key")
    print("2. Run 'python run.py' to start all services")
    print("3. Access the dashboard at http://localhost:5173")

if __name__ == "__main__":
    main() 
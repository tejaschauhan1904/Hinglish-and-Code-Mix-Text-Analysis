#!/usr/bin/env python3
"""
Hinglish Text Analyzer & NLP Suite - Main Application Launcher
Usage:
  python run.py              # Start Modern Web Studio (http://localhost:8000)
  python run.py 3000         # Start Modern Web Studio on custom port
  python run.py --streamlit  # Start Streamlit Dashboard
  python run.py --test       # Run test suite
"""

import sys
import os
import subprocess

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(base_dir, "backend")

    # Add backend directory to sys.path
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

    args = sys.argv[1:]

    if "--streamlit" in args:
        print("Launching Streamlit Dashboard...")
        app_path = os.path.join(backend_dir, "app.py")
        subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])
    elif "--test" in args:
        print("Running test suite...")
        test_path = os.path.join(backend_dir, "test_analyzer.py")
        subprocess.run([sys.executable, test_path])
    else:
        # Default: Launch modern Flask web studio
        from backend.server import main as run_server
        run_server()

if __name__ == "__main__":
    main()

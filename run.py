#!/usr/bin/env python3
"""
Hinglish Text Analyzer & NLP Suite - Main Application Launcher
Usage:
  python run.py              # Start Modern Web Studio (http://localhost:8000)
  python run.py 3000         # Start Modern Web Studio on custom port
  python run.py --streamlit  # Start Streamlit Dashboard
  python run.py --test       # Run test suite
  python run.py --migrate    # Migrate/seed all data into Supabase PostgreSQL
  python run.py --db-status  # Check Supabase database connectivity & table metrics
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
    elif "--migrate" in args:
        print("Running Supabase migration & data seeding...")
        migrate_path = os.path.join(base_dir, "migrate_to_supabase.py")
        subprocess.run([sys.executable, migrate_path])
    elif "--db-status" in args:
        import backend.db as db
        status = db.get_db_status()
        print("\nSupabase Database Status:")
        print(f"  Connected: {status['status']}")
        print(f"  Database: {status['database']}")
        print(f"  Total records across tables: {status['total_records']}")
        print("  Table breakdown:")
        for tbl, count in status["tables"].items():
            print(f"    - {tbl}: {count} records")
        print()
    else:
        # Default: Launch modern Flask web studio
        from backend.server import main as run_server
        run_server()

if __name__ == "__main__":
    main()

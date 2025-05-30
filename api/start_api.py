#!/usr/bin/env python3
"""
Personal Agent Team API - Startup Script

Convenience script to start the API in different modes.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def setup_python_path():
    """Setup Python path to include the project root."""
    # Get the project root (parent of api directory)
    api_dir = Path(__file__).parent
    project_root = api_dir.parent
    
    # Add project root to Python path if not already there
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # Also set PYTHONPATH environment variable
    current_pythonpath = os.environ.get('PYTHONPATH', '')
    if str(project_root) not in current_pythonpath:
        if current_pythonpath:
            os.environ['PYTHONPATH'] = f"{project_root}:{current_pythonpath}"
        else:
            os.environ['PYTHONPATH'] = str(project_root)


def check_environment():
    """Check if required environment variables are set."""
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Add your API keys to the .env file in the project root:")
        print("   OPENAI_API_KEY=sk-your-openai-api-key-here")
        return False
    
    print("✅ Environment variables configured")
    return True


def start_development():
    """Start API in development mode."""
    print("🚀 Starting API in development mode...")
    
    setup_python_path()
    
    if not check_environment():
        return
    
    # Set development environment
    os.environ["DEBUG"] = "true"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["RELOAD"] = "true"
    
    # Start with uvicorn for development - use correct module path
    cmd = [
        "uvicorn", 
        "api.main:app",  # This will work with our PYTHONPATH setup
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload",
        "--log-level", "debug"
    ]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 API stopped")


def start_production():
    """Start API in production mode."""
    print("🚀 Starting API in production mode...")
    
    setup_python_path()
    
    if not check_environment():
        return
    
    # Set production environment
    os.environ["DEBUG"] = "false"
    os.environ["LOG_LEVEL"] = "INFO"
    os.environ["RELOAD"] = "false"
    
    # Start with gunicorn for production
    workers = os.environ.get("WORKERS", "4")
    cmd = [
        "gunicorn",
        "api.main:app",
        "-w", workers,
        "-k", "uvicorn.workers.UvicornWorker",
        "--bind", "0.0.0.0:8000",
        "--access-logfile", "-",
        "--error-logfile", "-"
    ]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 API stopped")


def start_docker():
    """Start API with Docker Compose."""
    print("🐳 Starting API with Docker Compose...")
    
    # Check if docker-compose.yml exists
    if not Path("docker-compose.yml").exists():
        print("❌ docker-compose.yml not found")
        return
    
    # Start services
    cmd = ["docker-compose", "up", "-d"]
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("✅ API started with Docker Compose")
        print("🌐 API available at: http://localhost:8000")
        print("📚 API docs at: http://localhost:8000/docs")
        print("🔍 Health check: http://localhost:8000/health")
        print("\n📊 View logs with: docker-compose logs -f api")
        print("🛑 Stop with: docker-compose down")
    else:
        print("❌ Failed to start Docker Compose")


def show_status():
    """Show API status and useful information."""
    print("📊 Personal Agent Team API Status")
    print("=" * 50)
    
    # Check if API is running
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running at http://localhost:8000")
            
            # Get health info
            health = response.json()
            print(f"🏥 Status: {health.get('status', 'unknown')}")
            print(f"⏱️  Uptime: {health.get('uptime_seconds', 0):.1f} seconds")
            
            # Show available endpoints
            print("\n🔗 Available endpoints:")
            print("   - Health: http://localhost:8000/health")
            print("   - Agents: http://localhost:8000/agents")
            print("   - Docs: http://localhost:8000/docs")
            print("   - Metrics: http://localhost:8000/agents/metrics")
            
        else:
            print("⚠️  API is responding but not healthy")
            
    except Exception as e:
        print("❌ API is not running or not accessible")
        print(f"   Error: {e}")
    
    # Check Docker containers
    try:
        result = subprocess.run(["docker-compose", "ps"], 
                              capture_output=True, text=True)
        if result.returncode == 0 and "api" in result.stdout:
            print("\n🐳 Docker containers:")
            print(result.stdout)
    except:
        pass


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Personal Agent Team API Startup Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_api.py dev          # Start in development mode
  python start_api.py prod         # Start in production mode  
  python start_api.py docker       # Start with Docker Compose
  python start_api.py status       # Show API status
        """
    )
    
    parser.add_argument(
        "mode",
        choices=["dev", "prod", "docker", "status"],
        help="Startup mode"
    )
    
    args = parser.parse_args()
    
    print("🌟 Personal Agent Team API")
    print("Built following Agno's production standards")
    print("-" * 50)
    
    if args.mode == "dev":
        start_development()
    elif args.mode == "prod":
        start_production()
    elif args.mode == "docker":
        start_docker()
    elif args.mode == "status":
        show_status()


if __name__ == "__main__":
    main() 
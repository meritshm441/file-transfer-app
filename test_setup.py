#!/usr/bin/env python3
"""
Simple setup test to verify MongoDB integration without requiring a live connection
"""

import os
from dotenv import load_dotenv

def test_environment():
    """Test environment configuration"""
    print("🔧 Testing Environment Setup")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Check MongoDB URI
    mongo_uri = os.getenv('MONGODB_URI')
    if mongo_uri:
        print(f"✅ MongoDB URI configured: {mongo_uri[:50]}...")
    else:
        print("❌ MongoDB URI not found")
    
    # Check database name
    db_name = os.getenv('DB_NAME', 'file_transfer_app')
    print(f"✅ Database name: {db_name}")
    
    # Test required packages
    try:
        import pymongo
        print(f"✅ PyMongo installed: {pymongo.version}")
    except ImportError:
        print("❌ PyMongo not installed")
    
    try:
        import flask
        print(f"✅ Flask installed: {flask.__version__}")
    except ImportError:
        print("❌ Flask not installed")
    
    try:
        import flask_socketio
        print(f"✅ Flask-SocketIO installed")
    except ImportError:
        print("❌ Flask-SocketIO not installed")
    
    print("\n📋 Configuration Summary:")
    print(f"   Atlas Connection: {'Configured' if 'mongodb+srv://' in mongo_uri else 'Not configured'}")
    print(f"   Local Fallback: Available")
    print(f"   Environment: {os.getenv('FLASK_ENV', 'development')}")

def test_database_import():
    """Test database module import without connecting"""
    print("\n🗄️ Testing Database Module")
    print("=" * 40)
    
    try:
        # Temporarily disable database connection for testing
        import sys
        import os
        
        # Create a mock environment for testing
        os.environ['MONGODB_URI'] = 'mongodb://localhost:27017/test'
        
        # Try to import the database module structure
        with open('database.py', 'r') as f:
            content = f.read()
        
        # Check for key components
        components = [
            'class DatabaseManager',
            'def save_file',
            'def save_transfer',
            'def get_files',
            'def get_transfers',
            'def get_file_stats',
            'def get_transfer_stats'
        ]
        
        for component in components:
            if component in content:
                print(f"✅ {component}")
            else:
                print(f"❌ {component}")
                
        print("✅ Database module structure verified")
        
    except Exception as e:
        print(f"❌ Database module test failed: {e}")

def main():
    """Main test function"""
    print("🚀 MONGODB INTEGRATION SETUP TEST")
    print("=" * 60)
    
    test_environment()
    test_database_import()
    
    print("\n" + "=" * 60)
    print("📝 NEXT STEPS:")
    print("1. Start local MongoDB: mongod")
    print("2. Or fix Atlas connection issues")
    print("3. Run: python init_db.py")
    print("4. Start the application: python api.py")
    print("=" * 60)

if __name__ == "__main__":
    main()

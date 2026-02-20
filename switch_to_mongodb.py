#!/usr/bin/env python3
"""
Script to switch from file-based storage to MongoDB
"""

import os
import shutil
from datetime import datetime

def switch_to_mongodb():
    """Switch application to use MongoDB instead of file storage"""
    print("🔄 Switching to MongoDB Database")
    print("=" * 50)
    
    # Backup current file-based data
    if os.path.exists('data'):
        backup_dir = f'data_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        shutil.copytree('data', backup_dir)
        print(f"✅ Backed up file data to: {backup_dir}")
    
    # Update API to use MongoDB
    api_content = '''# Try to import MongoDB database, fallback to simple file-based storage
try:
    from database import get_database
    print("[API] Using MongoDB database")
    db = get_database()
except ImportError as e:
    print(f"[API] MongoDB import failed: {e}")
    print("[API] Falling back to simple file-based storage")
    from simple_db import get_database
    db = get_database()'''
    
    with open('api.py', 'r') as f:
        current_content = f.read()
    
    # Replace the import section
    lines = current_content.split('\n')
    new_lines = []
    skip_lines = False
    
    for line in lines:
        if 'from simple_db import get_database' in line:
            skip_lines = True
            new_lines.extend(api_content.split('\n'))
            continue
        elif skip_lines and line.strip() == '':
            skip_lines = False
        elif not skip_lines:
            new_lines.append(line)
    
    with open('api.py', 'w') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ Updated api.py to use MongoDB")
    
    # Update server to use MongoDB
    server_content = '''# Try to import MongoDB database, fallback to simple file-based storage
try:
    from database import get_database
    print("[Server] Using MongoDB database")
    db = get_database()
except ImportError as e:
    print(f"[Server] MongoDB import failed: {e}")
    print("[Server] Falling back to simple file-based storage")
    from simple_db import get_database
    db = get_database()'''
    
    with open('server.py', 'r') as f:
        current_content = f.read()
    
    lines = current_content.split('\n')
    new_lines = []
    skip_lines = False
    
    for line in lines:
        if 'from simple_db import get_database' in line:
            skip_lines = True
            new_lines.extend(server_content.split('\n'))
            continue
        elif skip_lines and line.strip() == '':
            skip_lines = False
        elif not skip_lines:
            new_lines.append(line)
    
    with open('server.py', 'w') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ Updated server.py to use MongoDB")
    
    print("\n📋 Next Steps:")
    print("1. Install MongoDB Community Server")
    print("2. Start MongoDB service: mongod")
    print("3. Test connection: python init_db.py")
    print("4. Restart the application: python api.py")
    print("\n🎯 Database Name: file_transfer_app")
    print("🎯 Connection: mongodb://localhost:27017/file_transfer_app")

def switch_to_file_storage():
    """Switch back to file-based storage"""
    print("🔄 Switching to File-Based Storage")
    print("=" * 50)
    
    # Update API to use file storage
    api_content = '''# Use simple file-based storage for now (MongoDB requires installation)
from simple_db import get_database
print("[API] Using file-based storage")
db = get_database()'''
    
    with open('api.py', 'r') as f:
        current_content = f.read()
    
    lines = current_content.split('\n')
    new_lines = []
    skip_lines = False
    
    for line in lines:
        if 'try:' in line and 'MongoDB' in current_content[current_content.find('try:'):current_content.find('try:')+200]:
            skip_lines = True
            new_lines.extend(api_content.split('\n'))
            continue
        elif skip_lines and line.strip() == '':
            skip_lines = False
        elif not skip_lines:
            new_lines.append(line)
    
    with open('api.py', 'w') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ Updated api.py to use file storage")
    
    # Update server to use file storage
    server_content = '''# Use simple file-based storage for now (MongoDB requires installation)
from simple_db import get_database
print("[Server] Using file-based storage")
db = get_database()'''
    
    with open('server.py', 'r') as f:
        current_content = f.read()
    
    lines = current_content.split('\n')
    new_lines = []
    skip_lines = False
    
    for line in lines:
        if 'try:' in line and 'MongoDB' in current_content[current_content.find('try:'):current_content.find('try:')+200]:
            skip_lines = True
            new_lines.extend(server_content.split('\n'))
            continue
        elif skip_lines and line.strip() == '':
            skip_lines = False
        elif not skip_lines:
            new_lines.append(line)
    
    with open('server.py', 'w') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ Updated server.py to use file storage")
    print("\n✅ Switched back to file-based storage")

if __name__ == "__main__":
    print("🗄️ Database Switcher")
    print("=" * 50)
    print("1. Switch to MongoDB")
    print("2. Switch to File Storage")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ")
    
    if choice == "1":
        switch_to_mongodb()
    elif choice == "2":
        switch_to_file_storage()
    else:
        print("Exiting...")

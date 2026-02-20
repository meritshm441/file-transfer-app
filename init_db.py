#!/usr/bin/env python3
"""
Database initialization script for MongoDB
Creates indexes and validates the database connection
"""

from database import db
import sys

def init_database():
    """Initialize MongoDB database with indexes and validation"""
    try:
        print("🔍 Testing MongoDB connection...")
        
        # Test connection
        db.client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        
        print("\n📊 Creating database indexes...")
        
        # Create file collection indexes
        db.files_collection.create_index([('filename', 1)], unique=False)
        db.files_collection.create_index([('upload_date', -1)])
        db.files_collection.create_index([('client_address', 1)])
        db.files_collection.create_index([('file_type', 1)])
        
        print("✅ Files collection indexes created")
        
        # Create transfer collection indexes
        db.transfers_collection.create_index([('transfer_date', -1)])
        db.transfers_collection.create_index([('client_address', 1)])
        db.transfers_collection.create_index([('status', 1)])
        db.transfers_collection.create_index([('filename', 1)])
        
        print("✅ Transfers collection indexes created")
        
        print("\n📈 Database statistics:")
        file_count = db.files_collection.count_documents({})
        transfer_count = db.transfers_collection.count_documents({})
        
        print(f"   Files: {file_count}")
        print(f"   Transfers: {transfer_count}")
        
        if file_count == 0 and transfer_count == 0:
            print("\n🎯 Database is ready for first use!")
        else:
            print("\n📋 Existing data found in database")
        
        print(f"\n🗄️  Database: '{db.db.name}'")
        print(f"📍 MongoDB Atlas Cluster: Connected")
        
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def test_operations():
    """Test basic database operations"""
    try:
        print("\n🧪 Testing database operations...")
        
        # Test file insertion
        test_file = {
            'filename': 'test_init.txt',
            'content': 'Database initialization test file',
            'size': 35,
            'lines': 1,
            'upload_date': datetime.utcnow(),
            'client_address': '127.0.0.1',
            'file_type': 'text',
            'checksum': 'test123'
        }
        
        result = db.files_collection.insert_one(test_file)
        print(f"✅ Test file inserted: {result.inserted_id}")
        
        # Test file retrieval
        retrieved = db.files_collection.find_one({'_id': result.inserted_id})
        print(f"✅ Test file retrieved: {retrieved['filename']}")
        
        # Test transfer insertion
        test_transfer = {
            'client_address': '127.0.0.1',
            'filename': 'test_init.txt',
            'size': 35,
            'transfer_time': 0.5,
            'speed_kbps': 70.0,
            'status': 'success',
            'transfer_date': datetime.utcnow()
        }
        
        result = db.transfers_collection.insert_one(test_transfer)
        print(f"✅ Test transfer inserted: {result.inserted_id}")
        
        # Cleanup test data
        db.files_collection.delete_one({'_id': retrieved['_id']})
        db.transfers_collection.delete_one({'_id': result.inserted_id})
        print("✅ Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Database operations test failed: {e}")
        return False

def main():
    """Main initialization function"""
    print("=" * 60)
    print("🚀 MONGODB DATABASE INITIALIZATION")
    print("=" * 60)
    
    # Initialize database
    if not init_database():
        print("\n❌ Initialization failed. Please check:")
        print("   • MongoDB is running")
        print("   • Connection string in .env is correct")
        print("   • Database permissions are sufficient")
        sys.exit(1)
    
    # Test operations
    if not test_operations():
        print("\n❌ Operations test failed")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ DATABASE INITIALIZATION COMPLETE")
    print("✅ Ready for file transfer operations")
    print("=" * 60)

if __name__ == "__main__":
    main()

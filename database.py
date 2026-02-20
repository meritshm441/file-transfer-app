#!/usr/bin/env python3
"""
MongoDB database models and connection management
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.client = None
        self.db = None
        self.files_collection = None
        self.transfers_collection = None
        self.connect()
    
    def connect(self):
        """Connect to MongoDB"""
        try:
            # Use environment variables for connection, fallback to localhost
            mongo_uri = os.getenv('MONGODB_URI', 'mongodb+srv://meritshm9:Defence%4021@cluster0.8ofq6ud.mongodb.net/?appName=Cluster0')
            db_name = os.getenv('DB_NAME', 'file_transfer_app')
            
            # Try to connect to the specified URI
            try:
                self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
                self.db = self.client[db_name]
                
                # Test connection
                self.client.admin.command('ping')
                print(f"[Database] Connected to MongoDB Atlas")
                
            except Exception as atlas_error:
                print(f"[Database] Atlas connection failed: {atlas_error}")
                print("[Database] Falling back to local MongoDB...")
                
                # Fallback to local MongoDB
                local_uri = 'mongodb://localhost:27017/'
                self.client = MongoClient(local_uri, serverSelectionTimeoutMS=3000)
                self.db = self.client[db_name]
                
                # Test connection
                self.client.admin.command('ping')
                print(f"[Database] Connected to local MongoDB at {local_uri}")
            
            # Initialize collections
            self.files_collection = self.db.files
            self.transfers_collection = self.db.transfers
            
            # Create indexes for better performance
            self.files_collection.create_index([('filename', 1)])
            self.files_collection.create_index([('upload_date', -1)])
            self.transfers_collection.create_index([('transfer_date', -1)])
            self.transfers_collection.create_index([('client_address', 1)])
            
            print(f"[Database] Database '{db_name}' ready")
            
        except Exception as e:
            print(f"[Database Error] Could not connect to any MongoDB instance: {e}")
            print("[Database Error] Please ensure MongoDB is running locally or Atlas connection is working")
            raise
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            print("[Database] Connection closed")
    
    # File operations
    def save_file(self, filename, content, filesize, client_address=None):
        """Save file metadata and content to database"""
        file_doc = {
            'filename': filename,
            'content': content,
            'size': filesize,
            'lines': len(content.splitlines()) if content else 0,
            'upload_date': datetime.utcnow(),
            'client_address': client_address,
            'file_type': self._detect_file_type(filename),
            'checksum': self._calculate_checksum(content)
        }
        
        result = self.files_collection.insert_one(file_doc)
        file_doc['_id'] = result.inserted_id
        return file_doc
    
    def get_files(self, limit=50, skip=0):
        """Get list of files with pagination"""
        files = list(self.files_collection.find(
            {}, 
            {'content': {'$slice': 200}}  # Limit content preview for list view
        ).sort('upload_date', -1).skip(skip).limit(limit))
        
        # Convert ObjectId to string for JSON serialization
        for file in files:
            file['_id'] = str(file['_id'])
            file['has_full_content'] = len(file.get('content', '')) > 200
            
        return files
    
    def get_file_by_id(self, file_id):
        """Get full file details by ID"""
        try:
            file = self.files_collection.find_one({'_id': file_id})
            if file:
                file['_id'] = str(file['_id'])
            return file
        except:
            return None
    
    def get_file_by_name(self, filename):
        """Get file by filename"""
        file = self.files_collection.find_one({'filename': filename})
        if file:
            file['_id'] = str(file['_id'])
        return file
    
    def delete_file(self, file_id):
        """Delete file by ID"""
        result = self.files_collection.delete_one({'_id': file_id})
        return result.deleted_count > 0
    
    def get_file_stats(self):
        """Get file statistics"""
        pipeline = [
            {
                '$group': {
                    '_id': None,
                    'total_files': {'$sum': 1},
                    'total_size': {'$sum': '$size'},
                    'avg_size': {'$avg': '$size'},
                    'total_lines': {'$sum': '$lines'}
                }
            }
        ]
        
        stats = list(self.files_collection.aggregate(pipeline))
        return stats[0] if stats else {
            'total_files': 0,
            'total_size': 0,
            'avg_size': 0,
            'total_lines': 0
        }
    
    # Transfer operations
    def save_transfer(self, client_address, filename, filesize, transfer_time, speed_kbps, status='success'):
        """Save transfer record"""
        transfer_doc = {
            'client_address': client_address,
            'filename': filename,
            'size': filesize,
            'transfer_time': transfer_time,
            'speed_kbps': speed_kbps,
            'status': status,
            'transfer_date': datetime.utcnow()
        }
        
        result = self.transfers_collection.insert_one(transfer_doc)
        transfer_doc['_id'] = result.inserted_id
        return transfer_doc
    
    def get_transfers(self, limit=100, skip=0):
        """Get transfer history"""
        transfers = list(self.transfers_collection.find(
            {}
        ).sort('transfer_date', -1).skip(skip).limit(limit))
        
        # Convert ObjectId to string
        for transfer in transfers:
            transfer['_id'] = str(transfer['_id'])
            
        return transfers
    
    def get_transfer_stats(self):
        """Get transfer statistics"""
        pipeline = [
            {
                '$group': {
                    '_id': None,
                    'total_transfers': {'$sum': 1},
                    'successful_transfers': {
                        '$sum': {'$cond': [{'$eq': ['$status', 'success']}, 1, 0]}
                    },
                    'total_data': {'$sum': '$size'},
                    'avg_speed': {'$avg': '$speed_kbps'},
                    'avg_time': {'$avg': '$transfer_time'}
                }
            }
        ]
        
        stats = list(self.transfers_collection.aggregate(pipeline))
        return stats[0] if stats else {
            'total_transfers': 0,
            'successful_transfers': 0,
            'total_data': 0,
            'avg_speed': 0,
            'avg_time': 0
        }
    
    # Utility methods
    def _detect_file_type(self, filename):
        """Detect file type based on extension"""
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        type_map = {
            'txt': 'text',
            'json': 'json',
            'csv': 'csv',
            'log': 'log',
            'xml': 'xml',
            'html': 'html',
            'css': 'css',
            'js': 'javascript',
            'py': 'python'
        }
        return type_map.get(ext, 'unknown')
    
    def _calculate_checksum(self, content):
        """Simple checksum for content integrity"""
        return str(hash(content)) if content else 'empty'

# Global database instance - lazy initialization
db = None

def get_database():
    """Get database instance with lazy initialization"""
    global db
    if db is None:
        db = DatabaseManager()
    return db

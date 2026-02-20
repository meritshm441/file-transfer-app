#!/usr/bin/env python3
"""
Simple file-based database fallback for testing without MongoDB
"""

import json
import os
from datetime import datetime
import threading

class SimpleDatabase:
    def __init__(self):
        self.data_dir = 'data'
        self.files_file = os.path.join(self.data_dir, 'files.json')
        self.transfers_file = os.path.join(self.data_dir, 'transfers.json')
        self.lock = threading.Lock()
        self._init_storage()
    
    def _init_storage(self):
        """Initialize storage directory and files"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize files storage
        if not os.path.exists(self.files_file):
            with open(self.files_file, 'w') as f:
                json.dump([], f)
        
        # Initialize transfers storage
        if not os.path.exists(self.transfers_file):
            with open(self.transfers_file, 'w') as f:
                json.dump([], f)
    
    def _read_json(self, filepath):
        """Read JSON file safely"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _write_json(self, filepath, data):
        """Write JSON file safely"""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    # File operations
    def save_file(self, filename, content, filesize, client_address=None):
        """Save file metadata and content"""
        files = self._read_json(self.files_file)
        
        file_doc = {
            '_id': f"file_{len(files) + 1}_{int(datetime.now().timestamp())}",
            'filename': filename,
            'content': content,
            'size': filesize,
            'lines': len(content.splitlines()) if content else 0,
            'upload_date': datetime.utcnow().isoformat(),
            'client_address': client_address,
            'file_type': self._detect_file_type(filename),
            'checksum': self._calculate_checksum(content)
        }
        
        files.append(file_doc)
        self._write_json(self.files_file, files)
        return file_doc
    
    def get_files(self, limit=50, skip=0):
        """Get list of files with pagination"""
        files = self._read_json(self.files_file)
        
        # Sort by upload_date (newest first)
        files.sort(key=lambda x: x.get('upload_date', ''), reverse=True)
        
        # Apply pagination
        paginated_files = files[skip:skip + limit]
        
        # Limit content preview for list view
        for file in paginated_files:
            if len(file.get('content', '')) > 200:
                file['has_full_content'] = True
                file['preview'] = file['content'][:200] + '...'
            else:
                file['has_full_content'] = False
                file['preview'] = file['content']
        
        return paginated_files
    
    def get_file_by_id(self, file_id):
        """Get full file details by ID"""
        files = self._read_json(self.files_file)
        for file in files:
            if file.get('_id') == file_id:
                return file
        return None
    
    def get_file_by_name(self, filename):
        """Get file by filename"""
        files = self._read_json(self.files_file)
        for file in files:
            if file.get('filename') == filename:
                return file
        return None
    
    def delete_file(self, file_id):
        """Delete file by ID"""
        files = self._read_json(self.files_file)
        original_count = len(files)
        files = [f for f in files if f.get('_id') != file_id]
        
        if len(files) < original_count:
            self._write_json(self.files_file, files)
            return True
        return False
    
    def get_file_stats(self):
        """Get file statistics"""
        files = self._read_json(self.files_file)
        
        if not files:
            return {
                'total_files': 0,
                'total_size': 0,
                'avg_size': 0,
                'total_lines': 0
            }
        
        total_files = len(files)
        total_size = sum(f.get('size', 0) for f in files)
        total_lines = sum(f.get('lines', 0) for f in files)
        avg_size = total_size / total_files if total_files > 0 else 0
        
        return {
            'total_files': total_files,
            'total_size': total_size,
            'avg_size': avg_size,
            'total_lines': total_lines
        }
    
    # Transfer operations
    def save_transfer(self, client_address, filename, filesize, transfer_time, speed_kbps, status='success'):
        """Save transfer record"""
        transfers = self._read_json(self.transfers_file)
        
        transfer_doc = {
            '_id': f"transfer_{len(transfers) + 1}_{int(datetime.now().timestamp())}",
            'client_address': client_address,
            'filename': filename,
            'size': filesize,
            'transfer_time': transfer_time,
            'speed_kbps': speed_kbps,
            'status': status,
            'transfer_date': datetime.utcnow().isoformat()
        }
        
        transfers.append(transfer_doc)
        self._write_json(self.transfers_file, transfers)
        return transfer_doc
    
    def get_transfers(self, limit=100, skip=0):
        """Get transfer history"""
        transfers = self._read_json(self.transfers_file)
        
        # Sort by transfer_date (newest first)
        transfers.sort(key=lambda x: x.get('transfer_date', ''), reverse=True)
        
        # Apply pagination
        return transfers[skip:skip + limit]
    
    def get_transfer_stats(self):
        """Get transfer statistics"""
        transfers = self._read_json(self.transfers_file)
        
        if not transfers:
            return {
                'total_transfers': 0,
                'successful_transfers': 0,
                'total_data': 0,
                'avg_speed': 0,
                'avg_time': 0
            }
        
        total_transfers = len(transfers)
        successful_transfers = len([t for t in transfers if t.get('status') == 'success'])
        total_data = sum(t.get('size', 0) for t in transfers)
        
        successful_transfers_data = [t for t in transfers if t.get('status') == 'success']
        avg_speed = sum(t.get('speed_kbps', 0) for t in successful_transfers_data) / len(successful_transfers_data) if successful_transfers_data else 0
        avg_time = sum(t.get('transfer_time', 0) for t in successful_transfers_data) / len(successful_transfers_data) if successful_transfers_data else 0
        
        return {
            'total_transfers': total_transfers,
            'successful_transfers': successful_transfers,
            'total_data': total_data,
            'avg_speed': avg_speed,
            'avg_time': avg_time
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

# Create global database instance
db = SimpleDatabase()

def get_database():
    """Get database instance"""
    return db

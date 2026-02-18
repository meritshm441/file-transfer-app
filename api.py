#!/usr/bin/env python3
"""
REST API with real-time updates for file transfer results
Modern backend for frontend engineering
"""

from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import glob
import os
import time
from datetime import datetime
import threading
import subprocess
import sys

app = Flask(__name__)
app.config['SECRET_KEY'] = 'file-transfer-secret'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

def get_received_files():
    """Get list of received files with metadata"""
    files = []
    for filepath in glob.glob('received_*.txt'):
        try:
            stat = os.stat(filepath)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            files.append({
                'id': filepath,
                'name': filepath,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'content': content,
                'lines': len(content.splitlines()),
                'preview': content[:200] + '...' if len(content) > 200 else content
            })
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
    
    files.sort(key=lambda x: x['modified'], reverse=True)
    return files

@app.route('/api/files')
def api_files():
    """REST API endpoint for file list"""
    return jsonify({
        'files': get_received_files(),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/files/<filename>')
def api_file_detail(filename):
    """Get detailed file info"""
    if filename.startswith('received_') and filename.endswith('.txt'):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            stat = os.stat(filename)
            return jsonify({
                'name': filename,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'content': content,
                'lines': len(content.splitlines())
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 404
    return jsonify({'error': 'File not found'}), 404

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload and transfer a file with progress tracking"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file temporarily
        temp_filename = f"temp_upload_{int(time.time())}.txt"
        file.save(temp_filename)
        
        # Get server info (assume localhost:9000 for demo)
        server_ip = '127.0.0.1'
        server_port = 9000
        
        # Start transfer in background thread with progress tracking
        def transfer_with_progress():
            try:
                # Emit start event
                socketio.emit('transfer_start', {
                    'filename': file.filename,
                    'size': os.path.getsize(temp_filename)
                })
                
                # Run client transfer script with progress monitoring
                client_script = os.path.join('src', 'client.py')
                process = subprocess.Popen([
                    sys.executable, client_script, '--send', 
                    server_ip, str(server_port), temp_filename
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                # Monitor progress
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        # Parse progress from client output
                        if '[TCP Transfer] Progress:' in output:
                            try:
                                progress_part = output.split('Progress:')[1].split('%')[0].strip()
                                progress = float(progress_part)
                                socketio.emit('transfer_progress', {
                                    'filename': file.filename,
                                    'progress': progress,
                                    'message': output.strip()
                                })
                            except:
                                pass
                        elif 'TRANSFER COMPLETE' in output:
                            socketio.emit('transfer_complete', {
                                'filename': file.filename,
                                'message': output.strip()
                            })
                        elif '[TCP Transfer Error]' in output:
                            socketio.emit('transfer_error', {
                                'filename': file.filename,
                                'error': output.strip()
                            })
                
                # Clean up
                process.wait()
                os.remove(temp_filename)
                
            except Exception as e:
                socketio.emit('transfer_error', {
                    'filename': file.filename,
                    'error': str(e)
                })
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
        
        # Start background transfer
        thread = threading.Thread(target=transfer_with_progress, daemon=True)
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Transfer started',
            'filename': file.filename
        })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<filename>')
def download(filename):
    """Download a received file"""
    if filename.startswith('received_') and filename.endswith('.txt'):
        return send_from_directory('.', filename, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

@app.route('/api/stats')
def api_stats():
    """Get statistics"""
    files = get_received_files()
    return jsonify({
        'total_files': len(files),
        'total_size': sum(f['size'] for f in files),
        'total_lines': sum(f['lines'] for f in files),
        'last_updated': datetime.now().isoformat()
    })

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('files_update', {'files': get_received_files()})
    emit('stats_update', {
        'total_files': len(get_received_files()),
        'total_size': sum(f['size'] for f in get_received_files()),
        'total_lines': sum(f['lines'] for f in get_received_files())
    })

def broadcast_updates():
    """Background thread to broadcast file updates"""
    last_files = []
    while True:
        current_files = get_received_files()
        if current_files != last_files:
            socketio.emit('files_update', {'files': current_files})
            socketio.emit('stats_update', {
                'total_files': len(current_files),
                'total_size': sum(f['size'] for f in current_files),
                'total_lines': sum(f['lines'] for f in current_files)
            })
            last_files = current_files
        time.sleep(2)

if __name__ == '__main__':
    # Start background update thread
    update_thread = threading.Thread(target=broadcast_updates, daemon=True)
    update_thread.start()
    
    print("🚀 File Transfer API Server")
    print("📡 WebSocket: ws://localhost:5001")
    print("🌐 REST API: http://localhost:5001/api")
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)

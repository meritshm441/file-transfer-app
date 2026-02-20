#!/usr/bin/env python3
"""
REST API with real-time updates for file transfer results
Modern backend for frontend engineering
"""

from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
import time
from datetime import datetime
import threading
import subprocess
import sys
import uuid

# Use simple file-based storage for now (MongoDB requires installation)
from simple_db import get_database
print("[API] Using file-based storage")
db = get_database()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'file-transfer-secret'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

def get_received_files():
    """Get list of received files from MongoDB"""
    try:
        files = db.get_files(limit=50)
        # Convert to format expected by frontend
        formatted_files = []
        for file in files:
            formatted_files.append({
                'id': file['_id'],
                'name': file['filename'],
                'size': file['size'],
                'modified': file['upload_date'],
                'content': file['content'],
                'lines': file['lines'],
                'preview': file['content'][:200] + '...' if len(file['content']) > 200 else file['content'],
                'file_type': file.get('file_type', 'unknown'),
                'client_address': file.get('client_address')
            })
        return formatted_files
    except Exception as e:
        print(f"Error getting files from database: {e}")
        return []

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
    try:
        file = db.get_file_by_name(filename)
        if file:
            return jsonify({
                'id': file['_id'],
                'name': file['filename'],
                'size': file['size'],
                'modified': file['upload_date'],
                'content': file['content'],
                'lines': file['lines'],
                'file_type': file.get('file_type', 'unknown'),
                'client_address': file.get('client_address')
            })
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
        
        # Start transfer in background thread with progress tracking
        def transfer_with_progress():
            temp_path = temp_filename
            transfer_id = str(uuid.uuid4())

            def emit_progress(protocol, stage, progress, message):
                if protocol == 'udp':
                    overall_progress = round(progress * 0.2, 2)
                else:
                    overall_progress = round(20 + (progress * 0.8), 2)

                socketio.emit('transfer_progress', {
                    'transfer_id': transfer_id,
                    'filename': file.filename,
                    'protocol': protocol,
                    'stage': stage,
                    'progress': progress,
                    'overall_progress': min(overall_progress, 100),
                    'message': message
                })

            try:
                # Emit start event
                socketio.emit('transfer_start', {
                    'transfer_id': transfer_id,
                    'filename': file.filename,
                    'size': os.path.getsize(temp_filename)
                })

                client_script = os.path.join('src', 'client.py')
                discovered_servers = []

                # UDP discovery stage
                emit_progress('udp', 'discovery', 5, 'Starting UDP server discovery...')
                discover_process = subprocess.Popen(
                    [sys.executable, client_script, '--discover'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                while True:
                    output = discover_process.stdout.readline()
                    if output == '' and discover_process.poll() is not None:
                        break
                    if not output:
                        continue

                    line = output.strip()
                    if not line:
                        continue

                    if '\t' in line:
                        parts = line.split('\t')
                        if len(parts) == 3:
                            discovered_servers.append({
                                'name': parts[0],
                                'address': parts[1],
                                'tcp_port': int(parts[2])
                            })
                    elif '[UDP Discovery]' in line:
                        if 'Broadcast sent' in line:
                            progress = 35
                        elif 'Found server:' in line:
                            progress = 75
                        elif 'Found' in line and 'server(s)' in line:
                            progress = 100
                        elif 'No servers found' in line:
                            progress = 100
                        else:
                            progress = 15

                        emit_progress('udp', 'discovery', progress, line)

                discover_process.wait()

                if not discovered_servers:
                    socketio.emit('transfer_error', {
                        'transfer_id': transfer_id,
                        'filename': file.filename,
                        'protocol': 'udp',
                        'error': 'UDP discovery completed but no transfer server was found.'
                    })
                    return

                selected_server = discovered_servers[0]
                server_ip = selected_server['address']
                server_port = selected_server['tcp_port']
                emit_progress('udp', 'discovery', 100, f"Selected server {selected_server['name']} ({server_ip}:{server_port})")

                # Run TCP transfer with progress monitoring
                client_script = os.path.join('src', 'client.py')
                process = subprocess.Popen([
                    sys.executable, client_script, '--send', 
                    server_ip, str(server_port), temp_path
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                # Monitor progress
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        line = output.strip()

                        # Parse TCP transfer stages from client output
                        if '[TCP Transfer] Connecting' in line:
                            emit_progress('tcp', 'connect', 5, line)
                        elif '[TCP Transfer] Connected' in line:
                            emit_progress('tcp', 'connect', 15, line)
                        elif '[TCP Transfer] Starting file upload' in line:
                            emit_progress('tcp', 'upload', 20, line)
                        elif '[TCP Transfer] Progress:' in line:
                            try:
                                progress_part = line.split('Progress:')[1].split('%')[0].strip()
                                progress = float(progress_part)
                                emit_progress('tcp', 'upload', progress, line)
                            except:
                                pass
                        elif 'TRANSFER COMPLETE' in line:
                            emit_progress('tcp', 'complete', 100, 'TCP transfer finished.')
                            socketio.emit('transfer_complete', {
                                'transfer_id': transfer_id,
                                'filename': file.filename,
                                'message': 'UDP discovery and TCP transfer complete.'
                            })
                        elif '[TCP Transfer Error]' in line:
                            socketio.emit('transfer_error', {
                                'transfer_id': transfer_id,
                                'filename': file.filename,
                                'protocol': 'tcp',
                                'error': line
                            })
                            return

                stderr_output = process.stderr.read().strip()
                process.wait()

                if process.returncode != 0:
                    socketio.emit('transfer_error', {
                        'transfer_id': transfer_id,
                        'filename': file.filename,
                        'protocol': 'tcp',
                        'error': stderr_output or 'TCP transfer process failed.'
                    })
                
            except Exception as e:
                socketio.emit('transfer_error', {
                    'transfer_id': transfer_id,
                    'filename': file.filename,
                    'error': str(e)
                })
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        
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
    """Download a received file from database"""
    try:
        file = db.get_file_by_name(filename)
        if file:
            # Create temporary file for download
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
                temp_file.write(file['content'])
                temp_path = temp_file.name
            
            return send_from_directory(os.path.dirname(temp_path), os.path.basename(temp_path), 
                                     as_attachment=True, download_name=filename)
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def api_stats():
    """Get statistics from database"""
    try:
        file_stats = db.get_file_stats()
        transfer_stats = db.get_transfer_stats()
        
        return jsonify({
            'files': {
                'total_files': file_stats['total_files'],
                'total_size': file_stats['total_size'],
                'total_lines': file_stats['total_lines'],
                'avg_size': file_stats['avg_size']
            },
            'transfers': {
                'total_transfers': transfer_stats['total_transfers'],
                'successful_transfers': transfer_stats['successful_transfers'],
                'total_data': transfer_stats['total_data'],
                'avg_speed': transfer_stats['avg_speed'],
                'avg_time': transfer_stats['avg_time']
            },
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

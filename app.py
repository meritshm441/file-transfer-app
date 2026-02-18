#!/usr/bin/env python3
"""
Flask web app to display file transfer results
Shows received files with their contents and metadata
"""

from flask import Flask, render_template, send_from_directory, jsonify
import glob
import os
from datetime import datetime

app = Flask(__name__)

def get_received_files():
    """Get list of received files with metadata"""
    files = []
    for filepath in glob.glob('received_*.txt'):
        try:
            stat = os.stat(filepath)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            files.append({
                'name': filepath,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'content': content,
                'lines': len(content.splitlines()),
                'preview': content[:200] + '...' if len(content) > 200 else content
            })
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
    
    # Sort by modification time (newest first)
    files.sort(key=lambda x: x['modified'], reverse=True)
    return files

@app.route('/')
def index():
    """Main page showing all received files"""
    files = get_received_files()
    return render_template('index.html', files=files)

@app.route('/api/files')
def api_files():
    """JSON API for file list"""
    return jsonify({'files': get_received_files()})

@app.route('/download/<filename>')
def download(filename):
    """Download a received file"""
    if filename.startswith('received_') and filename.endswith('.txt'):
        return send_from_directory('.', filename, as_attachment=True)
    return "File not found", 404

if __name__ == '__main__':
    print("Starting Flask web app...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)

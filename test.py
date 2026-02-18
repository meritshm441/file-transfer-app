#!/usr/bin/env python3
"""
Simple test script for the file transfer application
Run this to verify both UDP and TCP functionality
"""

import subprocess
import time
import os
import signal
import sys
import pathlib

def create_test_file():
    """Create a test file for transfers"""
    repo_root = pathlib.Path(__file__).resolve().parent
    test_dir = repo_root / "test_files"
    test_dir.mkdir(parents=True, exist_ok=True)
    filename = test_dir / "test_file.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("This is a test file for the socket programming assignment.\n")
        f.write("It demonstrates both UDP discovery and TCP file transfer.\n")
        f.write("X" * 1024)  # Add some bulk data
    return str(filename)

def run_test():
    print("=" * 60)
    print("TESTING FILE TRANSFER APPLICATION")
    print("=" * 60)

    repo_root = pathlib.Path(__file__).resolve().parent
    server_script = repo_root / "server.py"
    client_script = repo_root / "src" / "client.py"
    
    # Create test file
    test_file = create_test_file()
    print(f"✓ Created test file: {test_file} ({os.path.getsize(test_file)} bytes)")
    
    # Start server in background
    print("\n1. Starting server...")
    server_process = subprocess.Popen(
        [sys.executable, str(server_script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=str(repo_root)
    )
    time.sleep(2)  # Give server time to start
    
    # Run client discovery
    print("\n2. Testing UDP discovery...")
    discovery_result = subprocess.run(
        [sys.executable, str(client_script), '--discover'],
        capture_output=True,
        text=True,
        cwd=str(repo_root)
    )
    print(discovery_result.stdout)
    
    if "server" in discovery_result.stdout.lower():
        print("✓ UDP discovery working")
    else:
        print("✗ UDP discovery failed")
    
    # Extract server info from discovery
    lines = [line.strip() for line in discovery_result.stdout.splitlines() if line.strip()]
    server_line = None
    for line in lines:
        parts = line.split('\t')
        if len(parts) >= 3:
            server_line = parts
            break

    if server_line:
        server_name = server_line[0]
        server_ip = server_line[1]
        server_port = server_line[2]
            
        # Test TCP transfer
        print(f"\n3. Testing TCP file transfer to {server_ip}:{server_port}...")
        transfer_result = subprocess.run(
            [sys.executable, str(client_script), '--send', server_ip, server_port, test_file],
            capture_output=True,
            text=True,
            cwd=str(repo_root)
        )
        print(transfer_result.stdout)
        
        if "TRANSFER COMPLETE" in transfer_result.stdout:
            print("✓ TCP file transfer working")
        else:
            print("✗ TCP file transfer failed")
    else:
        print("✗ Could not parse server info from discovery output")
    
    # Cleanup
    print("\n4. Cleaning up...")
    server_process.terminate()
    server_process.wait()
    
    if os.path.exists(test_file):
        os.remove(test_file)
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    run_test()
#!/usr/bin/env python3
"""
File Transfer Server with UDP Discovery and TCP Transfer
Course Assignment: Socket Programming (UDP + TCP)
Python Version: 3.12.4
"""

import socket
import threading
import os
import time
import json
from datetime import datetime

# Configuration
UDP_DISCOVERY_PORT = 8888
TCP_BASE_PORT = 9000
BUFFER_SIZE = 8192
SERVER_NAME = socket.gethostname()

class FileTransferServer:
    def __init__(self):
        self.tcp_port = None
        self.running = True
        self.transfer_history = []
        self.lock = threading.Lock()
        
    def start_udp_discovery(self):
        """UDP: Listen for discovery broadcasts"""
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        try:
            udp_socket.bind(('', UDP_DISCOVERY_PORT))
            print(f"[UDP Discovery] Listening on port {UDP_DISCOVERY_PORT}")
            
            while self.running:
                udp_socket.settimeout(2.0)
                
                try:
                    data, client_addr = udp_socket.recvfrom(1024)
                    message = data.decode('utf-8')
                    
                    if message == "FILE_TRANSFER_DISCOVERY":
                        response = {
                            'server_name': SERVER_NAME,
                            'tcp_port': self.tcp_port or TCP_BASE_PORT,
                            'status': 'available',
                            'timestamp': time.time()
                        }
                        udp_socket.sendto(json.dumps(response).encode(), client_addr)
                        print(f"[UDP Discovery] Responded to {client_addr}")
                        
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"[UDP Discovery Error] {e}")
                    
        except Exception as e:
            print(f"[UDP Error] {e}")
        finally:
            udp_socket.close()
    
    def handle_tcp_client(self, client_socket, client_addr):
        """TCP: Handle file transfer with a single client"""
        try:
            # Receive file metadata
            metadata_json = client_socket.recv(1024).decode('utf-8')
            metadata = json.loads(metadata_json)
            
            filename = metadata['filename']
            filesize = metadata['filesize']
            
            print(f"[TCP Transfer] Client {client_addr} wants to send: {filename} ({filesize} bytes)")
            
            # Acknowledge receipt
            client_socket.send(b"READY")
            
            # Receive the file
            received_bytes = 0
            start_time = time.time()
            last_progress = 0
            
            # Create unique filename
            base_name = os.path.basename(filename)
            name, ext = os.path.splitext(base_name)
            save_name = f"received_{name}_{int(time.time())}{ext}"
            
            with open(save_name, 'wb') as f:
                while received_bytes < filesize:
                    chunk = client_socket.recv(BUFFER_SIZE)
                    if not chunk:
                        break
                    f.write(chunk)
                    received_bytes += len(chunk)
                    
                    # Progress reporting
                    progress = (received_bytes / filesize) * 100
                    if int(progress) >= last_progress + 10:
                        print(f"[TCP Transfer] Progress: {progress:.1f}%")
                        last_progress = int(progress)
            
            transfer_time = time.time() - start_time
            speed = (filesize / transfer_time / 1024) if transfer_time > 0 else 0
            
            # Log transfer (thread-safe)
            with self.lock:
                self.transfer_history.append({
                    'client': str(client_addr),
                    'filename': filename,
                    'size': filesize,
                    'time': transfer_time,
                    'speed': speed,
                    'timestamp': datetime.now().isoformat()
                })
            
            # Send completion confirmation
            result = {
                'status': 'success',
                'bytes_received': received_bytes,
                'transfer_time': round(transfer_time, 2),
                'speed_kbps': round(speed, 2)
            }
            client_socket.send(json.dumps(result).encode())
            
            print(f"[TCP Transfer] Complete: {received_bytes} bytes in {transfer_time:.2f}s ({speed:.2f} KB/s)")
            
        except Exception as e:
            print(f"[TCP Error] {e}")
            try:
                error_msg = {'status': 'error', 'message': str(e)}
                client_socket.send(json.dumps(error_msg).encode())
            except:
                pass
        finally:
            client_socket.close()
    
    def start_tcp_server(self):
        """TCP: Listen for file transfer connections"""
        # Find an available port
        port = TCP_BASE_PORT
        tcp_socket = None
        
        while port < TCP_BASE_PORT + 100:
            try:
                tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                tcp_socket.bind(('', port))
                self.tcp_port = port
                break
            except OSError:
                port += 1
                if tcp_socket:
                    tcp_socket.close()
                continue
        
        if not tcp_socket:
            print("[TCP Server] No available ports found!")
            return
            
        tcp_socket.listen(5)
        print(f"[TCP Server] Listening on port {self.tcp_port}")
        
        while self.running:
            try:
                tcp_socket.settimeout(2.0)
                client_socket, client_addr = tcp_socket.accept()
                print(f"[TCP Server] Connection from {client_addr}")
                
                # Handle client in new thread
                client_thread = threading.Thread(
                    target=self.handle_tcp_client,
                    args=(client_socket, client_addr)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"[TCP Server Error] {e}")
        
        if tcp_socket:
            tcp_socket.close()
    
    def start(self):
        """Start both UDP discovery and TCP transfer servers"""
        print("=" * 60)
        print(f"FILE TRANSFER SERVER - {SERVER_NAME}")
        print(f"Python Version: 3.12.4")
        print("=" * 60)
        
        # Start UDP discovery thread
        udp_thread = threading.Thread(target=self.start_udp_discovery)
        udp_thread.daemon = True
        udp_thread.start()
        
        # Start TCP server (main thread)
        try:
            self.start_tcp_server()
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the server"""
        self.running = False
        print("\n[Server] Shutting down...")
        
        # Print transfer statistics
        if self.transfer_history:
            print("\n=== Transfer Statistics ===")
            total_bytes = sum(t['size'] for t in self.transfer_history)
            total_time = sum(t['time'] for t in self.transfer_history)
            print(f"Total transfers: {len(self.transfer_history)}")
            print(f"Total data: {total_bytes:,} bytes ({total_bytes/1024/1024:.2f} MB)")
            if total_time > 0:
                print(f"Average speed: {total_bytes/total_time/1024:.2f} KB/s")

if __name__ == "__main__":
    server = FileTransferServer()
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
    except Exception as e:
        print(f"[Fatal Error] {e}")
        server.stop()
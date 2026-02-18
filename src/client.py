#!/usr/bin/env python3
"""
File Transfer Client with UDP Discovery and TCP Transfer
Course Assignment: Socket Programming (UDP + TCP)
Author: Group [Your Group Number]
Date: February 2026
"""

import socket
import threading
import os
import time
import json
import sys

# Configuration
UDP_DISCOVERY_PORT = 8888
UDP_BROADCAST_ADDR = '<broadcast>'
BUFFER_SIZE = 8192

class FileTransferClient:
    def __init__(self):
        self.servers = {}  # {server_id: {'name': name, 'tcp_port': port, 'address': addr, 'last_seen': time}}
        
    def discover_servers(self, timeout=3):
        """
        UDP Broadcast: Find all file transfer servers on the local network
        """
        print("\n[UDP Discovery] Searching for servers...")
        
        # Create UDP socket for broadcasting
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udp_socket.settimeout(timeout)
        
        # Send discovery broadcast
        discovery_msg = "FILE_TRANSFER_DISCOVERY"
        
        try:
            udp_socket.sendto(discovery_msg.encode(), (UDP_BROADCAST_ADDR, UDP_DISCOVERY_PORT))
            print(f"[UDP Discovery] Broadcast sent on port {UDP_DISCOVERY_PORT}")
            
            # Listen for responses
            start_time = time.time()
            found_servers = []
            
            while time.time() - start_time < timeout:
                try:
                    data, server_addr = udp_socket.recvfrom(1024)
                    response = json.loads(data.decode())
                    
                    server_id = f"{server_addr[0]}:{response['tcp_port']}"
                    if server_id not in self.servers:
                        self.servers[server_id] = {
                            'name': response['server_name'],
                            'tcp_port': response['tcp_port'],
                            'address': server_addr[0],
                            'last_seen': time.time()
                        }
                        found_servers.append(f"{response['server_name']} ({server_addr[0]}:{response['tcp_port']})")
                        print(f"[UDP Discovery] Found server: {response['server_name']} at {server_addr[0]}")
                        
                except socket.timeout:
                    continue
                except json.JSONDecodeError:
                    continue
            
            if found_servers:
                print(f"[UDP Discovery] Found {len(found_servers)} server(s)")
            else:
                print("[UDP Discovery] No servers found")
                
            return list(self.servers.values())
            
        except Exception as e:
            print(f"[UDP Discovery Error] {e}")
            return []
        finally:
            udp_socket.close()
    
    def transfer_file_tcp(self, server_ip, server_port, filepath):
        """
        TCP: Transfer a file to the selected server
        """
        if not os.path.exists(filepath):
            print(f"[Error] File not found: {filepath}")
            return False
        
        filesize = os.path.getsize(filepath)
        filename = os.path.basename(filepath)
        
        print(f"\n[TCP Transfer] Connecting to {server_ip}:{server_port}")
        print(f"[TCP Transfer] File: {filename} ({filesize} bytes)")
        
        # Create TCP socket
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.settimeout(30)
        
        try:
            # Connect to server
            tcp_socket.connect((server_ip, server_port))
            print("[TCP Transfer] Connected")
            
            # Send file metadata
            metadata = {
                'filename': filename,
                'filesize': filesize
            }
            tcp_socket.send(json.dumps(metadata).encode())
            
            # Wait for server acknowledgment
            ack = tcp_socket.recv(1024).decode()
            if ack != "READY":
                print("[TCP Transfer] Server not ready")
                return False
            
            print("[TCP Transfer] Starting file upload...")
            
            # Send file in chunks
            sent_bytes = 0
            start_time = time.time()
            last_progress = 0
            
            with open(filepath, 'rb') as f:
                while sent_bytes < filesize:
                    chunk = f.read(BUFFER_SIZE)
                    if not chunk:
                        break
                    
                    tcp_socket.send(chunk)
                    sent_bytes += len(chunk)
                    
                    # Show progress
                    progress = (sent_bytes / filesize) * 100
                    if int(progress) >= last_progress + 10:
                        print(f"[TCP Transfer] Progress: {progress:.1f}% ({sent_bytes}/{filesize} bytes)")
                        last_progress = int(progress)
            
            # Get server confirmation
            response_data = tcp_socket.recv(1024).decode()
            result = json.loads(response_data)
            
            transfer_time = time.time() - start_time
            speed = filesize / transfer_time / 1024  # KB/s
            
            print("\n" + "=" * 40)
            print("TRANSFER COMPLETE")
            print("=" * 40)
            print(f"File: {filename}")
            print(f"Size: {filesize} bytes ({filesize/1024:.2f} KB)")
            print(f"Time: {transfer_time:.2f} seconds")
            print(f"Speed: {speed:.2f} KB/s")
            print(f"Status: {result.get('status', 'unknown')}")
            
            return True
            
        except socket.timeout:
            print("[TCP Transfer Error] Connection timeout")
            return False
        except ConnectionRefusedError:
            print("[TCP Transfer Error] Connection refused - server may be down")
            return False
        except Exception as e:
            print(f"[TCP Transfer Error] {e}")
            return False
        finally:
            tcp_socket.close()
    
    def interactive_mode(self):
        """Interactive client with menu"""
        print("=" * 50)
        print("FILE TRANSFER CLIENT")
        print("=" * 50)
        
        while True:
            print("\n--- Menu ---")
            print("1. Discover servers (UDP broadcast)")
            print("2. Transfer file to server (TCP)")
            print("3. List discovered servers")
            print("4. Exit")
            
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == '1':
                servers = self.discover_servers()
                if servers:
                    print("\nDiscovered servers:")
                    for i, server in enumerate(servers, 1):
                        print(f"  {i}. {server['name']} at {server['address']}:{server['tcp_port']}")
                
            elif choice == '2':
                if not self.servers:
                    print("No servers discovered. Please discover servers first (option 1).")
                    continue
                
                # List servers
                print("\nAvailable servers:")
                server_list = list(self.servers.values())
                for i, server in enumerate(server_list, 1):
                    print(f"  {i}. {server['name']} ({server['address']}:{server['tcp_port']})")
                
                # Select server
                try:
                    server_idx = int(input("\nSelect server number: ")) - 1
                    if server_idx < 0 or server_idx >= len(server_list):
                        print("Invalid selection")
                        continue
                    
                    selected = server_list[server_idx]
                    
                    # Get file path
                    filepath = input("Enter file path to transfer: ").strip()
                    
                    # Transfer file
                    self.transfer_file_tcp(selected['address'], selected['tcp_port'], filepath)
                    
                except ValueError:
                    print("Invalid input")
                except KeyboardInterrupt:
                    print("\nTransfer cancelled")
                    
            elif choice == '3':
                if self.servers:
                    print("\nDiscovered servers:")
                    for server_id, info in self.servers.items():
                        age = time.time() - info['last_seen']
                        print(f"  • {info['name']} at {info['address']}:{info['tcp_port']} (last seen: {age:.0f}s ago)")
                else:
                    print("No servers discovered yet")
                    
            elif choice == '4':
                print("Goodbye!")
                break
                
            else:
                print("Invalid option")

def main():
    client = FileTransferClient()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        # Command line mode for scripting
        if sys.argv[1] == '--discover':
            servers = client.discover_servers()
            for server in servers:
                print(f"{server['name']}\t{server['address']}\t{server['tcp_port']}")
        elif sys.argv[1] == '--send' and len(sys.argv) >= 5:
            server_ip = sys.argv[2]
            server_port = int(sys.argv[3])
            filepath = sys.argv[4]
            client.transfer_file_tcp(server_ip, server_port, filepath)
    else:
        # Interactive mode
        client.interactive_mode()

if __name__ == "__main__":
    main()
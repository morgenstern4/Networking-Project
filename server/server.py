import socket
import threading
import os
import time
import random
from congestion.controller import CongestionController
from PyQt5.QtCore import pyqtSignal, QObject

HOST = 'localhost'
PORT = 5000
FILE_DIR = 'files'
CHUNK_SIZE = 1024

class ServerSignals(QObject):
    update_graph = pyqtSignal(float)
    status_update = pyqtSignal(str)

def simulate_packet_loss():
    return random.random() < 0.05

def handle_client(conn, addr, signals):
    print(f"[+] Client connected: {addr}")
    cc = CongestionController()
    signals.status_update.emit(f"Client connected: {addr}")
    
    try:
        while True:
            command = conn.recv(1024).decode().strip()
            if not command:
                break
            
            if command == "LIST":
                files = os.listdir(FILE_DIR)
                conn.sendall(("\n".join(files) + "\n").encode())
            elif command.startswith("GET "):
                filename = command[4:].strip()
                filepath = os.path.join(FILE_DIR, filename)
                
                if not os.path.exists(filepath):
                    conn.sendall(b"ERROR: File not found\n")
                    continue
                
                file_size = os.path.getsize(filepath)
                conn.sendall(f"{file_size}".encode())
                ack = conn.recv(1024)

                with open(filepath, "rb") as f:
                    bytes_sent = 0
                    while True:
                        chunk = f.read(CHUNK_SIZE)
                        if not chunk:
                            break
                            
                        if simulate_packet_loss():
                            signals.status_update.emit(f"[{addr}] Packet loss simulated")
                            cc.on_loss()
                            signals.update_graph.emit(cc.cwnd)
                            continue
                            
                        conn.sendall(chunk)
                        cc.on_ack()
                        bytes_sent += len(chunk)
                        signals.update_graph.emit(cc.cwnd)
                        time.sleep(0.01)
                        
                        progress = bytes_sent / file_size * 100
                        signals.status_update.emit(
                            f"Sending {filename}: {progress:.1f}% "
                            f"(cwnd={cc.cwnd:.1f}, algo={cc.mode})"
                        )
    except Exception as e:
        signals.status_update.emit(f"Error: {str(e)}")
    finally:
        conn.close()
        signals.status_update.emit(f"Client disconnected: {addr}")

def start_server(signals):
    if not os.path.exists(FILE_DIR):
        os.makedirs(FILE_DIR)
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()
    signals.status_update.emit(f"Server listening on {HOST}:{PORT}")
    
    while True:
        conn, addr = s.accept()
        threading.Thread(
            target=handle_client, 
            args=(conn, addr, signals),
            daemon=True
        ).start()
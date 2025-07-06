from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                            QListWidget, QLabel, QMessageBox, QProgressBar)
import socket
import os

HOST = 'localhost'
PORT = 5000
CHUNK_SIZE = 1024
DOWNLOAD_DIR = 'downloads'

class ClientGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TCP Client - File Downloader")
        self.setGeometry(200, 200, 400, 400)
        self.layout = QVBoxLayout()
        
        self.label = QLabel("Available files from server:")
        self.layout.addWidget(self.label)
        
        self.file_list = QListWidget()
        self.layout.addWidget(self.file_list)
        
        self.progress = QProgressBar()
        self.layout.addWidget(self.progress)
        
        self.download_button = QPushButton("Download Selected File")
        self.download_button.clicked.connect(self.download_file)
        self.layout.addWidget(self.download_button)
        
        self.refresh_button = QPushButton("Refresh File List")
        self.refresh_button.clicked.connect(self.get_file_list)
        self.layout.addWidget(self.refresh_button)
        
        self.setLayout(self.layout)
        self.get_file_list()
        
        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)
    
    def get_file_list(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                s.sendall(b"LIST")
                data = s.recv(4096).decode()
                self.file_list.clear()
                self.file_list.addItems(data.strip().split("\n"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not connect to server: {str(e)}")
    
    def download_file(self):
        selected = self.file_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Warning", "Please select a file")
            return
            
        filename = selected.text()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                s.sendall(f"GET {filename}".encode())
                
                size_data = s.recv(1024).decode()
                if "ERROR" in size_data:
                    QMessageBox.critical(self, "Error", size_data)
                    return
                    
                file_size = int(size_data)
                self.progress.setMaximum(file_size)
                self.progress.setValue(0)
                
                s.sendall(b"READY")
                received = 0
                output_path = os.path.join(DOWNLOAD_DIR, filename)
                
                with open(output_path, "wb") as f:
                    while received < file_size:
                        data = s.recv(CHUNK_SIZE)
                        if not data:
                            break
                        f.write(data)
                        received += len(data)
                        self.progress.setValue(received)
                        QApplication.processEvents()
                
                QMessageBox.information(self, "Success", f"Downloaded: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        finally:
            self.progress.reset()

if __name__ == "__main__":
    app = QApplication([])
    win = ClientGUI()
    win.show()
    app.exec_()
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                            QPushButton, QTextEdit)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from server.server import start_server, ServerSignals
import threading

class ServerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TCP Server - Congestion Control Visualizer")
        self.setGeometry(100, 100, 800, 600)
        self.layout = QVBoxLayout()
        
        # Status display
        self.status_label = QLabel("Server Status: Not running")
        self.layout.addWidget(self.status_label)
        
        # Start/Stop button
        self.control_button = QPushButton("Start Server")
        self.control_button.clicked.connect(self.toggle_server)
        self.layout.addWidget(self.control_button)
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.layout.addWidget(self.log_display)
        
        # Graph
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.cwnd_data = []
        self.layout.addWidget(self.canvas)
        
        # Server signals
        self.signals = ServerSignals()
        self.signals.status_update.connect(self.update_status)
        self.signals.update_graph.connect(self.update_graph)
        
        self.server_thread = None
        self.running = False
        
        self.setLayout(self.layout)
        
    def toggle_server(self):
        if self.running:
            self.running = False
            self.control_button.setText("Start Server")
            self.status_label.setText("Server Status: Stopped")
        else:
            self.running = True
            self.control_button.setText("Stop Server")
            self.server_thread = threading.Thread(
                target=start_server,
                args=(self.signals,),
                daemon=True
            )
            self.server_thread.start()
    
    def update_status(self, message):
        self.log_display.append(message)
    
    def update_graph(self, cwnd_value):
        self.cwnd_data.append(cwnd_value)
        self.ax.clear()
        self.ax.set_title("Congestion Window (cwnd) Over Time")
        self.ax.set_xlabel("Packet Sequence")
        self.ax.set_ylabel("Window Size (packets)")
        self.ax.plot(self.cwnd_data, 'b-', marker='o')
        self.canvas.draw()

def start_server_gui():
    app = QApplication([])
    window = ServerGUI()
    window.show()
    app.exec_()

if __name__ == "__main__":
    start_server_gui()
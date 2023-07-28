import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton
from PyQt6.QtNetwork import QTcpServer, QHostAddress


class ServerApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.tcp_server = None
        self.setWindowTitle("ServerProcessor")
        self.setGeometry(100, 100, 300, 150)

        self.status_label = QLabel("H-engine not running", self)
        self.status_label.setGeometry(20, 20, 260, 30)

        self.start_button = QPushButton("Start", self)
        self.start_button.setGeometry(20, 60, 120, 40)
        self.start_button.clicked.connect(self.start_server)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.setGeometry(160, 60, 120, 40)
        self.stop_button.clicked.connect(self.stop_server)

        self.data_label = QLabel("Data:", self)
        self.data_label.setGeometry(20, 100, 260, 30)

    def start_server(self):
        if self.tcp_server is None:
            self.tcp_server = QTcpServer(self)
            self.tcp_server.newConnection.connect(self.on_new_connection)

            if self.tcp_server.listen(QHostAddress('127.0.0.1'), 1302):  # QHostAddress.Any
                self.status_label.setText("H-engine running - Listening for MSC ...")
            else:
                self.status_label.setText("Failed to start H-engine")
                self.tcp_server = None

    def stop_server(self):
        if self.tcp_server is not None:
            self.tcp_server.close()
            self.tcp_server = None
            self.status_label.setText("H-engine stopped")
        else:
            self.status_label.setText("H-engine is not running")

    def on_new_connection(self):
        client_socket = self.tcp_server.nextPendingConnection()
        self.status_label.setText("MSC connected: {0}:{1}".format(client_socket.peerAddress().toString(), client_socket.peerPort()))
        client_socket.disconnected.connect(self.on_client_disconnected)
        client_socket.readyRead.connect(lambda: self.on_ready_read(client_socket))

    def on_ready_read(self, client_socket):
        data = client_socket.readAll().data().decode()  # Read received data and convert to a string
        print(data)
        self.data_label.setText(f"Data: {data}")

    def on_client_disconnected(self):
        client_socket = self.sender()
        self.status_label.setText(
            "MSC disconnected: {0}:{1}".format(client_socket.peerAddress().toString(), client_socket.peerPort()))
        client_socket.deleteLater()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ServerApp()
    window.show()
    sys.exit(app.exec())

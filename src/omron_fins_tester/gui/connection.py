from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QGroupBox, QMessageBox, QComboBox)
from PyQt6.QtCore import pyqtSignal

class ConnectionPanel(QWidget):
    # Signals to communicate with the main app
    connect_requested = pyqtSignal(str, int, int, int, int, int, str) # IP, Port, DestNode, SrcNode, DestNet, SrcNet, Protocol
    disconnect_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        group_box = QGroupBox("Bağlantı Ayarları")
        group_layout = QHBoxLayout()
        group_box.setLayout(group_layout)

        # Protocol
        group_layout.addWidget(QLabel("Protokol:"))
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["UDP", "TCP"])
        self.protocol_combo.setFixedWidth(60)
        group_layout.addWidget(self.protocol_combo)

        # IP Address
        group_layout.addWidget(QLabel("IP:"))
        self.ip_input = QLineEdit("192.168.250.1")
        self.ip_input.setFixedWidth(100)
        group_layout.addWidget(self.ip_input)

        # Port
        group_layout.addWidget(QLabel("Port:"))
        self.port_input = QLineEdit("9600")
        self.port_input.setFixedWidth(50)
        group_layout.addWidget(self.port_input)

        # Dest Node
        group_layout.addWidget(QLabel("Dest Node:"))
        self.dest_node_input = QLineEdit("0")
        self.dest_node_input.setFixedWidth(30)
        group_layout.addWidget(self.dest_node_input)

        # Src Node
        group_layout.addWidget(QLabel("Src Node:"))
        self.src_node_input = QLineEdit("0")
        self.src_node_input.setFixedWidth(30)
        group_layout.addWidget(self.src_node_input)

        # Connect / Disconnect Buttons
        self.connect_btn = QPushButton("Bağlan")
        self.connect_btn.clicked.connect(self.on_connect_clicked)
        group_layout.addWidget(self.connect_btn)

        self.disconnect_btn = QPushButton("Bağlantıyı Kes")
        self.disconnect_btn.clicked.connect(self.on_disconnect_clicked)
        self.disconnect_btn.setEnabled(False)
        group_layout.addWidget(self.disconnect_btn)

        # Status Label
        self.status_label = QLabel("Durum: Bekleniyor")
        self.status_label.setStyleSheet("color: orange; font-weight: bold;")
        group_layout.addWidget(self.status_label)

        layout.addWidget(group_box)

    def on_connect_clicked(self):
        ip = self.ip_input.text().strip()
        port_str = self.port_input.text().strip()
        dn_str = self.dest_node_input.text().strip()
        sn_str = self.src_node_input.text().strip()
        protocol = self.protocol_combo.currentText()

        if not ip or not port_str.isdigit() or not dn_str.isdigit() or not sn_str.isdigit():
            QMessageBox.warning(self, "Hata", "Lütfen geçerli IP, Port ve Node değerleri girin.")
            return

        self.connect_requested.emit(ip, int(port_str), int(dn_str), int(sn_str), 0, 0, protocol)

    def on_disconnect_clicked(self):
        self.disconnect_requested.emit()

    def set_connected_state(self, is_connected: bool):
        self.protocol_combo.setEnabled(not is_connected)
        self.ip_input.setEnabled(not is_connected)
        self.port_input.setEnabled(not is_connected)
        self.dest_node_input.setEnabled(not is_connected)
        self.src_node_input.setEnabled(not is_connected)
        self.connect_btn.setEnabled(not is_connected)
        self.disconnect_btn.setEnabled(is_connected)

        if is_connected:
            self.status_label.setText("Durum: BAĞLI")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.status_label.setText("Durum: BAĞLANTI YOK")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")

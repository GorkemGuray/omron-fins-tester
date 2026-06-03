from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QLabel, 
                               QLineEdit, QPushButton, QGroupBox, QMessageBox, QComboBox)
from PyQt6.QtCore import pyqtSignal, Qt

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
        group_layout = QGridLayout()
        group_layout.setHorizontalSpacing(10)
        group_layout.setVerticalSpacing(10)
        group_box.setLayout(group_layout)

        # Protocol
        group_layout.addWidget(QLabel("Protokol:"), 0, 0)
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["UDP", "TCP"])
        self.protocol_combo.setFixedWidth(80)
        group_layout.addWidget(self.protocol_combo, 0, 1)

        # IP Address
        group_layout.addWidget(QLabel("IP:"), 0, 2)
        self.ip_input = QLineEdit("192.168.250.1")
        self.ip_input.setMinimumWidth(130)
        self.ip_input.setMaximumWidth(150)
        group_layout.addWidget(self.ip_input, 0, 3)

        # Port
        group_layout.addWidget(QLabel("Port:"), 0, 4)
        self.port_input = QLineEdit("9600")
        self.port_input.setFixedWidth(65)
        group_layout.addWidget(self.port_input, 0, 5)

        # Connect / Disconnect Buttons
        self.connect_btn = QPushButton("Bağlan")
        self.connect_btn.clicked.connect(self.on_connect_clicked)
        group_layout.addWidget(self.connect_btn, 0, 6)

        self.disconnect_btn = QPushButton("Bağlantıyı Kes")
        self.disconnect_btn.clicked.connect(self.on_disconnect_clicked)
        self.disconnect_btn.setEnabled(False)
        group_layout.addWidget(self.disconnect_btn, 0, 7)

        # Dest Node
        group_layout.addWidget(QLabel("Dest Node:"), 1, 0)
        self.dest_node_input = QLineEdit("0")
        self.dest_node_input.setFixedWidth(50)
        group_layout.addWidget(self.dest_node_input, 1, 1)

        # Src Node
        group_layout.addWidget(QLabel("Src Node:"), 1, 2)
        self.src_node_input = QLineEdit("0")
        self.src_node_input.setFixedWidth(50)
        group_layout.addWidget(self.src_node_input, 1, 3)

        # Status Label
        group_layout.addWidget(QLabel("Durum:"), 1, 4)
        self.status_label = QLabel("BEKLENİYOR")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(
            "background-color: #e65100; color: #ffe0b2; border: 1px solid #f57c00; "
            "border-radius: 4px; padding: 4px 8px; font-weight: bold;"
        )
        group_layout.addWidget(self.status_label, 1, 5, 1, 3)

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
            self.status_label.setText("BAĞLI")
            self.status_label.setStyleSheet(
                "background-color: #1b5e20; color: #c8e6c9; border: 1px solid #2e7d32; "
                "border-radius: 4px; padding: 4px 8px; font-weight: bold;"
            )
        else:
            self.status_label.setText("BAĞLANTI YOK")
            self.status_label.setStyleSheet(
                "background-color: #b71c1c; color: #ffcdd2; border: 1px solid #d32f2f; "
                "border-radius: 4px; padding: 4px 8px; font-weight: bold;"
            )

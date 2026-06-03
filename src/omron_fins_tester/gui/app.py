import sys
import time
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QMessageBox, QApplication
from omron_fins_tester.core.client import OmronFinsClient
from omron_fins_tester.gui.connection import ConnectionPanel
from omron_fins_tester.gui.variables import VariablesPanel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Omron FINS Tester")
        self.resize(950, 650)

        self.client = OmronFinsClient()

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Connection Panel
        self.conn_panel = ConnectionPanel()
        self.conn_panel.connect_requested.connect(self.handle_connect)
        self.conn_panel.disconnect_requested.connect(self.handle_disconnect)
        layout.addWidget(self.conn_panel)

        # Variables Panel
        self.var_panel = VariablesPanel()
        self.var_panel.read_requested.connect(self.handle_read)
        self.var_panel.write_requested.connect(self.handle_write)
        layout.addWidget(self.var_panel)

        # Disable vars panel initially
        self.var_panel.setEnabled(False)

    def handle_connect(self, ip: str, port: int, dest_node: int, src_node: int, dest_net: int, src_net: int, protocol: str):
        success, msg = self.client.connect(ip, port, dest_node, src_node, dest_net, src_net, protocol)
        if success:
            self.conn_panel.set_connected_state(True)
            self.var_panel.setEnabled(True)
            self.statusBar().showMessage(f"Bağlandı: {ip}:{port}")
        else:
            QMessageBox.critical(self, "Bağlantı Hatası", msg)

    def handle_disconnect(self):
        self.client.disconnect()
        self.conn_panel.set_connected_state(False)
        self.var_panel.stop_auto_read()
        self.var_panel.setEnabled(False)
        self.statusBar().showMessage("Bağlantı kesildi.")

    def handle_read(self, row: int, area: str, address_str: str, dtype: str, silent: bool = False):
        start_time = time.time()
        success, result, msg = self.client.read_variable(area, address_str, dtype)
        latency = (time.time() - start_time) * 1000

        if success:
            # If result is a list and has 1 element, extract it
            if isinstance(result, list) and len(result) == 1:
                val = result[0]
            else:
                val = result
            
            self.var_panel.update_value(row, val)
            self.statusBar().showMessage(f"Okuma başarılı ({latency:.1f} ms) - Alan: {area}{address_str}")
        else:
            if not silent:
                QMessageBox.warning(self, "Okuma Hatası", f"Okuma işlemi başarısız: {msg}")
            else:
                self.statusBar().showMessage(f"Okuma Hatası: {msg}")

    def handle_write(self, row: int, area: str, address_str: str, dtype: str, parsed_val: object):
        start_time = time.time()
        success, msg = self.client.write_variable(parsed_val, area, address_str, dtype)
        latency = (time.time() - start_time) * 1000

        if success:
            self.statusBar().showMessage(f"Yazma başarılı ({latency:.1f} ms) - Alan: {area}{address_str}")
            # Automatically read back to verify
            self.handle_read(row, area, address_str, dtype)
        else:
            QMessageBox.warning(self, "Yazma Hatası", f"Yazma işlemi başarısız: {msg}")

def run_app():
    import os
    app = QApplication(sys.argv)
    
    style_path = os.path.join(os.path.dirname(__file__), 'style.qss')
    if os.path.exists(style_path):
        with open(style_path, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())
            
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

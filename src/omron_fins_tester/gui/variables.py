from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QComboBox, QMessageBox, QAbstractItemView, QCheckBox)
from PyQt6.QtCore import pyqtSignal, QTimer, Qt
import struct
import ast

class VariablesPanel(QWidget):
    # Signals emitted when read or write is clicked
    read_requested = pyqtSignal(int, str, str, str, bool)  # row, memory_area, address_str, data_type, is_silent
    write_requested = pyqtSignal(int, str, str, str, object) # row, memory_area, address_str, data_type, parsed_value

    def __init__(self):
        super().__init__()
        self.init_ui()

        # Timer for polling
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self.on_poll_timeout)

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Add Variable Form
        form_layout = QHBoxLayout()
        
        self.area_combo = QComboBox()
        self.area_combo.addItems(["D", "W", "C", "H"])
        self.area_combo.setFixedWidth(60)
        form_layout.addWidget(QLabel("Alan:"))
        form_layout.addWidget(self.area_combo)

        self.address_input = QLineEdit("100")
        self.address_input.setPlaceholderText("Adres (Örn: 100)")
        self.address_input.setMinimumWidth(100)
        self.address_input.setMaximumWidth(140)
        form_layout.addWidget(QLabel("Adres:"))
        form_layout.addWidget(self.address_input)

        self.type_mapping = {
            "BOOL (Bit)": "b",
            "WORD (16-bit Hex)": "w",
            "DWORD (32-bit Hex)": "dw",
            "INT (16-bit Signed)": "i",
            "DINT (32-bit Signed)": "d",
            "REAL (32-bit Float)": "r",
            "LREAL (64-bit Float)": "l",
            "UINT (16-bit Unsigned)": "ui",
            "UDINT (32-bit Unsigned)": "udi"
        }

        self.type_combo = QComboBox()
        self.type_combo.addItems(list(self.type_mapping.keys()))
        self.type_combo.setMinimumWidth(180)
        self.type_combo.setMaximumWidth(220)
        form_layout.addWidget(QLabel("Tip:"))
        form_layout.addWidget(self.type_combo)

        add_btn = QPushButton("Değişken Ekle")
        add_btn.clicked.connect(self.on_add_clicked)
        form_layout.addWidget(add_btn)
        form_layout.addStretch()

        layout.addLayout(form_layout)

        # Polling Form
        poll_layout = QHBoxLayout()
        self.auto_read_cb = QCheckBox("Otomatik Okuma")
        self.auto_read_cb.stateChanged.connect(self.on_auto_read_toggled)
        poll_layout.addWidget(self.auto_read_cb)

        poll_layout.addWidget(QLabel("Periyot (ms):"))
        self.period_input = QLineEdit("1000")
        self.period_input.setFixedWidth(70)
        poll_layout.addWidget(self.period_input)
        poll_layout.addStretch()

        layout.addLayout(poll_layout)

        # Table
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(["Alan", "Adres", "Tip", "Format", "Okunan", "Değiştir", "Oku", "Sil"])
        
        # Configure default row height to prevent clipping of padded cell widgets
        self.table.verticalHeader().setDefaultSectionSize(36)
        
        # Configure specific column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents) # Alan
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)          # Adres
        
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)            # Tip
        self.table.setColumnWidth(2, 155)
        
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)            # Format
        self.table.setColumnWidth(3, 105)
        
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)          # Okunan
        
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)      # Değiştir
        self.table.setColumnWidth(5, 140)
        
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)            # Oku
        self.table.setColumnWidth(6, 80)
        
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)            # Sil
        self.table.setColumnWidth(7, 80)
        
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

    def on_add_clicked(self):
        area = self.area_combo.currentText()
        address_str = self.address_input.text().strip().upper()
        dtype = self.type_combo.currentText()

        # Remove common prefixes like %, D, W, C, H
        clean_addr = address_str.replace('%', '').replace('D', '').replace('W', '').replace('C', '').replace('H', '')
        
        if not clean_addr.replace('.', '').isdigit():
            QMessageBox.warning(self, "Hata", "Adres sadece sayısal bir değer olmalıdır (Örn: 100 veya 100.05).")
            return

        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, 0, QTableWidgetItem(area))
        self.table.setItem(row, 1, QTableWidgetItem(clean_addr))
        self.table.setItem(row, 2, QTableWidgetItem(dtype))
        
        format_combo = QComboBox()
        format_combo.addItems(["Decimal", "Hex", "Binary"])
        self.table.setCellWidget(row, 3, format_combo)

        read_label = QLabel("-")
        read_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setCellWidget(row, 4, read_label)

        dtype = self.type_mapping.get(dtype, "w")
        
        if dtype == 'b':
            # Bool type: TRUE/FALSE buttons
            format_combo.setEnabled(False)
            
            modify_widget = QWidget()
            modify_widget.setMinimumWidth(125)
            h_layout = QHBoxLayout(modify_widget)
            h_layout.setContentsMargins(2, 2, 2, 2)
            h_layout.setSpacing(2)
            
            btn_true = QPushButton("TRUE")
            btn_true.setStyleSheet(
                "QPushButton { background-color: #252526; color: #4caf50; border: 1px solid #3c3c3c; border-radius: 3px; font-weight: bold; padding: 2px; }"
                "QPushButton:hover { background-color: #2e7d32; color: white; }"
                "QPushButton:pressed { background-color: #1b5e20; }"
            )
            btn_true.clicked.connect(lambda _, mw=modify_widget: self._emit_bool_write(mw, 1))
            
            btn_false = QPushButton("FALSE")
            btn_false.setStyleSheet(
                "QPushButton { background-color: #252526; color: #f44336; border: 1px solid #3c3c3c; border-radius: 3px; font-weight: bold; padding: 2px; }"
                "QPushButton:hover { background-color: #c62828; color: white; }"
                "QPushButton:pressed { background-color: #b71c1c; }"
            )
            btn_false.clicked.connect(lambda _, mw=modify_widget: self._emit_bool_write(mw, 0))
            
            h_layout.addWidget(btn_true)
            h_layout.addWidget(btn_false)
            self.table.setCellWidget(row, 5, modify_widget)
        else:
            # Numeric type: QLineEdit with Enter support
            write_input = QLineEdit()
            write_input.returnPressed.connect(lambda w=write_input: self._on_enter_pressed(w))
            self.table.setCellWidget(row, 5, write_input)

        read_btn = QPushButton("Oku")
        read_btn.clicked.connect(lambda _, r=row: self.on_read_clicked(self.get_row_index(read_btn)))
        self.table.setCellWidget(row, 6, read_btn)

        delete_btn = QPushButton("Sil")
        delete_btn.clicked.connect(lambda _, r=row: self.on_delete_clicked(self.get_row_index(delete_btn)))
        self.table.setCellWidget(row, 7, delete_btn)

    def on_auto_read_toggled(self, state):
        if self.auto_read_cb.isChecked():
            period_str = self.period_input.text().strip()
            if not period_str.isdigit() or int(period_str) < 100:
                QMessageBox.warning(self, "Hata", "Lütfen 100'den büyük geçerli bir periyot (ms) girin.")
                self.auto_read_cb.setChecked(False)
                return
            
            period_ms = int(period_str)
            self.period_input.setEnabled(False)
            self.poll_timer.start(period_ms)
        else:
            self.poll_timer.stop()
            self.period_input.setEnabled(True)

    def stop_auto_read(self):
        self.auto_read_cb.setChecked(False)
        self.poll_timer.stop()
        self.period_input.setEnabled(True)

    def on_poll_timeout(self):
        for row in range(self.table.rowCount()):
            self.on_read_clicked(row, silent=True)

    def get_row_index(self, widget: QWidget) -> int:
        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()):
                if self.table.cellWidget(i, j) == widget:
                    return i
        return -1

    def _emit_bool_write(self, widget: QWidget, val: int):
        row = self.get_row_index(widget)
        if row < 0: return
        area = self.table.item(row, 0).text()
        address_str = self.table.item(row, 1).text()
        dtype_desc = self.table.item(row, 2).text()
        dtype = self.type_mapping.get(dtype_desc, "w")
        self.write_requested.emit(row, area, address_str, dtype, val)

    def _on_enter_pressed(self, widget: QLineEdit):
        row = self.get_row_index(widget)
        if row < 0: return
        self.on_write_clicked(row)

    def on_read_clicked(self, row: int, silent: bool = False):
        if row < 0: return
        area = self.table.item(row, 0).text()
        address_str = self.table.item(row, 1).text()
        dtype_desc = self.table.item(row, 2).text()
        dtype = self.type_mapping.get(dtype_desc, "w")
        
        self.read_requested.emit(row, area, address_str, dtype, silent)

    def on_write_clicked(self, row: int):
        if row < 0: return
        area = self.table.item(row, 0).text()
        address_str = self.table.item(row, 1).text()
        dtype_desc = self.table.item(row, 2).text()
        dtype = self.type_mapping.get(dtype_desc, "w")
        
        format_combo = self.table.cellWidget(row, 3)
        fmt = format_combo.currentText()
        
        value_widget = self.table.cellWidget(row, 5)
        if isinstance(value_widget, QLineEdit):
            val_str = value_widget.text().strip()
            if not val_str:
                QMessageBox.warning(self, "Hata", "Yazılacak değeri girin.")
                return
            
            try:
                if fmt == "Hex":
                    parsed_val = int(val_str, 16)
                elif fmt == "Binary":
                    parsed_val = int(val_str, 2)
                else:
                    if dtype in ['r', 'l']:
                        parsed_val = float(val_str)
                    else:
                        parsed_val = int(val_str)
            except ValueError:
                QMessageBox.warning(self, "Tür Hatası", f"Girdiğiniz değer '{fmt}' formatına uygun değil.")
                return
                
            self.write_requested.emit(row, area, address_str, dtype, parsed_val)

    def on_delete_clicked(self, row: int):
        if row >= 0:
            self.table.removeRow(row)

    def update_value(self, row: int, value):
        if row >= 0 and row < self.table.rowCount():
            dtype_desc = self.table.item(row, 2).text()
            dtype = self.type_mapping.get(dtype_desc, "w")
            
            value_widget = self.table.cellWidget(row, 4)
            if isinstance(value_widget, QLabel):
                if dtype == 'b':
                    value_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    if value == 1:
                        value_widget.setText("TRUE")
                        value_widget.setStyleSheet(
                            "background-color: #1b5e20; color: #c8e6c9; border: 1px solid #2e7d32; "
                            "border-radius: 4px; padding: 2px 6px; font-weight: bold;"
                        )
                    else:
                        value_widget.setText("FALSE")
                        value_widget.setStyleSheet(
                            "background-color: #b71c1c; color: #ffcdd2; border: 1px solid #d32f2f; "
                            "border-radius: 4px; padding: 2px 6px; font-weight: bold;"
                        )
                else:
                    value_widget.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                    format_combo = self.table.cellWidget(row, 3)
                    fmt = format_combo.currentText()
                    formatted_str = self._format_value(value, fmt, dtype)
                    value_widget.setText(formatted_str)
                    value_widget.setStyleSheet("") # reset style

    def _format_value(self, val, fmt: str, dtype: str) -> str:
        num = val
        if isinstance(val, list) and len(val) > 0:
            val = val[0]
            
        if isinstance(val, bytes):
            if dtype == 'r':
                try:
                    num = struct.unpack('>f', val)[0]
                except Exception:
                    num = 0.0
            elif dtype == 'l':
                try:
                    num = struct.unpack('>d', val)[0]
                except Exception:
                    num = 0.0
            else:
                num = int.from_bytes(val, byteorder='big', signed=(dtype in ['i', 'd']))
        elif isinstance(val, str):
            if val.startswith(r'\x'):
                try:
                    b = ast.literal_eval(f"b'{val}'")
                    num = int.from_bytes(b, byteorder='big', signed=(dtype in ['i', 'd']))
                except Exception:
                    num = 0
            else:
                try:
                    num = float(val) if dtype in ['r', 'l'] else int(val)
                except ValueError:
                    return str(val)
        else:
            num = val

        if isinstance(num, float):
            return f"{num:.4f}"
            
        if not isinstance(num, int):
            return str(val)
            
        if fmt == "Hex":
            return hex(num).upper().replace('0X', '0x')
        elif fmt == "Binary":
            return bin(num)
        else:
            return str(num)

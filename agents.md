# Agent Guidelines for Omron FINS Tester

Welcome! If you are an AI assistant or a human developer contributing to this project, please follow the guidelines established below.

## 1. Project Philosophy & UI Design
- **Industrial Look & Feel**: The UI is designed to feel like professional industrial software (e.g., Omron Sysmac Studio, TIA Portal, or VS Code). 
- **Dark Mode**: All styling should respect the dark mode palette defined in `src/omron_fins_tester/gui/style.qss`. If adding new widgets, ensure they blend well with `#1e1e1e` backgrounds and `#e0e0e0` text.
- **Minimalism & Ergonomics**: We removed unnecessary UI clutter (like the "Write" button in favor of the `Enter` key for text fields and `TRUE/FALSE` buttons for Booleans). Maintain this UX paradigm when adding new features.

## 2. Architecture Patterns
- **PyQt6 Event Loop**: All UI interactions run via PyQt6. Do not implement blocking operations in the UI thread. Use `QTimer` for polling (`variables.py`), not `time.sleep()`.
- **Signal & Slot Separation**: The GUI components (`variables.py`, `connection.py`) should NOT directly import or call the FINS client. They emit Signals (`read_requested`, `write_requested`, `connect_requested`), which are connected to slots inside `MainWindow` (`app.py`). `app.py` acts as the Controller orchestrating the UI and the Client layer.
- **Client Wrapper**: `core/client.py` isolates the `fins` Python package. Always manage PLC data type conversions and End Code checking within the `client.py` wrapper.

## 3. Omron FINS Specifics (Important Quicks)
- **Node Routing is Crucial**: Omron PLCs frequently reject commands with `timeout` or routing errors if `dest_node` and `src_node` are not provided correctly.
- **Normal Completion End Codes**: While `00 00` is the standard Normal Completion End Code, some Omron memory areas or Boolean reads will return `00 40` (or other sub-codes starting with `00`). Always check for success using `end_code.startswith(b'\x00')` rather than an exact match to `b'\x00\x00'`.
- **Memory Area Codes**: 
  - Word reading: `D` (0x82), `W` (0xB1), `H` (0xB2), `C` (0xB0).
  - Bit reading: `D` (0x02), `W` (0x31), `H` (0x32), `C` (0x30).
  Always split addresses (e.g., `300.05` -> word `300`, bit `5`) and apply the correct specific FINS Area ID.

## 4. Error Handling
- Never allow an error to crash the app. The UI is built to handle connection drops gracefully.
- Handle Exceptions from Python's `struct.unpack` and `int.from_bytes` cleanly during parsing and format them as UI warnings (`QMessageBox`).

Thank you for helping improve the Omron FINS Tester!

# Virtual RAW TCP/IP Printer Server v2

A high-productivity desktop GUI emulator featuring **4 concurrent RAW TCP/IP socket listeners** in a 2x2 split-screen layout with real-time **document auto-detection**, **PDF reader integration**, **hex dump inspection**, and **file export**.

Designed for testing multi-printer routing, warehouse dispatching, POS networks, and document generation workflows.

---

## 🚀 Key Features

1. **Multi-Printer Split Screen (2x2 Grid)**:
   - Run up to **4 independent TCP/IP socket listeners simultaneously**.
   - Custom configurations per pane: **Host/IP** (default `0.0.0.0` / `127.0.0.1`), **Port** (default `9100`, `9101`, `9102`, `9103`), and **Label**.
   - Global Master Controls: `▶ Start All Printers`, `⏹ Stop All`, and `🧹 Clear All Logs`.
   - Independent pane start/stop toggles with automatic input locking when listening.

2. **Smart Document Preview & Detection**:
   - **PDF Stream Detection (`%PDF-`)**: Automatically saves the payload stream to a temporary PDF and enables the **`👁️ Open PDF`** button to open the document directly in your OS default viewer (Edge, Chrome, Adobe Reader).
   - **HTML Document Detection**: Identifies HTML/XML print payloads.
   - **RAW / ESC Codes**: Displays raw string and byte stream output.

3. **3 Document Inspection Modes**:
   - 📝 **Formatted View**: Job headers (Timestamp, Client IP, Size, Type) + extracted text snippets.
   - 🔤 **Raw Text View**: Full text view with UTF-8 / Latin1 fallback decoding.
   - 🔢 **Hex Dump View**: Byte-level offset and ASCII representation (16 bytes/line) for protocol inspection.

4. **File Export**:
   - **`💾 Save File`** button to export received payloads to `.pdf`, `.txt`, or `.raw` format.

5. **Zero External Dependencies**:
   - Powered 100% by Python 3 standard library (`tkinter`, `socket`, `threading`, `tempfile`). No `pip install` required.

---

## 💻 Quick Start

### Prerequisites
- Python 3.8+ installed (with Tkinter support).

### Running the Application

**Option 1: Windows Double-Click Launcher**
Double-click `run.bat`.

**Option 2: Terminal / Command Line**
```bash
python app.py
```

---

## ⚙️ Testing Multi-Printer Dispatching

1. Start all printers using **`▶ Start All Printers`** (or configure custom ports like `9100`, `9101`, `9102`, `9103`).
2. Dispatch print payloads to specific ports:

### Example: Testing from Python

```python
import socket

def send_print_job(host, port, payload_bytes):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(payload_bytes)

# Send Text Job to Printer 1 (Port 9100)
send_print_job("127.0.0.1", 9100, b"RECEIPT #1001\nItem: Coffee\nPrice: $4.50\n")

# Send PDF Job to Printer 2 (Port 9101)
with open("sample_invoice.pdf", "rb") as f:
    pdf_bytes = f.read()
    send_print_job("127.0.0.1", 9101, pdf_bytes)
```

---

## 📂 Project Structure

```text
├── app.py           # Main GUI application script
├── run.bat          # Windows double-click launcher
├── requirements.txt # Dependency specifications (Python standard library)
├── .gitignore       # Git ignore rules
└── README.md        # Public documentation
```

---

## 📄 License
MIT License. Free to use for personal and commercial development/testing.

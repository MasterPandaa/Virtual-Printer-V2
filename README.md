# Virtual Printer V2 — Multi-Port RAW TCP/IP Printer Emulator & Inspector

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat&logo=python&logoColor=white)](#)
[![Architecture](https://img.shields.io/badge/Architecture-2x2%20Split%20Grid%20(4%20Ports)-9cf.svg)](#)
[![Formats Supported](https://img.shields.io/badge/Payloads-PDF%20%7C%20HTML%20%7C%20ESC%2FPOS%20%7C%20RAW-purple.svg)](#)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Standard%20Library%20Only-orange.svg)](#)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An advanced desktop TCP/IP network printer emulator featuring **4 concurrent RAW socket listeners** arranged in a 2x2 split-screen grid.

Virtual Printer V2 is built for QA engineers, POS developers, and systems integrators testing multi-destination print routing (e.g., Cashier `9100`, Kitchen `9101`, Bar `9102`, Dispatch `9103`) without physical printer hardware. It incorporates automatic format classification (PDF, HTML, ESC/POS, RAW), integrated PDF document viewing, low-level Hex Dump inspection, and payload file export.

---

## Overview

Complex POS and ERP systems frequently route distinct document types to different physical print endpoints simultaneously. Testing such systems requires running multiple socket listeners and inspecting payload integrity:

- **Concurrent Multi-Port Simulation**: Runs up to 4 independent multithreaded TCP socket servers concurrently in a single window.
- **Binary Magic Number Detection**: Identifies `%PDF-` binary headers and provides a one-click launcher to open incoming documents in the system's default PDF reader.
- **Low-Level Protocol Hex Dump**: Inspects raw byte streams with 16-byte offset headers and ASCII representations for protocol debugging and command sequence verification.
- **One-Click Payload Export**: Saves received socket buffers to disk (`.pdf`, `.txt`, `.raw`) for test artifact recording.
- **Zero External Dependencies**: Implemented strictly with Python's built-in standard library (`socket`, `threading`, `tkinter`).

---

## Technical Features

1. **2x2 Multi-Printer Grid**:
   - 4 independent socket panels with individual IP, port, and printer label configurations.
   - Master controls: Start All, Stop All, and Clear All.
   - Independent per-panel start/stop switches.
2. **Payload Auto-Detection**:
   - **PDF Stream (`%PDF-`)**: Automatically saves stream to a temporary file and triggers the native OS viewer.
   - **HTML/XML Stream**: Identifies web markup and formatted documents.
   - **RAW / ESC/POS Stream**: Identifies terminal control codes, carriage returns, and receipt cuts.
3. **Tri-Mode Stream Inspection**:
   - **Formatted View**: Metadata header (timestamp, client IP/port, payload size, type) with text summary.
   - **Raw Text View**: Full UTF-8 and Latin-1 fallback string representation.
   - **Hex Dump View**: 16-byte hex offset view for byte-level protocol analysis.
4. **Multithreaded Isolation**: Each socket listener runs in a dedicated background worker thread, ensuring heavy socket transmissions do not freeze the UI.

---

## Quickstart

### Prerequisites

- Python 3.8+ with `tkinter` support.
- *On Linux (Debian/Ubuntu)*: `sudo apt install python3-tk`

### Installation & Run

1. **Clone the repository**:
   ```bash
   git clone https://github.com/MasterPandaa/Virtual-Printer-V2.git
   cd Virtual-Printer-V2
   ```

2. **Launch the emulator**:
   ```bash
   python app.py
   ```
   *(On Windows, you can double-click `run.bat`)*

3. **Multi-Port Test Script (PowerShell)**:
   ```powershell
   # Send test prints to Port 9100 and Port 9101 simultaneously
   9100..9101 | ForEach-Object {
       $client = New-Object System.Net.Sockets.TcpClient("127.0.0.1", $_)
       $stream = $client.GetStream()
       $writer = New-Object System.IO.StreamWriter($stream)
       $writer.WriteLine("Test print sent to port $_")
       $writer.Flush()
       $client.Close()
   }
   ```

---

## Project Structure

```text
Virtual-Printer-V2/
├── app.py                      # Multi-panel Tkinter GUI and concurrent socket engine
├── run.bat                     # Windows batch launcher
├── README.md                   # Project documentation
└── LICENSE                     # MIT License
```

---

## License

This project is licensed under the [MIT License](LICENSE).

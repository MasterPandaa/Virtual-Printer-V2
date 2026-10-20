<p align="center">
  <img src="https://raw.githubusercontent.com/MasterPandaa/MasterPandaa/main/assets/banners/Virtual-Printer-V2.svg" alt="Virtual Printer V2 Banner" width="100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Networking-Concurrent_4--Port_Hub-0891B2?style=flat-square" alt="4-Port Hub">
  <img src="https://img.shields.io/badge/Ports-9100_%7C_9101_%7C_9102_%7C_9103-3B82F6?style=flat-square" alt="Ports">
  <img src="https://img.shields.io/badge/Inspection-Hex_Dump_|_PDF_Export-10B981?style=flat-square" alt="Hex Dump">
  <img src="https://img.shields.io/badge/Language-Python_3-3776AB?style=flat-square&logo=python" alt="Python">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-gray?style=flat-square" alt="License"></a>
</p>

## Overview

Commercial restaurant and retail environments split printing jobs across multiple physical stations simultaneously: cashier receipts on port 9100, bar drink chits on port 9101, hot kitchen orders on port 9102, and cold prep orders on port 9103.

Virtual-Printer-V2 is a multi-threaded RAW TCP/IP network printer emulator that listens concurrently on **4 independent socket ports (9100–9103)**. The application captures simultaneous POS print queues, provides deep **Hex Dump** byte analysis for binary ESC/POS sequences, and parses incoming streams into searchable PDF documents.

---

## Architecture Flow

```text
POS System / Restaurant Dispatcher
   │
   ├── Port 9100: Cashier Register   ──► Thread 1 (Socket Listener 9100)
   ├── Port 9101: Bar Drink Chits    ──► Thread 2 (Socket Listener 9101)
   ├── Port 9102: Kitchen Order Line ──► Thread 3 (Socket Listener 9102)
   └── Port 9103: Prep Station       ──► Thread 4 (Socket Listener 9103)
                                              │
                                              ▼
                                 Multi-Threaded Ingestion Hub
                                 (Hex Dump Analyzer & PDF Parser)
                                              │
                                              ▼
                             Unified Multi-Channel Desktop GUI
```

---

## Core Capabilities

- **Concurrent 4-Port Server**: Runs 4 independent socket listening threads simultaneously across ports 9100, 9101, 9102, and 9103.
- **Deep Hex Dump Inspection**: Visualizes binary byte streams alongside ASCII representations, essential for debugging ESC/POS command sequences.
- **Automated PDF Parsing**: Converts text and document streams into cleanly formatted, archived PDF files.
- **Per-Port Status Telemetry**: Independent connection counters, traffic gauges, and status indicators for each listening socket.
- **Traffic Isolation**: Logs and displays print streams per channel without cross-port queue contamination.

---

## Quickstart

```bash
git clone https://github.com/MasterPandaa/Virtual-Printer-V2.git
cd Virtual-Printer-V2
pip install -r requirements.txt
python main.py
```

---

## License

This project is licensed under the [MIT License](LICENSE).

# 🖨️ Virtual Printer V2 - Multi-Port RAW TCP/IP Printer Emulator & Protocol Inspector

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat&logo=python&logoColor=white)](#)
[![Architecture](https://img.shields.io/badge/Architecture-2x2%20Split%20Grid%20(4%20Ports)-9cf.svg)](#)
[![Formats Supported](https://img.shields.io/badge/Payloads-PDF%20%7C%20HTML%20%7C%20ESC%2FPOS%20%7C%20RAW-purple.svg)](#)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Standard%20Library%20Only-orange.svg)](#)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Virtual Printer V2** adalah emulator server printer jaringan generasi kedua dengan kapabilitas **4 concurrent RAW TCP/IP socket listeners** dalam antarmuka *split-screen grid (2x2)*. Dilengkapi fitur **deteksi format cerdas (PDF/HTML/RAW)**, **integrasi pembuka PDF instan**, **mode inspeksi Hex Dump**, dan **fitur ekspor payload**.

Sangat ideal untuk pengujian arsitektur *multi-printer routing*, sistem logistik pergudangan (*warehouse multi-station*), sistem F&B POS (Dapur, Bar, Kasir, Checker), dan validasi integrasi *document stream*.

---

## 🌟 Mengapa Menggunakan Virtual Printer V2?

- 🎛️ **Simulasi 4 Printer Sekaligus**: Menguji skenario pengiriman ke banyak printer berbeda (misal: Kasir `9100`, Bar `9101`, Dapur `9102`, Gudang `9103`) dalam 1 jendela aplikasi.
- 📄 **Smart PDF Detection & Viewer**: Mengenali *header binary* `%PDF-` secara otomatis dan menyajikan tombol **`👁️ Open PDF`** untuk membuka dokumen langsung di PDF viewer default sistem operasi.
- 🔍 **Inspeksi Protokol Tingkat Lanjut (Hex Dump)**: Analisis byte stream secara presisi baris-per-baris (16 byte offset + representasi ASCII) untuk validasi protokol atau *debugging command escape*.
- 💾 **Ekspor Payload Satu-Klik**: Menyimpan *payload* yang diterima ke dalam format `.pdf`, `.txt`, atau `.raw` untuk dokumentasi QA.
- ⚡ **Zero External Dependencies**: Dibangun murni dengan modul standar Python 3 bawaan (*tanpa instalasi pihak ketiga*).

---

## 🚀 Fitur Utama

1. **Multi-Printer Split Screen (2x2 Grid Layout)**:
   - Menjalankan hingga **4 socket listener TCP/IP independen** secara bersamaan.
   - Konfigurasi mandiri per panel: **Host/IP**, **Port** (default `9100`, `9101`, `9102`, `9103`), dan **Label Printer**.
   - Kontrol Master Global: `▶ Start All Printers`, `⏹ Stop All`, dan `🧹 Clear All Logs`.
   - Toggle saklar independen per panel dengan fitur penguncian input otomatis saat server aktif.

2. **Smart Payload Auto-Detection**:
   - **PDF Stream (`%PDF-`)**: Deteksi *magic number* PDF otomatis dan pembacaan via default OS viewer.
   - **HTML/XML Stream**: Deteksi *tag markup* dokumen berbasis web.
   - **RAW / ESC/POS Stream**: Deteksi karakter kendali dan teks struk standar.

3. **3 Mode Inspeksi Dokumen Terintegrasi**:
   - 📝 **Formatted View**: Metadata pekerjaan cetak (Timestamp, IP Klien, Ukuran Data, Tipe Dokumen) + ekstrak cuplikan teks.
   - 🔤 **Raw Text View**: Visualisasi teks penuh dengan mekanisme decoding adaptif `UTF-8` / `Latin-1`.
   - 🔢 **Hex Dump View**: Inspeksi heksadesimal tingkat rendah per 16 byte dengan representasi ASCII untuk kebutuhan *reverse engineering* protokol.

4. **Payload Exporter**:
   - Tombol **`💾 Save File`** untuk menyimpan payload secara instan ke file fisik komputer Anda.

5. **Multi-Threaded & Non-Blocking**:
   - Setiap panel berjalan pada thread terpisah sehingga lalu lintas socket berkecepatan tinggi tidak membuat antarmuka membeku (*freeze*).

---

## 🛠️ Tata Cara Instalasi

### 1. Prasyarat Sistem
- **Python 3.8+** (dengan Tkinter).

### 2. Download / Clone Repository
```bash
git clone https://github.com/MasterPandaa/Virtual-Printer-V2.git
cd Virtual-Printer-V2
```

---

### 3. Menjalankan Aplikasi

#### 🪟 Windows
- **Cara Cepat**: Klik ganda file `run.bat`.
- **Melalui Terminal**:
  ```powershell
  python app.py
  ```

#### 🐧 Linux (Ubuntu / Debian / Arch / Fedora)
```bash
# Pastikan python3-tk tersedia
sudo apt install python3-tk  # Debian/Ubuntu

python3 app.py
```

#### 🍎 macOS
```bash
python3 app.py
```

---

## 📖 Panduan Penggunaan

```text
┌─────────────────────────────────────────────────────────────────┐
│                    VIRTUAL PRINTER V2 (2x2 GRID)                │
├────────────────────────────────┬────────────────────────────────┤
│ [Panel 1] Kasir (Port 9100)    │ [Panel 2] Bar (Port 9101)      │
│ Status: LISTENING              │ Status: LISTENING              │
├────────────────────────────────┼────────────────────────────────┤
│ [Panel 3] Dapur (Port 9102)    │ [Panel 4] Gudang (Port 9103)   │
│ Status: LISTENING              │ Status: LISTENING              │
└────────────────────────────────┴────────────────────────────────┘
```

1. **Atur Port & Nama Label**: Ubah nama label pada masing-masing dari ke-4 panel sesuai kebutuhan stasiun cetak Anda.
2. **Jalankan Server**:
   - Klik **`▶ Start All Printers`** di header atas untuk mengaktifkan seluruh panel sekaligus.
   - Atau klik **`Start`** pada panel individu yang ingin diuji secara spesifik.
3. **Kirim Data Cetak**: Arahkan aplikasi pengirim ke port panel yang bersangkutan (`9100`, `9101`, `9102`, atau `9103`).
4. **Inspeksi Hasil**:
   - Jika payload adalah **PDF**, klik tombol **`👁️ Open PDF`** untuk memvalidasi layout dokumen.
   - Ganti tab inspeksi (**Formatted**, **Raw Text**, atau **Hex Dump**) untuk memeriksa konten.
   - Simpan data dengan mengklik **`💾 Save File`**.
5. **Reset Log**: Klik **`🧹 Clear All Logs`** untuk mengosongkan riwayat antrean pengujian.

---

## 🧪 Uji Mandiri & Testing Suite

Berikut *script* pengujian Python untuk mensimulasikan skenario pengiriman ke beberapa printer sekaligus (*Multi-Station Dispatching*):

```python
import socket

def send_print_job(host: str, port: int, payload_bytes: bytes, label: str):
    print(f"📡 Mengirim ke [{label}] ({host}:{port})...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        sock.sendall(payload_bytes)
    print(f"✅ Sukses terkirim ke [{label}]")

HOST = "127.0.0.1"

# 1. Kirim Struk Kasir (Port 9100)
cashier_payload = (
    "=== STRUK KASIR ===\n"
    "No: #00192 | Kasir: Admin\n"
    "1x Americano      Rp 28.000\n"
    "1x Croissant      Rp 32.000\n"
    "Total             Rp 60.000\n"
    "===================\n"
).encode("utf-8")
send_print_job(HOST, 9100, cashier_payload, "KASIR")

# 2. Kirim Pesanan Dapur (Port 9102)
kitchen_payload = (
    "*** ORDER TIKET DAPUR ***\n"
    "Meja: 08 | Waktu: 14:30\n"
    "- 1x Croissant (Hangatkan)\n"
    "*************************\n"
).encode("utf-8")
send_print_job(HOST, 9102, kitchen_payload, "DAPUR")

# 3. Kirim File PDF (Port 9101)
try:
    with open("sample_invoice.pdf", "rb") as f:
        send_print_job(HOST, 9101, f.read(), "PDF_PRINT")
except FileNotFoundError:
    print("ℹ️ Lewati pengiriman file PDF (sample_invoice.pdf tidak ditemukan)")
```

---

## 📦 Struktur Project

```text
Virtual-Printer-V2/
├── app.py              # Engine multi-listener 4-port, parser payload & GUI 2x2
├── run.bat             # Launcher instan satu-klik untuk Windows
├── requirements.txt    # Spesifikasi dependensi (Standard Library)
├── .gitignore          # Konfigurasi pengabaian file Git
├── LICENSE             # Dokumen lisensi open-source MIT
└── README.md           # Dokumentasi komprehensif proyek
```

---

## 🔒 Privasi & Keamanan

- **Zero External Telemetry**: 100% beroperasi secara lokal (*air-gapped compatible*).
- **Ephemeral PDF Storage**: File sementara yang dibuat untuk pratinjau PDF disimpan di direktori *temp* sistem operasi dan terisolasi secara aman.
- **Port Isolation**: Setiap thread socket dikelola secara independen tanpa saling bertabrakan (*thread-safe*).

---

## 📄 Lisensi & Kontribusi

Didistribusikan di bawah lisensi [MIT](LICENSE). Terbuka untuk pengembangan komunitas dan integrasi pengujian software.

Silakan sampaikan usulan perbaikan atau isu melalui [GitHub Issues](https://github.com/MasterPandaa/Virtual-Printer-V2/issues) atau ajukan *Pull Request*.

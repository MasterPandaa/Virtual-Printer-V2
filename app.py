"""
Virtual RAW TCP/IP Printer Server v2 (Multi-Printer & Document Preview)
A multi-instance desktop GUI emulator running up to 4 concurrent TCP/IP socket listeners.
Features auto-format detection (PDF/HTML/RAW), external PDF preview, hex dump view, and file export.
Built with Python 3 standard library (Tkinter, Sockets, Threading).
"""

import os
import re
import socket
import threading
import datetime
import tempfile
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog


class PrinterInstance:
    """
    Represents a single Virtual RAW TCP/IP Printer listener on a specific port and IP.
    """
    def __init__(self, printer_id, name, default_port, on_log_cb, on_payload_cb, on_status_cb):
        self.id = printer_id
        self.name = name
        self.port = default_port
        self.ip = "0.0.0.0"
        self.is_running = False
        self.server_socket = None
        self.server_thread = None
        self.on_log_cb = on_log_cb
        self.on_payload_cb = on_payload_cb
        self.on_status_cb = on_status_cb
        self.job_count = 0
        self.last_job_data = None
        self.last_job_meta = None

    def start(self, ip=None, port=None, name=None):
        if ip:
            self.ip = ip
        if port:
            self.port = port
        if name:
            self.name = name

        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.ip, self.port))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1.0)
            self.is_running = True

            self.on_status_cb(self.id, True, f"LISTENING {self.ip}:{self.port}")
            self.on_log_cb(self.id, f"Virtual Printer '{self.name}' started on {self.ip}:{self.port}", "START")

            self.server_thread = threading.Thread(target=self._server_loop, daemon=True)
            self.server_thread.start()
            return True, "OK"
        except Exception as e:
            self.is_running = False
            if self.server_socket:
                try:
                    self.server_socket.close()
                except Exception:
                    pass
                self.server_socket = None
            err_msg = str(e)
            self.on_status_cb(self.id, False, f"ERROR: {err_msg}")
            self.on_log_cb(self.id, f"Failed to start printer '{self.name}' on {self.ip}:{self.port}: {err_msg}", "ERROR")
            return False, err_msg

    def stop(self):
        self.is_running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass
            self.server_socket = None

        self.on_status_cb(self.id, False, "STOPPED")
        self.on_log_cb(self.id, f"Virtual Printer '{self.name}' stopped.", "STOP")

    def _server_loop(self):
        while self.is_running:
            try:
                client_sock, client_addr = self.server_socket.accept()
            except socket.timeout:
                continue
            except Exception:
                break

            self.on_log_cb(self.id, f"Accepted connection from {client_addr[0]}:{client_addr[1]}", "CONNECT")
            client_handler = threading.Thread(
                target=self._handle_client,
                args=(client_sock, client_addr),
                daemon=True
            )
            client_handler.start()

    def _handle_client(self, client_sock, client_addr):
        client_sock.settimeout(10.0)
        received_chunks = []
        try:
            while True:
                data = client_sock.recv(4096)
                if not data:
                    break
                received_chunks.append(data)
        except socket.timeout:
            self.on_log_cb(self.id, f"Connection timeout/completed from {client_addr[0]}:{client_addr[1]}", "TIMEOUT")
        except Exception as e:
            self.on_log_cb(self.id, f"Socket read end from {client_addr[0]}:{client_addr[1]}: {str(e)}", "INFO")
        finally:
            try:
                client_sock.close()
            except Exception:
                pass

            total_data = b"".join(received_chunks)
            if total_data:
                self.job_count += 1
                self.last_job_data = total_data
                self.last_job_meta = {
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "client": f"{client_addr[0]}:{client_addr[1]}",
                    "size": len(total_data),
                    "job_no": self.job_count
                }
                self.on_log_cb(self.id, f"Job #{self.job_count} received ({len(total_data)} B) from {client_addr[0]}:{client_addr[1]}", "SUCCESS")
                self.on_payload_cb(self.id, self.last_job_meta, total_data)
            else:
                self.on_log_cb(self.id, f"Ping/Handshake from {client_addr[0]}:{client_addr[1]} (0 B)", "PING")


class MultiVirtualPrinterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Virtual RAW Printer Server v2 — Multi-Printer & Document Preview")
        self.root.geometry("1450x920")
        self.root.minsize(1050, 720)

        # Temporary folder for received PDF previews
        self.temp_dir = os.path.join(tempfile.gettempdir(), "virtual_printer_v2")
        os.makedirs(self.temp_dir, exist_ok=True)

        self.printers = {}
        self.printer_uipos = {}

        self._apply_styles()
        self._init_printer_instances()
        self._build_ui()

    def _apply_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Color palette (Dark Modern Catppuccin / Obsidian inspired)
        self.bg_color = "#181825"
        self.card_bg = "#1e1e2e"
        self.card_border = "#313244"
        self.accent_color = "#89b4fa"
        self.text_color = "#cdd6f4"
        self.subtext_color = "#a6adc8"
        self.success_color = "#a6e3a1"
        self.danger_color = "#f38ba8"
        self.warning_color = "#fab387"

        self.root.configure(bg=self.bg_color)

        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("Card.TFrame", background=self.card_bg, relief="flat")
        self.style.configure("HeaderFrame.TFrame", background=self.card_bg)

        self.style.configure("TLabel", background=self.bg_color, foreground=self.text_color, font=("Segoe UI", 9))
        self.style.configure("Card.TLabel", background=self.card_bg, foreground=self.text_color, font=("Segoe UI", 9))
        self.style.configure("Title.TLabel", background=self.bg_color, foreground="#ffffff", font=("Segoe UI", 14, "bold"))
        self.style.configure("SubTitle.TLabel", background=self.bg_color, foreground=self.subtext_color, font=("Segoe UI", 9))
        self.style.configure("PaneTitle.TLabel", background=self.card_bg, foreground=self.accent_color, font=("Segoe UI", 9, "bold"))

        self.style.configure("TNotebook", background=self.card_bg, borderwidth=0)
        self.style.configure("TNotebook.Tab", background="#313244", foreground=self.text_color, padding=[8, 3], font=("Segoe UI", 8))
        self.style.map("TNotebook.Tab", background=[("selected", self.accent_color)], foreground=[("selected", "#11111b")])

        self.style.configure("TCombobox", fieldbackground="#11111b", background="#313244", foreground="#cdd6f4", font=("Segoe UI", 8))

    def _init_printer_instances(self):
        configs = [
            (1, "Printer 1", 9100),
            (2, "Printer 2", 9101),
            (3, "Printer 3", 9102),
            (4, "Printer 4", 9103),
        ]

        for p_id, label, port in configs:
            self.printers[p_id] = PrinterInstance(
                printer_id=p_id,
                name=f"Printer {p_id} ({label})",
                default_port=port,
                on_log_cb=self._handle_printer_log,
                on_payload_cb=self._handle_printer_payload,
                on_status_cb=self._handle_printer_status
            )

    def _build_ui(self):
        # 1. Top Header & Global Master Controls
        header_card = ttk.Frame(self.root, style="Card.TFrame", padding="12 10")
        header_card.pack(fill="x", padx=10, pady=8)

        # Title block
        title_box = ttk.Frame(header_card, style="Card.TFrame")
        title_box.pack(side="left")

        ttk.Label(title_box, text="🖨️ Virtual Printer v2 — Multi-Printer Testing Center", style="Title.TLabel").pack(anchor="w")
        local_ip = self._get_local_ip()
        ttk.Label(title_box, text=f"Local Host IP: 127.0.0.1 | Network LAN IP: {local_ip} | Configurable IP, Port & Label per Printer Pane", style="SubTitle.TLabel").pack(anchor="w")

        # Control Buttons block
        btn_box = ttk.Frame(header_card, style="Card.TFrame")
        btn_box.pack(side="right")

        self.btn_start_all = tk.Button(
            btn_box, text="▶ Start All Printers", bg="#a6e3a1", fg="#11111b",
            font=("Segoe UI", 9, "bold"), relief="flat", padx=12, pady=4,
            activebackground="#94e2d5", cursor="hand2", command=self.start_all_printers
        )
        self.btn_start_all.pack(side="left", padx=4)

        self.btn_stop_all = tk.Button(
            btn_box, text="⏹ Stop All", bg="#f38ba8", fg="#11111b",
            font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=4,
            activebackground="#e5c890", cursor="hand2", command=self.stop_all_printers
        )
        self.btn_stop_all.pack(side="left", padx=4)

        btn_clear_all = tk.Button(
            btn_box, text="🧹 Clear All Logs", bg="#45475a", fg="#cdd6f4",
            font=("Segoe UI", 9), relief="flat", padx=10, pady=4,
            activebackground="#585b70", cursor="hand2", command=self.clear_all_logs
        )
        btn_clear_all.pack(side="left", padx=4)

        # 2. Main 2x2 Split Screen Grid Layout
        grid_container = ttk.Frame(self.root)
        grid_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Configure 2x2 grid weights
        grid_container.rowconfigure(0, weight=1)
        grid_container.rowconfigure(1, weight=1)
        grid_container.columnconfigure(0, weight=1)
        grid_container.columnconfigure(1, weight=1)

        # Build 4 Printer Panes
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        default_labels = ["Area 1", "Area 2", "Area 3", "Area 4"]

        for p_id in range(1, 5):
            r, c = positions[p_id - 1]
            def_label = default_labels[p_id - 1]
            pane_frame = self._build_printer_pane(grid_container, p_id, def_label)
            pane_frame.grid(row=r, column=c, sticky="nsew", padx=4, pady=4)

    def _build_printer_pane(self, parent, p_id, default_label):
        printer = self.printers[p_id]
        pane = ttk.Frame(parent, style="Card.TFrame", padding="8")

        # --- Row 1: Header (Pane Badge + Label Combobox/Entry + Start/Stop Button) ---
        row1 = ttk.Frame(pane, style="Card.TFrame")
        row1.pack(fill="x", pady=(0, 4))

        ttk.Label(row1, text=f"Printer {p_id}", style="PaneTitle.TLabel").pack(side="left", padx=(0, 4))
        ttk.Label(row1, text="Label:", style="Card.TLabel", font=("Segoe UI", 8)).pack(side="left", padx=(2, 2))

        # Label Combobox with customizable options
        label_combo = ttk.Combobox(
            row1, width=16, font=("Segoe UI", 8),
            values=["Area 1", "Area 2", "Area 3", "Area 4", "Office", "Warehouse", "Packaging", "Receipt"]
        )
        label_combo.set(default_label)
        label_combo.pack(side="left", padx=(0, 8))

        btn_toggle = tk.Button(
            row1, text="▶ Start", bg="#a6e3a1", fg="#11111b",
            font=("Segoe UI", 8, "bold"), relief="flat", padx=10, pady=2,
            cursor="hand2", command=lambda p=p_id: self.toggle_printer(p)
        )
        btn_toggle.pack(side="right")

        # --- Row 2: Inputs (IP + Port) & Status Bar ---
        row2 = ttk.Frame(pane, style="Card.TFrame")
        row2.pack(fill="x", pady=(0, 6))

        ttk.Label(row2, text="IP:", style="Card.TLabel", font=("Segoe UI", 8)).pack(side="left", padx=(0, 2))
        ip_ent = ttk.Entry(row2, width=16, font=("Segoe UI", 8))
        ip_ent.insert(0, "0.0.0.0")
        ip_ent.pack(side="left", padx=(0, 6))

        ttk.Label(row2, text="Port:", style="Card.TLabel", font=("Segoe UI", 8)).pack(side="left", padx=(0, 2))
        port_ent = ttk.Entry(row2, width=6, font=("Segoe UI", 8))
        port_ent.insert(0, str(printer.port))
        port_ent.pack(side="left", padx=(0, 8))

        status_lbl = ttk.Label(row2, text="● STOPPED", foreground=self.danger_color, style="Card.TLabel", font=("Segoe UI", 8, "bold"))
        status_lbl.pack(side="left", padx=(4, 0))

        job_cnt_lbl = ttk.Label(row2, text="Jobs: 0", foreground=self.subtext_color, style="Card.TLabel", font=("Segoe UI", 8))
        job_cnt_lbl.pack(side="right")

        # --- Tabs: Document Preview vs Connection Activity Log ---
        notebook = ttk.Notebook(pane)
        notebook.pack(fill="both", expand=True)

        # --- Tab 1: Received Document Preview ---
        tab_preview = ttk.Frame(notebook, style="Card.TFrame", padding="4")
        notebook.add(tab_preview, text="📄 Document Preview")

        # Preview Action Bar
        prev_act_bar = ttk.Frame(tab_preview, style="Card.TFrame")
        prev_act_bar.pack(fill="x", pady=(0, 4))

        doc_type_lbl = ttk.Label(prev_act_bar, text="No document received yet", foreground=self.subtext_color, style="Card.TLabel", font=("Segoe UI", 8, "italic"))
        doc_type_lbl.pack(side="left")

        btn_open_ext = tk.Button(
            prev_act_bar, text="👁️ Open PDF", bg="#89b4fa", fg="#11111b",
            font=("Segoe UI", 8, "bold"), relief="flat", padx=6, pady=1,
            cursor="hand2", state="disabled", command=lambda p=p_id: self.open_pdf_external(p)
        )
        btn_open_ext.pack(side="right", padx=2)

        btn_save = tk.Button(
            prev_act_bar, text="💾 Save File", bg="#313244", fg="#cdd6f4",
            font=("Segoe UI", 8), relief="flat", padx=6, pady=1,
            cursor="hand2", state="disabled", command=lambda p=p_id: self.save_document(p)
        )
        btn_save.pack(side="right", padx=2)

        # Preview Modes Notebook inside Tab 1 (Formatted / Raw Text / Hex Dump)
        doc_sub_nb = ttk.Notebook(tab_preview)
        doc_sub_nb.pack(fill="both", expand=True)

        # 1. Formatted View
        fmt_text = scrolledtext.ScrolledText(
            doc_sub_nb, wrap="word", bg="#11111b", fg="#a6e3a1",
            insertbackground="#ffffff", font=("Consolas", 8), relief="flat"
        )
        doc_sub_nb.add(fmt_text, text="Formatted")

        # 2. Raw Text View
        raw_text = scrolledtext.ScrolledText(
            doc_sub_nb, wrap="none", bg="#11111b", fg="#cdd6f4",
            insertbackground="#ffffff", font=("Courier New", 8), relief="flat"
        )
        doc_sub_nb.add(raw_text, text="Raw Text")

        # 3. Hex Dump View
        hex_text = scrolledtext.ScrolledText(
            doc_sub_nb, wrap="none", bg="#11111b", fg="#fab387",
            insertbackground="#ffffff", font=("Courier New", 8), relief="flat"
        )
        doc_sub_nb.add(hex_text, text="Hex Dump")

        # --- Tab 2: Connection & Event Logs ---
        tab_log = ttk.Frame(notebook, style="Card.TFrame", padding="4")
        notebook.add(tab_log, text="📜 Activity Log")

        log_text = scrolledtext.ScrolledText(
            tab_log, wrap="word", bg="#181825", fg="#cdd6f4",
            insertbackground="#ffffff", font=("Consolas", 8), relief="flat"
        )
        log_text.pack(fill="both", expand=True)

        # Store references to UI components
        self.printer_uipos[p_id] = {
            "label_combo": label_combo,
            "ip_entry": ip_ent,
            "port_entry": port_ent,
            "btn_toggle": btn_toggle,
            "status_lbl": status_lbl,
            "job_cnt_lbl": job_cnt_lbl,
            "doc_type_lbl": doc_type_lbl,
            "btn_open_ext": btn_open_ext,
            "btn_save": btn_save,
            "fmt_text": fmt_text,
            "raw_text": raw_text,
            "hex_text": hex_text,
            "log_text": log_text,
            "current_pdf_path": None,
            "current_raw_bytes": None,
            "current_meta": None
        }

        return pane

    def _get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def toggle_printer(self, p_id):
        printer = self.printers[p_id]
        ui = self.printer_uipos[p_id]

        if not printer.is_running:
            ip_val = ui["ip_entry"].get().strip() or "0.0.0.0"
            port_str = ui["port_entry"].get().strip()
            label_val = ui["label_combo"].get().strip() or f"Printer {p_id}"

            if not port_str.isdigit() or int(port_str) < 1 or int(port_str) > 65535:
                messagebox.showerror("Port Error", f"Port for printer {p_id} is invalid (1-65535)")
                return
            port = int(port_str)
            printer.start(ip=ip_val, port=port, name=f"Printer {p_id} ({label_val})")
        else:
            printer.stop()

    def start_all_printers(self):
        for p_id, printer in self.printers.items():
            if not printer.is_running:
                ui = self.printer_uipos[p_id]
                ip_val = ui["ip_entry"].get().strip() or "0.0.0.0"
                port_str = ui["port_entry"].get().strip()
                label_val = ui["label_combo"].get().strip() or f"Printer {p_id}"
                port = int(port_str) if port_str.isdigit() else printer.port
                printer.start(ip=ip_val, port=port, name=f"Printer {p_id} ({label_val})")

    def stop_all_printers(self):
        for printer in self.printers.values():
            if printer.is_running:
                printer.stop()

    def clear_all_logs(self):
        for p_id, ui in self.printer_uipos.items():
            ui["log_text"].delete("1.0", tk.END)
            ui["fmt_text"].delete("1.0", tk.END)
            ui["raw_text"].delete("1.0", tk.END)
            ui["hex_text"].delete("1.0", tk.END)
            ui["doc_type_lbl"].config(text="No document received yet", foreground=self.subtext_color)
            ui["btn_open_ext"].config(state="disabled")
            ui["btn_save"].config(state="disabled")
            ui["current_pdf_path"] = None
            ui["current_raw_bytes"] = None
            ui["current_meta"] = None

    def _handle_printer_status(self, p_id, is_running, status_text):
        def _update():
            ui = self.printer_uipos[p_id]
            if is_running:
                ui["status_lbl"].config(text=f"● {status_text}", foreground=self.success_color)
                ui["btn_toggle"].config(text="⏹ Stop", bg="#f38ba8", fg="#11111b")
                ui["ip_entry"].config(state="disabled")
                ui["port_entry"].config(state="disabled")
                ui["label_combo"].config(state="disabled")
            else:
                ui["status_lbl"].config(text=f"● {status_text}", foreground=self.danger_color)
                ui["btn_toggle"].config(text="▶ Start", bg="#a6e3a1", fg="#11111b")
                ui["ip_entry"].config(state="normal")
                ui["port_entry"].config(state="normal")
                ui["label_combo"].config(state="normal")

        self.root.after(0, _update)

    def _handle_printer_log(self, p_id, message, level):
        def _append():
            ui = self.printer_uipos[p_id]
            now = datetime.datetime.now().strftime("%H:%M:%S")
            log_line = f"[{now}] [{level}] {message}\n"
            ui["log_text"].insert(tk.END, log_line)
            ui["log_text"].see(tk.END)

        self.root.after(0, _append)

    def _handle_printer_payload(self, p_id, meta, raw_bytes):
        def _render():
            ui = self.printer_uipos[p_id]
            ui["job_cnt_lbl"].config(text=f"Jobs: {meta['job_no']}")
            ui["current_raw_bytes"] = raw_bytes
            ui["current_meta"] = meta

            # 1. Detect Document Format (PDF, HTML/XML, RAW Text, etc.)
            is_pdf = raw_bytes.startswith(b"%PDF-")
            is_html = b"<html" in raw_bytes.lower() or b"<!doctype html" in raw_bytes.lower()

            if is_pdf:
                doc_type = "PDF Document (%PDF-)"
                # Save temporary pdf file for external viewing
                pdf_filename = f"job_p{p_id}_{meta['job_no']}_{datetime.datetime.now().strftime('%H%M%S')}.pdf"
                pdf_path = os.path.join(self.temp_dir, pdf_filename)
                try:
                    with open(pdf_path, "wb") as f:
                        f.write(raw_bytes)
                    ui["current_pdf_path"] = pdf_path
                    ui["btn_open_ext"].config(state="normal")
                except Exception as e:
                    self._handle_printer_log(p_id, f"Error saving temp PDF preview: {str(e)}", "WARNING")

                ui["doc_type_lbl"].config(text=f"📄 {doc_type} ({meta['size']} B)", foreground=self.accent_color)
            elif is_html:
                doc_type = "HTML Document Payload"
                ui["btn_open_ext"].config(state="disabled")
                ui["doc_type_lbl"].config(text=f"🌐 {doc_type} ({meta['size']} B)", foreground=self.success_color)
            else:
                doc_type = "RAW Print Payload / Text"
                ui["btn_open_ext"].config(state="disabled")
                ui["doc_type_lbl"].config(text=f"📝 {doc_type} ({meta['size']} B)", foreground=self.warning_color)

            ui["btn_save"].config(state="normal")

            # 2. Render Formatted Preview
            fmt_header = (
                f"====================================================\n"
                f" RECEIVED DOCUMENT JOB #{meta['job_no']}\n"
                f" Printer: [{p_id}] {self.printers[p_id].name}\n"
                f" Client: {meta['client']} | Time: {meta['timestamp']}\n"
                f" Type: {doc_type} | Size: {meta['size']} bytes\n"
                f"====================================================\n\n"
            )

            if is_pdf:
                printable_strings = re.findall(rb"[\x20-\x7e\r\n\t]{4,}", raw_bytes)
                extracted_text = "\n".join([s.decode("latin1", errors="ignore") for s in printable_strings[:50]])
                fmt_body = (
                    f"📌 [PDF BINARY DETECTED]\n"
                    f"The payload is a binary PDF document ({meta['size']} bytes).\n"
                    f"Saved temporary PDF for preview at:\n{ui['current_pdf_path']}\n\n"
                    f"Click '👁️ Open PDF' button above to open in your system default PDF reader.\n\n"
                    f"--- Extracted PDF Text / Metadata Snippets ---\n"
                    f"{extracted_text}\n"
                )
            else:
                try:
                    text_str = raw_bytes.decode("latin1")
                except Exception:
                    text_str = raw_bytes.decode("utf-8", errors="replace")
                fmt_body = text_str

            ui["fmt_text"].delete("1.0", tk.END)
            ui["fmt_text"].insert(tk.END, fmt_header + fmt_body)
            ui["fmt_text"].see("1.0")

            # 3. Render Raw Text View
            try:
                raw_str = raw_bytes.decode("utf-8", errors="replace")
            except Exception:
                raw_str = raw_bytes.decode("latin1", errors="replace")

            ui["raw_text"].delete("1.0", tk.END)
            ui["raw_text"].insert(tk.END, raw_str)
            ui["raw_text"].see("1.0")

            # 4. Render Hex Dump View (First 2048 bytes max for smooth performance)
            hex_lines = []
            dump_bytes = raw_bytes[:2048]
            for i in range(0, len(dump_bytes), 16):
                chunk = dump_bytes[i:i + 16]
                hex_part = " ".join([f"{b:02X}" for b in chunk])
                ascii_part = "".join([chr(b) if 32 <= b <= 126 else "." for b in chunk])
                hex_lines.append(f"{i:08X}  {hex_part:<48}  |{ascii_part}|")

            if len(raw_bytes) > 2048:
                hex_lines.append(f"\n... [{len(raw_bytes) - 2048} more bytes truncated in hex dump view] ...")

            ui["hex_text"].delete("1.0", tk.END)
            ui["hex_text"].insert(tk.END, "\n".join(hex_lines))
            ui["hex_text"].see("1.0")

        self.root.after(0, _render)

    def open_pdf_external(self, p_id):
        ui = self.printer_uipos[p_id]
        pdf_path = ui.get("current_pdf_path")
        if pdf_path and os.path.exists(pdf_path):
            try:
                os.startfile(pdf_path)
            except Exception as e:
                messagebox.showerror("File Error", f"Failed to open PDF:\n{str(e)}")
        else:
            messagebox.showwarning("Warning", "No temporary PDF file available.")

    def save_document(self, p_id):
        ui = self.printer_uipos[p_id]
        raw_bytes = ui.get("current_raw_bytes")
        meta = ui.get("current_meta")
        if not raw_bytes:
            messagebox.showwarning("Warning", "No document payload available to save.")
            return

        is_pdf = raw_bytes.startswith(b"%PDF-")
        default_ext = ".pdf" if is_pdf else ".txt"
        file_types = [("PDF Document", "*.pdf"), ("Text File", "*.txt"), ("RAW File", "*.raw"), ("All Files", "*.*")] if is_pdf else [("Text File", "*.txt"), ("RAW File", "*.raw"), ("All Files", "*.*")]

        default_name = f"printer_{p_id}_job_{meta['job_no']}{default_ext}"
        filepath = filedialog.asksaveasfilename(
            title="Save Received Document",
            initialfile=default_name,
            filetypes=file_types
        )

        if filepath:
            try:
                with open(filepath, "wb") as f:
                    f.write(raw_bytes)
                messagebox.showinfo("Success", f"Document saved successfully to:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")


def main():
    root = tk.Tk()
    app = MultiVirtualPrinterApp(root)

    def on_closing():
        app.stop_all_printers()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()

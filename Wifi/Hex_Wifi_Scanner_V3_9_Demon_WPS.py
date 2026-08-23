import subprocess
import threading
from datetime import datetime
import csv
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import customtkinter as ctk


APP_TITLE = "Hex Wi-Fi Scanner V3.9 - Demon WPS 😈"
APP_GEOMETRY = "1200x700"


# =========================
#  Cargar archivo OUI grande
# =========================

def load_oui_file(filename="manuf_demon.txt"):
    """
    Carga un archivo de OUIs estilo Wireshark:
    XX:XX:XX <fabricante...>

    Ejemplo línea:
    00:11:22 Cisco Systems
    """
    oui_map = {}
    try:
        with open(filename, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                if len(parts) < 2:
                    continue
                prefix = parts[0].upper()
                if ":" in prefix and len(prefix) == 8:  # XX:XX:XX
                    vendor = " ".join(parts[1:])
                    oui_map[prefix] = vendor
    except FileNotFoundError:
        # Si no existe, seguimos pero sin fabricantes
        return {}
    return oui_map


OUI_VENDOR = load_oui_file()


def lookup_vendor(bssid: str) -> str:
    """Devuelve el fabricante a partir del OUI del BSSID."""
    try:
        parts = bssid.upper().split(":")
        if len(parts) < 3:
            return "Desconocido"
        oui = ":".join(parts[:3])
        return OUI_VENDOR.get(oui, "Desconocido")
    except Exception:
        return "Desconocido"


# =========================
#  Utilidades de señal
# =========================

def signal_to_bar(dbm: int) -> str:
    """
    Convierte una señal en dBm a barra tipo Wireshark:
    █████, ████░, ███░░, etc.
    """
    if dbm >= -50:
        blocks = 5
    elif dbm >= -60:
        blocks = 4
    elif dbm >= -70:
        blocks = 3
    elif dbm >= -80:
        blocks = 2
    else:
        blocks = 1
    return "█" * blocks + "░" * (5 - blocks)


def parse_dbm(raw: str) -> int:
    """Intenta parsear un valor de señal como dBm (int)."""
    s = str(raw).strip()
    if s.endswith("dBm"):
        s = s[:-3].strip()
    try:
        return int(s)
    except Exception:
        return -100


# =========================
#  Utilidades de sistema
# =========================

def run_command(cmd):
    """Ejecuta un comando y devuelve (stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return "", f"Error ejecutando comando: {e}"


# =========================
#  Clase principal
# =========================

class HexWifiScanner(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Config ventana
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.title(APP_TITLE)
        self.geometry(APP_GEOMETRY)
        self.minsize(1100, 650)

        # Estado
        self.current_iface = None
        self.scan_thread = None
        self.scanning = False
        self.stop_requested = False
        self.signal_sort_desc = True

        # Auto-refresh
        self.auto_refresh_enabled = False
        self.auto_refresh_after_id = None

        # Escaneo de clientes AP
        self.selected_bssid = None
        self.selected_channel = None
        self.stop_clients_flag = False
        self.clients_proc = None
        self.clients_thread = None

        # Layout general
        self.columnconfigure(0, weight=0, minsize=260)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self._build_left_panel()
        self._build_right_panel()
        self._build_export_menu()

        # Cargar interfaces
        self.refresh_interfaces()

    # =========================
    #  Construcción de UI
    # =========================

    def _build_left_panel(self):
        self.left_frame = ctk.CTkFrame(self, corner_radius=15)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(
            self.left_frame,
            text="Hex Wi-Fi Scanner V3.9",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 5))

        ctk.CTkLabel(
            self.left_frame,
            text="Modo Demoníaco 😈\nEscaneo legal educativo",
            justify="center"
        ).pack(pady=(0, 15))

        # ---- INTERFAZ ----
        iface_frame = ctk.CTkFrame(self.left_frame, corner_radius=10)
        iface_frame.pack(fill="x", padx=10, pady=(5, 10))

        ctk.CTkLabel(
            iface_frame,
            text="Interfaz Wi-Fi",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))

        self.iface_combo = ctk.CTkComboBox(
            iface_frame,
            values=[],
            state="readonly",
            command=self.on_iface_change
        )
        self.iface_combo.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkButton(
            iface_frame,
            text="Detectar interfaces",
            command=self.refresh_interfaces
        ).pack(fill="x", padx=10, pady=(0, 10))

        # ---- MÉTODO ----
        method_frame = ctk.CTkFrame(self.left_frame, corner_radius=10)
        method_frame.pack(fill="x", padx=10, pady=(5, 10))

        ctk.CTkLabel(
            method_frame,
            text="Método de escaneo",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))

        self.method_combo = ctk.CTkComboBox(
            method_frame,
            values=["Auto (nmcli ➝ iwlist)", "Sólo nmcli", "Sólo iwlist"],
            state="readonly"
        )
        self.method_combo.set("Auto (nmcli ➝ iwlist)")
        self.method_combo.pack(fill="x", padx=10, pady=(0, 10))

        # ---- ACCIONES ----
        actions_frame = ctk.CTkFrame(self.left_frame, corner_radius=10)
        actions_frame.pack(fill="x", padx=10, pady=(5, 10))

        self.scan_button = ctk.CTkButton(
            actions_frame,
            text="Iniciar escaneo",
            command=self.start_scan
        )
        self.scan_button.pack(fill="x", padx=10, pady=(10, 5))

        self.stop_button = ctk.CTkButton(
            actions_frame,
            text="Detener escaneo",
            command=self.request_stop,
            fg_color="red"
        )
        self.stop_button.pack(fill="x", padx=10, pady=(0, 10))

        # ---- ESCANEO DE CLIENTES + WPS ----
        clients_btn_frame = ctk.CTkFrame(self.left_frame, corner_radius=10)
        clients_btn_frame.pack(fill="x", padx=10, pady=(5, 10))

        ctk.CTkLabel(
            clients_btn_frame,
            text="AP seleccionado (doble clic)\nClientes + WPS",
            font=ctk.CTkFont(size=14, weight="bold"),
            justify="center"
        ).pack(pady=(10, 5))

        self.ap_clients_button = ctk.CTkButton(
            clients_btn_frame,
            text="Escanear clientes del AP",
            command=self.start_ap_clients_scan
        )
        self.ap_clients_button.pack(fill="x", padx=10, pady=(0, 5))

        self.ap_clients_stop_button = ctk.CTkButton(
            clients_btn_frame,
            text="Detener escaneo de clientes",
            fg_color="red",
            command=self.stop_ap_clients_scan
        )
        self.ap_clients_stop_button.pack(fill="x", padx=10, pady=(0, 5))

        self.wps_button = ctk.CTkButton(
            clients_btn_frame,
            text="Analizar WPS del AP",
            command=self.analyze_wps_for_selected_ap
        )
        self.wps_button.pack(fill="x", padx=10, pady=(0, 10))

        # ---- EXPORTAR ----
        export_frame = ctk.CTkFrame(self.left_frame, corner_radius=10)
        export_frame.pack(fill="x", padx=10, pady=(5, 10))

        ctk.CTkLabel(
            export_frame,
            text="Exportar resultados",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))

        self.export_button = ctk.CTkButton(
            export_frame,
            text="Exportar datos ▾",
            command=self.show_export_menu
        )
        self.export_button.pack(fill="x", padx=10, pady=(0, 10))

        # Info legal
        ctk.CTkLabel(
            self.left_frame,
            text="⚠ Usa esto solo en tus redes\n o en laboratorio.",
            text_color="orange",
            justify="center"
        ).pack(pady=(10, 10))

    def _build_right_panel(self):
        self.right_frame = ctk.CTkFrame(self, corner_radius=15)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # 3 filas: tabla APs, tabla clientes, logs
        self.right_frame.rowconfigure(0, weight=3)
        self.right_frame.rowconfigure(1, weight=2)
        self.right_frame.rowconfigure(2, weight=1)
        self.right_frame.columnconfigure(0, weight=1)

        # ---- APs ----
        table_container = ctk.CTkFrame(self.right_frame, corner_radius=10)
        table_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))

        ctk.CTkLabel(
            table_container,
            text="Redes Wi-Fi detectadas (APs)",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))

        # Auto-refresh
        controls_frame = ctk.CTkFrame(table_container, corner_radius=8)
        controls_frame.pack(fill="x", padx=10, pady=(0, 5))

        auto_label = ctk.CTkLabel(controls_frame, text="Auto-refresh:")
        auto_label.pack(side="left", padx=(10, 5), pady=5)

        self.auto_refresh_switch = ctk.CTkSwitch(
            controls_frame,
            text="OFF",
            command=self.toggle_auto_refresh
        )
        self.auto_refresh_switch.pack(side="left", padx=(0, 20), pady=5)

        interval_label = ctk.CTkLabel(controls_frame, text="Intervalo (s):")
        interval_label.pack(side="left", padx=(10, 5), pady=5)

        self.auto_interval_combo = ctk.CTkComboBox(
            controls_frame,
            values=["2", "5", "10", "30", "60"],
            state="readonly"
        )
        self.auto_interval_combo.set("10")
        self.auto_interval_combo.pack(side="left", padx=(0, 10), pady=5)

        # Tabla APs
        tree_frame = ctk.CTkFrame(table_container, corner_radius=8)
        tree_frame.pack(expand=True, fill="both", padx=10, pady=(0, 10))

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("bssid", "ssid", "channel", "signal", "bars", "enc", "vendor"),
            show="headings"
        )

        self.tree.heading("bssid", text="BSSID")
        self.tree.heading("ssid", text="SSID")
        self.tree.heading("channel", text="Canal")
        self.tree.heading("signal", text="Señal (dBm)", command=self.sort_by_signal)
        self.tree.heading("bars", text="Intensidad")
        self.tree.heading("enc", text="Cifrado")
        self.tree.heading("vendor", text="Fabricante")

        self.tree.column("bssid", width=160, anchor="center")
        self.tree.column("ssid", width=200, anchor="w")
        self.tree.column("channel", width=60, anchor="center")
        self.tree.column("signal", width=100, anchor="center")
        self.tree.column("bars", width=110, anchor="center")
        self.tree.column("enc", width=110, anchor="center")
        self.tree.column("vendor", width=180, anchor="w")

        y_scroll = ctk.CTkScrollbar(tree_frame, command=self.tree.yview)
        x_scroll = ctk.CTkScrollbar(tree_frame, command=self.tree.xview, orientation="horizontal")
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        self.tree.tag_configure("strong", background="#144d14")
        self.tree.tag_configure("medium", background="#4d4d14")
        self.tree.tag_configure("weak", background="#4d2c14")
        self.tree.tag_configure("veryweak", background="#4d1414")

        self.tree.tag_configure("enc_open", foreground="#bbbbbb")
        self.tree.tag_configure("enc_wep", foreground="#ff4d4d")
        self.tree.tag_configure("enc_wpa", foreground="#ff9933")
        self.tree.tag_configure("enc_wpa2", foreground="#66ff66")
        self.tree.tag_configure("enc_wpa3", foreground="#99ffcc")

        self.tree.bind("<Double-1>", self.on_tree_double_click)

        # ---- CLIENTES ----
        clients_container = ctk.CTkFrame(self.right_frame, corner_radius=10)
        clients_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 5))

        ctk.CTkLabel(
            clients_container,
            text="Estaciones / Clientes del AP seleccionado",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))

        clients_frame = ctk.CTkFrame(clients_container, corner_radius=8)
        clients_frame.pack(expand=True, fill="both", padx=10, pady=(0, 10))

        self.clients_tree = ttk.Treeview(
            clients_frame,
            columns=("mac", "power", "rate", "lost", "frames", "probe"),
            show="headings"
        )

        self.clients_tree.heading("mac", text="MAC")
        self.clients_tree.heading("power", text="Potencia")
        self.clients_tree.heading("rate", text="Rate")
        self.clients_tree.heading("lost", text="Lost")
        self.clients_tree.heading("frames", text="Frames")
        self.clients_tree.heading("probe", text="Probe / SSID")

        self.clients_tree.column("mac", width=160, anchor="center")
        self.clients_tree.column("power", width=70, anchor="center")
        self.clients_tree.column("rate", width=80, anchor="center")
        self.clients_tree.column("lost", width=60, anchor="center")
        self.clients_tree.column("frames", width=70, anchor="center")
        self.clients_tree.column("probe", width=220, anchor="w")

        clients_y_scroll = ctk.CTkScrollbar(clients_frame, command=self.clients_tree.yview)
        self.clients_tree.configure(yscrollcommand=clients_y_scroll.set)

        self.clients_tree.grid(row=0, column=0, sticky="nsew")
        clients_y_scroll.grid(row=0, column=1, sticky="ns")

        clients_frame.rowconfigure(0, weight=1)
        clients_frame.columnconfigure(0, weight=1)

        # ---- LOGS + RESUMEN WPS ----
        logs_frame = ctk.CTkFrame(self.right_frame, corner_radius=10)
        logs_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5, 10))

        title_frame = ctk.CTkFrame(logs_frame, corner_radius=8)
        title_frame.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(
            title_frame,
            text="Console / Logs",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left", padx=(0, 10))

        self.wps_summary_label = ctk.CTkLabel(
            title_frame,
            text="WPS: sin analizar",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#cccccc"
        )
        self.wps_summary_label.pack(side="left", padx=(10, 0))

        self.logs_text = ctk.CTkTextbox(logs_frame)
        self.logs_text.pack(expand=True, fill="both", padx=10, pady=(0, 10))

    def _build_export_menu(self):
        self.export_menu = tk.Menu(self, tearoff=0)
        self.export_menu.add_command(label="Exportar APs a CSV", command=self.export_to_csv)
        self.export_menu.add_command(label="Exportar APs a JSON", command=self.export_to_json)

    # =========================
    #  Utilidades UI
    # =========================

    def log(self, msg):
        ts = datetime.now().strftime("[%H:%M:%S] ")
        self.logs_text.insert("end", ts + msg + "\n")
        self.logs_text.see("end")

    def on_iface_change(self, value):
        self.current_iface = value
        self.log(f"Interfaz seleccionada: {value}")

    def refresh_interfaces(self):
        stdout, stderr = run_command("iw dev | awk '$1==\"Interface\"{print $2}'")
        self.iface_combo.configure(values=[])
        self.current_iface = None

        if stdout:
            ifaces = stdout.splitlines()
            if ifaces:
                self.iface_combo.configure(values=ifaces)
                self.iface_combo.set(ifaces[0])
                self.current_iface = ifaces[0]
                self.log(f"Interfaces encontradas: {', '.join(ifaces)}")
                return

        self.iface_combo.set("")
        self.log("No se detectaron interfaces Wi-Fi.")

    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def clear_clients_table(self):
        for item in self.clients_tree.get_children():
            self.clients_tree.delete(item)

    # =========================
    #  Auto-refresh
    # =========================

    def get_auto_interval_seconds(self) -> int:
        val = self.auto_interval_combo.get().strip()
        try:
            return max(1, int(val))
        except Exception:
            return 10

    def toggle_auto_refresh(self):
        if self.auto_refresh_switch.get() == 1:
            self.auto_refresh_enabled = True
            self.auto_refresh_switch.configure(text="ON")
            self.log(f"Auto-refresh ACTIVADO (cada {self.get_auto_interval_seconds()} s).")
            self.schedule_next_auto_refresh()
        else:
            self.auto_refresh_enabled = False
            self.auto_refresh_switch.configure(text="OFF")
            self.log("Auto-refresh DESACTIVADO.")
            if self.auto_refresh_after_id is not None:
                try:
                    self.after_cancel(self.auto_refresh_after_id)
                except Exception:
                    pass
                self.auto_refresh_after_id = None

    def schedule_next_auto_refresh(self):
        if not self.auto_refresh_enabled:
            return
        interval_ms = self.get_auto_interval_seconds() * 1000
        if self.auto_refresh_after_id is not None:
            try:
                self.after_cancel(self.auto_refresh_after_id)
            except Exception:
                pass
        self.auto_refresh_after_id = self.after(interval_ms, self._auto_refresh_tick)

    def _auto_refresh_tick(self):
        if not self.auto_refresh_enabled:
            return
        if not self.scanning:
            self.log("Auto-refresh: lanzando nuevo escaneo...")
            self.start_scan()
        else:
            self.log("Auto-refresh: esperando a que termine el escaneo activo...")
        self.schedule_next_auto_refresh()

    # =========================
    #  Escaneo general APs
    # =========================

    def start_scan(self):
        if not self.current_iface:
            messagebox.showwarning("Hex Scanner", "Selecciona una interfaz primero.")
            return
        if self.scanning:
            self.log("Ya hay un escaneo en curso.")
            return

        self.scanning = True
        self.stop_requested = False
        self.clear_table()
        self.log("Iniciando escaneo de APs...")

        method = self.method_combo.get()
        self.scan_button.configure(state="disabled")

        self.scan_thread = threading.Thread(
            target=self._scan_worker,
            args=(method,),
            daemon=True
        )
        self.scan_thread.start()

    def request_stop(self):
        if not self.scanning:
            self.log("No hay escaneo activo.")
            return
        self.stop_requested = True
        self.log("Deteniendo escaneo (cuando termine el comando)...")

    def _scan_worker(self, mode):
        nets = []

        try_nm = mode in ("Auto (nmcli ➝ iwlist)", "Sólo nmcli")
        try_iw = mode in ("Auto (nmcli ➝ iwlist)", "Sólo iwlist")

        if try_nm:
            nets = self._scan_nmcli()
            if nets:
                self._finish_scan(nets, "nmcli")
                return

        if try_iw:
            nets = self._scan_iwlist()
            self._finish_scan(nets, "iwlist")
            return

        self._finish_scan([], "error")

    def _scan_nmcli(self):
        self.log("Usando nmcli...")
        stdout, stderr = run_command(
            "nmcli -t -f SSID,BSSID,CHAN,SIGNAL,SECURITY device wifi list"
        )

        if stderr:
            if "Error" in stderr or "permission" in stderr.lower():
                self.log(f"nmcli error: {stderr}")
            else:
                self.log(f"nmcli stderr: {stderr}")

        nets = []
        for line in stdout.splitlines():
            try:
                parts = line.split(":")
                if len(parts) < 5:
                    continue
                ssid = parts[0]
                bssid = parts[1]
                channel = parts[2]
                signal_percent = parts[3]
                security = ":".join(parts[4:]) if len(parts) > 4 else "OPEN"
                if not bssid or ":" not in bssid:
                    continue
                try:
                    p = int(signal_percent)
                    dbm = int(p / 2 - 100)
                except Exception:
                    dbm = -100
                nets.append({
                    "bssid": bssid,
                    "ssid": ssid if ssid else "(oculto)",
                    "channel": channel,
                    "signal": str(dbm),
                    "enc": security if security else "OPEN"
                })
            except Exception:
                continue
        return nets

    def _scan_iwlist(self):
        self.log("Usando iwlist...")
        stdout, stderr = run_command("iwlist scan")

        if "Cell " not in stdout:
            self.log("iwlist no devolvió celdas válidas, saltando a nmcli si está en modo Auto.")
            if stderr:
                self.log(f"iwlist stderr: {stderr}")
            return []

        nets = []
        cells = stdout.split("Cell ")
        for cell in cells:
            if "Address:" not in cell:
                continue
            try:
                bssid = cell.split("Address:")[1].split("\n")[0].strip()
                ssid = cell.split("ESSID:")[1].split("\n")[0].replace('"', "").strip() if "ESSID:" in cell else "(oculto)"
                channel = cell.split("Channel:")[1].split("\n")[0].strip() if "Channel:" in cell else "?"
                signal_raw = cell.split("Signal level=")[1].split(" ")[0].strip() if "Signal level=" in cell else "-100"
                dbm = parse_dbm(signal_raw)

                if "WPA3" in cell:
                    enc = "WPA3"
                elif "WPA2" in cell:
                    enc = "WPA2"
                elif "WPA" in cell:
                    enc = "WPA"
                elif "WEP" in cell:
                    enc = "WEP"
                else:
                    enc = "OPEN"

                nets.append({
                    "bssid": bssid,
                    "ssid": ssid,
                    "channel": channel,
                    "signal": str(dbm),
                    "enc": enc
                })
            except Exception:
                continue
        return nets

    def _finish_scan(self, networks, source):
        def update():
            self.scanning = False
            self.scan_button.configure(state="normal")

            if not networks:
                self.log("No se detectaron redes.")
                return

            for net in networks:
                dbm = parse_dbm(net["signal"])
                bars = signal_to_bar(dbm)
                vendor = lookup_vendor(net["bssid"])

                if dbm >= -50:
                    sig_tag = "strong"
                elif dbm >= -70:
                    sig_tag = "medium"
                elif dbm >= -85:
                    sig_tag = "weak"
                else:
                    sig_tag = "veryweak"

                enc_raw = net["enc"].upper()
                if "WEP" in enc_raw:
                    enc_tag = "enc_wep"
                    enc_display = "WEP"
                elif "WPA3" in enc_raw:
                    enc_tag = "enc_wpa3"
                    enc_display = "WPA3"
                elif "WPA2" in enc_raw:
                    enc_tag = "enc_wpa2"
                    enc_display = "WPA2"
                elif "WPA" in enc_raw:
                    enc_tag = "enc_wpa"
                    enc_display = "WPA"
                elif "OPEN" in enc_raw:
                    enc_tag = "enc_open"
                    enc_display = "OPEN"
                else:
                    enc_tag = "enc_open"
                    enc_display = enc_raw or "OPEN"

                self.tree.insert(
                    "",
                    "end",
                    values=(
                        net["bssid"],
                        net["ssid"],
                        net["channel"],
                        net["signal"],
                        bars,
                        enc_display,
                        vendor
                    ),
                    tags=(sig_tag, enc_tag)
                )

            self.log(f"Escaneo completado ({len(networks)} redes, método: {source}).")

        self.after(0, update)

    # =========================
    #  Ordenar por potencia
    # =========================

    def sort_by_signal(self):
        children = list(self.tree.get_children())
        if not children:
            return

        def get_dbm(item_id):
            vals = self.tree.item(item_id, "values")
            if not vals:
                return -100
            raw = vals[3]
            return parse_dbm(str(raw))

        children.sort(key=get_dbm, reverse=self.signal_sort_desc)

        for idx, item_id in enumerate(children):
            self.tree.move(item_id, "", idx)

        direction = "descendente" if self.signal_sort_desc else "ascendente"
        self.log(f"Tabla ordenada por potencia ({direction}).")
        self.signal_sort_desc = not self.signal_sort_desc

    # =========================
    #  Doble clic en AP
    # =========================

    def on_tree_double_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
        vals = self.tree.item(item_id, "values")
        if not vals:
            return

        bssid, ssid, channel, signal, bars, enc, vendor = vals
        self.selected_bssid = bssid
        self.selected_channel = channel

        self.clipboard_clear()
        self.clipboard_append(bssid)

        self.log(
            f"AP seleccionado → SSID: {ssid} | BSSID: {bssid} | Canal: {channel} | "
            f"Potencia: {signal} dBm ({bars}) | Cifrado: {enc} | Fabricante: {vendor} "
            f"(BSSID copiado / preparado para clientes + WPS)"
        )

    # =========================
    #  Escaneo clientes AP (airodump)
    # =========================

    def start_ap_clients_scan(self):
        if not self.current_iface:
            self.log("Selecciona una interfaz primero.")
            return
        if not self.selected_bssid or not self.selected_channel:
            self.log("Selecciona un AP con doble clic antes de escanear clientes.")
            return
        if self.clients_thread and self.clients_thread.is_alive():
            self.log("Ya hay un escaneo de clientes en curso.")
            return

        self.log(
            f"Iniciando análisis de clientes para {self.selected_bssid} en canal {self.selected_channel}...\n"
            f"⚠ Necesitas modo monitor y permisos (ejecuta la app como root)."
        )
        self.clear_clients_table()
        self.stop_clients_flag = False

        self.clients_thread = threading.Thread(
            target=self._clients_scan_worker,
            args=(self.selected_bssid, self.selected_channel),
            daemon=True
        )
        self.clients_thread.start()

    def stop_ap_clients_scan(self):
        self.stop_clients_flag = True
        self.log("Orden enviada para detener el escaneo de clientes...")
        if self.clients_proc:
            try:
                self.clients_proc.terminate()
            except Exception:
                pass

    def _clients_scan_worker(self, bssid, channel):
        iface = self.current_iface
        cmd = f"airodump-ng --bssid {bssid} -c {channel} {iface}"
        self.log(f"Comando clientes AP: {cmd}")

        try:
            self.clients_proc = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        except Exception as e:
            self.log(f"Error lanzando airodump-ng: {e}")
            return

        stations_block = False

        while not self.stop_clients_flag:
            line = self.clients_proc.stdout.readline()
            if not line:
                break

            line = line.strip()

            if "STATION" in line and "BSSID" in line:
                stations_block = True
                self.after(0, self.clear_clients_table)
                continue

            if not stations_block or not line:
                continue

            parts = line.split()
            if len(parts) < 6:
                continue

            mac = parts[0]
            power = parts[1]
            rate = parts[2]
            lost = parts[3]
            frames = parts[4]
            probe = " ".join(parts[5:])

            def upsert():
                for item_id in self.clients_tree.get_children():
                    vals = self.clients_tree.item(item_id, "values")
                    if vals and vals[0] == mac:
                        self.clients_tree.item(
                            item_id,
                            values=(mac, power, rate, lost, frames, probe)
                        )
                        break
                else:
                    self.clients_tree.insert(
                        "",
                        "end",
                        values=(mac, power, rate, lost, frames, probe)
                    )

            self.after(0, upsert)

        try:
            self.clients_proc.terminate()
        except Exception:
            pass
        self.clients_proc = None
        self.log("Escaneo de clientes del AP finalizado.")

    # =========================
    #  Analizador WPS (wash)
    # =========================

    def analyze_wps_for_selected_ap(self):
        """
        Analiza WPS del AP seleccionado usando 'wash'.
        Solo lectura: NO intenta PIN, NO ataca, solo informa.
        """
        if not self.current_iface:
            self.log("Selecciona una interfaz primero.")
            messagebox.showinfo("WPS", "Selecciona una interfaz primero.")
            return

        if not self.selected_bssid or not self.selected_channel:
            self.log("Selecciona un AP con doble clic antes de analizar WPS.")
            messagebox.showinfo(
                "WPS",
                "Selecciona un AP en la tabla (doble clic) antes de analizar WPS."
            )
            return

        iface = self.current_iface
        self.log(
            f"Iniciando análisis WPS para {self.selected_bssid} (canal {self.selected_channel}) "
            f"con wash en interfaz {iface}..."
        )
        self.wps_summary_label.configure(text="WPS: analizando...", text_color="#ffcc66")

        # IMPORTANTE: para wash, la interfaz debe estar en modo monitor.
        # Si no lo está, wash fallará. El usuario ya lo ha usado con wlan0 en monitor.
        cmd = f"wash -i {iface} -c {self.selected_channel}"
        stdout, stderr = run_command(cmd)

        if stderr and "command not found" in stderr.lower():
            self.log("wash no está instalado. Instálalo con: sudo apt install reaver")
            messagebox.showerror(
                "WPS",
                "No se encontró 'wash' en el sistema.\nInstálalo con:\n\nsudo apt install reaver"
            )
            self.wps_summary_label.configure(text="WPS: error (wash no encontrado)", text_color="#ff6666")
            return

        if not stdout:
            self.log("wash no devolvió salida. ¿Interfaz en modo monitor? ¿AP visible?")
            messagebox.showwarning(
                "WPS",
                "wash no devolvió datos.\nAsegúrate de que la interfaz está en modo monitor\n"
                "y que el AP está emitiendo."
            )
            self.wps_summary_label.configure(text="WPS: sin datos", text_color="#ff6666")
            return

        lines = stdout.splitlines()
        ap_info = None

        for line in lines:
            line = line.strip()
            if not line or line.startswith("BSSID") or line.startswith("-"):
                continue
            parts = line.split()
            if len(parts) < 5:
                continue
            bssid = parts[0].upper()
            if bssid != self.selected_bssid.upper():
                continue

            ch = parts[1]
            dbm = parts[2]
            wps_ver = parts[3]
            locked = parts[4]
            vendor = parts[5] if len(parts) > 5 else "?"
            ssid = " ".join(parts[6:]) if len(parts) > 6 else ""

            ap_info = {
                "bssid": bssid,
                "channel": ch,
                "dbm": dbm,
                "wps_ver": wps_ver,
                "locked": locked,
                "vendor": vendor,
                "ssid": ssid
            }
            break

        if not ap_info:
            self.log("wash no devolvió información WPS para este AP.")
            messagebox.showinfo(
                "WPS",
                "No se encontró información WPS para este AP en la salida de wash.\n\n"
                "Puede significar que el AP no anuncia WPS o está fuera de alcance."
            )
            self.wps_summary_label.configure(text="WPS: sin info", text_color="#ffcc66")
            return

        # Interpretación básica (sin explotación)
        wps_ver = ap_info["wps_ver"]
        locked = ap_info["locked"]
        ssid = ap_info["ssid"] or "(oculto)"
        vendor = ap_info["vendor"]
        dbm = ap_info["dbm"]

        if wps_ver.startswith("2"):
            risk_text = "WPS 2.0 → suele estar mejor protegido.\nRecomendado: desactivar WPS si no lo usas."
            color = "#66ff66"
            level = "Bajo / Controlado"
        else:
            risk_text = (
                "WPS versión antigua (1.x). Puede ser más vulnerable en routers viejos.\n"
                "Recomendado: desactivar WPS en la configuración del router."
            )
            color = "#ff9933"
            level = "Medio / Depende del modelo"

        if locked.lower() == "yes":
            risk_text += "\n\nEl AP reporta WPS Locked: mecanismos anti-ataque activos."
        else:
            risk_text += "\n\nEl AP NO reporta WPS Locked. Muchos routers modernos aún limitan internamente."

        summary = (
            f"AP: {ssid}\n"
            f"BSSID: {ap_info['bssid']}\n"
            f"Canal: {ap_info['channel']}  |  Señal: {dbm} dBm\n"
            f"Fabricante (wash): {vendor}\n"
            f"WPS versión: {wps_ver}\n"
            f"WPS Locked: {locked}\n\n"
            f"Nivel estimado: {level}\n\n"
            f"{risk_text}"
        )

        self.log("Análisis WPS completado para este AP:")
        for line in summary.splitlines():
            self.log("WPS ▶ " + line)

        self.wps_summary_label.configure(
            text=f"WPS {wps_ver} | Locked: {locked}",
            text_color=color
        )

        messagebox.showinfo("Análisis WPS (solo auditoría)", summary)

    # =========================
    #  Exportación APs
    # =========================

    def show_export_menu(self):
        try:
            x = self.export_button.winfo_rootx()
            y = self.export_button.winfo_rooty() + self.export_button.winfo_height()
            self.export_menu.tk_popup(x, y)
        finally:
            self.export_menu.grab_release()

    def _get_table_data(self):
        rows = []
        for item_id in self.tree.get_children():
            vals = self.tree.item(item_id, "values")
            if not vals or len(vals) < 7:
                continue
            bssid, ssid, channel, signal, bars, enc, vendor = vals
            rows.append({
                "bssid": bssid,
                "ssid": ssid,
                "channel": channel,
                "signal": parse_dbm(signal),
                "bars": bars,
                "enc": enc,
                "vendor": vendor
            })
        return rows

    def export_to_csv(self):
        data = self._get_table_data()
        if not data:
            messagebox.showinfo("Exportar CSV", "No hay datos de APs para exportar.")
            return

        default_name = f"wifi_aps_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=default_name,
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not filename:
            return

        try:
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(["BSSID", "SSID", "Canal", "dBm", "Barras", "Cifrado", "Fabricante"])
                for row in data:
                    writer.writerow([
                        row["bssid"],
                        row["ssid"],
                        row["channel"],
                        row["signal"],
                        row["bars"],
                        row["enc"],
                        row["vendor"]
                    ])
            self.log(f"Datos de APs exportados a CSV: {filename}")
            messagebox.showinfo("Exportar CSV", f"Exportado correctamente:\n{filename}")
        except Exception as e:
            self.log(f"Error exportando a CSV: {e}")
            messagebox.showerror("Exportar CSV", f"Error al exportar:\n{e}")

    def export_to_json(self):
        data = self._get_table_data()
        if not data:
            messagebox.showinfo("Exportar JSON", "No hay datos de APs para exportar.")
            return

        default_name = f"wifi_aps_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialfile=default_name,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not filename:
            return

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.log(f"Datos de APs exportados a JSON: {filename}")
            messagebox.showinfo("Exportar JSON", f"Exportado correctamente:\n{filename}")
        except Exception as e:
            self.log(f"Error exportando a JSON: {e}")
            messagebox.showerror("Exportar JSON", f"Error al exportar:\n{e}")


if __name__ == "__main__":
    app = HexWifiScanner()
    app.mainloop()

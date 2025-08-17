#!/bin/python3
import sys
import subprocess
import os
import signal
import tkinter as tk
from tkinter import ttk
from pathlib import Path

current_connection = None
vpn_process = None
connect_buttons = []

def connect_vpn(vpn_file):
    global vpn_process
    if vpn_process is None:
        vpn_process = subprocess.Popen(
            ["sudo", "openvpn", "--config", str(vpn_file)],
        )
        print(f"Connecting to {vpn_file}")
        print(f"Process: {vpn_process}")
    else:
        print("VPN already running!")

def disconnect_vpn():
    global vpn_process
    if vpn_process is not None:
        # Завершаем процесс openvpn
        os.kill(vpn_process.pid, signal.SIGKILL)
        vpn_process = None
        print("Disconnected.")
    else:
        print("No VPN connection running.")

def connect(vpn_file, button):
    global current_connection
    print(f"Connecting to {vpn_file}")

    connect_vpn()

    # Эта кнопка становится зелёной
    button.config(text="Connected", style="Success.TButton")
    button.state(["disabled"])

    # Остальные сбрасываем в синие "Connect"
    for btn in connect_buttons:
        if btn != button:
            btn.config(text="Connect", style="Primary.TButton")
            btn.state(["!disabled"])

    btn_disconnect.state(["!disabled"])
    status_label.config(text=f"Connected to {vpn_file.name}")
    current_connection = vpn_file

def disconnect():
    global current_connection
    print("Disconnect function called")

    disconnect_vpn(vpn_file)

    # Все кнопки возвращаются в "Connect" (синие)
    for btn in connect_buttons:
        btn.config(text="Connect", style="Primary.TButton")
        btn.state(["!disabled"])

    btn_disconnect.state(["disabled"])
    current_connection = None
    status_label.config(text="No connection")

root = tk.Tk()
root.title("VPN Manager")
root.minsize(420, 320)

# ===== Стили =====
style = ttk.Style(root)
style.theme_use("clam")

# Общие
style.configure("TFrame", background="#F5F6F7")
style.configure("TLabel", background="#F5F6F7", font=("Segoe UI", 10))
style.configure("TButton", font=("Segoe UI", 10), padding=6)

# Disconnect (красная)
style.configure("Danger.TButton", foreground="white", background="#E74C3C")
style.map("Danger.TButton", background=[("active", "#C0392B")])

# Connect (синие)
style.configure("Primary.TButton", foreground="white", background="#3498DB")
style.map("Primary.TButton", background=[("active", "#2980B9")])

# Connected (зелёные)
style.configure("Success.TButton", foreground="white", background="#2ECC71")
style.map("Success.TButton", background=[("active", "#27AE60")])

# ===== Интерфейс =====
main_frame = ttk.Frame(root, padding=15)
main_frame.pack(fill="both", expand=True)

status_label = ttk.Label(main_frame, text="No connection", font=("Segoe UI", 10, "bold"))
status_label.pack(pady=(0, 12), fill="x")

btn_disconnect = ttk.Button(main_frame, text="Disconnect", style="Danger.TButton", command=disconnect)
btn_disconnect.pack(pady=(0, 12), fill="x")
btn_disconnect.state(["disabled"])

vpn_dir = Path.home() / "Desktop/whoerconfigs_old"
vpn_files = list(vpn_dir.glob("*.ovpn"))

vpn_list_frame = ttk.Frame(main_frame)
vpn_list_frame.pack(fill="both", expand=True)

connect_buttons.clear()

if not vpn_files:
    ttk.Label(vpn_list_frame, text="No VPN files found").pack(pady=10)
else:
    for vpn_file in vpn_files:
        row = ttk.Frame(vpn_list_frame)
        row.pack(fill="x", pady=1)

        label = ttk.Label(row, text=vpn_file.name, anchor="w")
        label.pack(side="left", fill="x", expand=True)

        btn_connect = ttk.Button(row, text="Connect", style="Primary.TButton")
        btn_connect.config(command=lambda f=vpn_file, b=btn_connect: connect(f, b))
        btn_connect.pack(side="right")
        connect_buttons.append(btn_connect)

root.mainloop()

#!/bin/python3
import subprocess
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import threading

current_connection = None
connect_buttons = []

def disconnect_vpn():
    """Завершает все процессы OpenVPN."""
    try:
        subprocess.run(["sudo", "/usr/bin/pkill", "-9", "openvpn"], check=False)
        print("All OpenVPN processes killed.")
    except Exception as e:
        print(f"Error killing VPN processes: {e}")

def connect_vpn(vpn_file, timeout=3):
    """Запускает OpenVPN с выбранным конфигом и ждёт инициализации."""
    try:
        process = subprocess.Popen(
            ["sudo", "/usr/sbin/openvpn", "--config", str(vpn_file)],
            stderr=subprocess.STDOUT,
            stdout=subprocess.PIPE,
            text=True
        )

        connected = False

        def read_output():
            nonlocal connected
            for line in process.stdout:
                print(line, end="")
                if "Initialization Sequence Completed" in line:
                    connected = True
                    break

        t = threading.Thread(target=read_output)
        t.start()
        t.join(timeout)

        if connected:
            print(f"{vpn_file.name} connected successfully!")
            return process
        else:
            print(f"{vpn_file.name} failed to connect within {timeout} seconds.")
            disconnect_vpn()
            return False
    except Exception as e:
        print(f"Error during VPN connection: {e}")
        return False

def connect(vpn_file, button):
    """Обёртка для подключения VPN с отображением статуса в GUI."""
    disconnect()
    def worker():
        global current_connection
        process = connect_vpn(vpn_file)

        if process:
            # Успешное подключение
            button.config(text="Connected", style="Success.TButton")
            current_connection = vpn_file
            status_label.config(text=f"Connected to {vpn_file.name}")
            btn_disconnect.state(["!disabled"])
        else:
            # Неудача
            button.config(text="Connect", style="Primary.TButton")
            status_label.config(text=f"Failed to connect to {vpn_file.name}")
            current_connection = None

        # Разблокируем все кнопки
        for btn in connect_buttons:
            btn.state(["!disabled"])
            if btn != button and current_connection is None:
                btn.config(text="Connect", style="Primary.TButton")

    # Сразу обновляем интерфейс: кнопка "Connecting…", блокируем остальные
    button.config(text="Connecting...", style="Connecting.TButton")
    for btn in connect_buttons:
        btn.state(["disabled"])

    threading.Thread(target=worker, daemon=True).start()

def disconnect():
    """Отключение VPN и обновление интерфейса."""
    global current_connection
    print("Disconnect function called")
    disconnect_vpn()
    for btn in connect_buttons:
        btn.config(text="Connect", style="Primary.TButton")
        btn.state(["!disabled"])
    btn_disconnect.state(["disabled"])
    current_connection = None
    status_label.config(text="No connection")


# ===== Tkinter GUI =====
root = tk.Tk()
root.tk.call("tk", "appname", "vpn-manager")
root.title("VPN Manager")
root.minsize(420, 320)

style = ttk.Style(root)
style.theme_use("clam")

# Стили
style.configure("TButton", font=("Segoe UI", 10), padding=6)
style.configure("Danger.TButton", foreground="white", background="#E74C3C")
style.map("Danger.TButton", background=[("active", "#C0392B")])
style.configure("Primary.TButton", foreground="white", background="#3498DB")
style.map("Primary.TButton", background=[("active", "#2980B9")])
style.configure("Success.TButton", foreground="white", background="#2ECC71")
style.map("Success.TButton", background=[("active", "#27AE60")])
style.configure("Connecting.TButton", foreground="black")
style.map("Connecting.TButton", foreground=[("disabled", "black")])

main_frame = ttk.Frame(root, padding=15)
main_frame.pack(fill="both", expand=True)

status_label = ttk.Label(main_frame, text="No connection", font=("Segoe UI", 10, "bold"))
status_label.pack(pady=(0, 12), fill="x")

btn_disconnect = ttk.Button(main_frame, text="Disconnect", style="Danger.TButton", command=disconnect)
btn_disconnect.pack(pady=(0, 12), fill="x")
btn_disconnect.state(["disabled"])

vpn_dir = Path("/etc/config/ovpn/")
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

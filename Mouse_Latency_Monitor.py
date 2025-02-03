import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
from threading import Thread
import time

class SerialMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Mouse Latency Monitor")
        self.serial_port = None
        self.is_timing = False
        self.start_time = None
        self.stop_receiving = False  # Flag to control whether to stop receiving data

        # UI Layout
        self.setup_ui()

    def setup_ui(self):
        # Serial Port Selection
        tk.Label(self.root, text="Serial Port:").grid(row=0, column=0, padx=5, pady=5)
        self.cmb_port = ttk.Combobox(self.root)
        self.cmb_port.grid(row=0, column=1, padx=5, pady=5)
        self.cmb_port['values'] = [port.device for port in serial.tools.list_ports.comports()]
        if self.cmb_port['values']:
            self.cmb_port.current(0)

        # Baud Rate Selection
        tk.Label(self.root, text="Baud Rate:").grid(row=1, column=0, padx=5, pady=5)
        self.cmb_baudrate = ttk.Combobox(self.root)
        self.cmb_baudrate.grid(row=1, column=1, padx=5, pady=5)
        self.cmb_baudrate['values'] = ["9600", "19200", "38400", "57600", "115200"]
        self.cmb_baudrate.current(0)

        # Connect/Disconnect Button
        self.btn_connect = tk.Button(self.root, text="Connect", command=self.toggle_connection)
        self.btn_connect.grid(row=2, column=0, padx=5, pady=5)

        # Reconnect Button
        self.btn_reconnect = tk.Button(self.root, text="Reconnect", command=self.reconnect, state=tk.DISABLED)
        self.btn_reconnect.grid(row=2, column=1, padx=5, pady=5)

        # Real-time Data Display Area
        self.txt_data = tk.Text(self.root, height=10, width=50)
        self.txt_data.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        # Pause Button
        self.btn_pause = tk.Button(self.root, text="Pause", command=self.pause_timing, state=tk.DISABLED)
        self.btn_pause.grid(row=4, column=0, padx=5, pady=5)

        # Time Difference Display Area
        self.lbl_time_diff = tk.Label(self.root, text="Latency (s:ms:μs): 0:000:000")
        self.lbl_time_diff.grid(row=4, column=1, padx=5, pady=5)

    def toggle_connection(self):
        if self.serial_port is None or not self.serial_port.is_open:
            self.connect_serial()
        else:
            self.disconnect_serial()

    def connect_serial(self):
        port = self.cmb_port.get()
        baudrate = int(self.cmb_baudrate.get())
        try:
            self.serial_port = serial.Serial(port, baudrate, timeout=1)
            self.btn_connect.config(text="Disconnect")
            self.btn_reconnect.config(state=tk.NORMAL)
            self.btn_pause.config(state=tk.NORMAL)
            self.txt_data.insert(tk.END, "Connected to serial port\n")
            # Start a thread to read serial data
            self.read_thread = Thread(target=self.read_serial, daemon=True)
            self.read_thread.start()
        except Exception as e:
            self.txt_data.insert(tk.END, f"Connection failed: {e}\n")

    def disconnect_serial(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.serial_port = None
        self.btn_connect.config(text="Connect")
        self.btn_reconnect.config(state=tk.DISABLED)
        self.btn_pause.config(state=tk.DISABLED)
        self.txt_data.insert(tk.END, "Disconnected\n")

    def reconnect(self):
        """Reconnect to the serial port and reset the state"""
        self.disconnect_serial()  # Disconnect current connection
        self.reset_state()  # Reset the state
        self.connect_serial()  # Reconnect

    def reset_state(self):
        """Reset all states"""
        self.stop_receiving = False
        self.is_timing = False
        self.start_time = None
        self.txt_data.delete(1.0, tk.END)  # Clear the data display area
        self.lbl_time_diff.config(text="Latency (s:ms:μs): 0:000:000")  # Reset the time difference display

    def read_serial(self):
        while self.serial_port and self.serial_port.is_open and not self.stop_receiving:
            try:
                data = self.serial_port.readline().decode('utf-8').strip()
                if data:
                    self.txt_data.insert(tk.END, data + "\n")
                    self.txt_data.see(tk.END)  # Auto-scroll to the latest data
                    if not self.is_timing and "-" in data:
                        self.start_time = time.perf_counter()
                        self.is_timing = True
                        self.stop_receiving = True  # Stop receiving data after the first "-" is received
                        self.txt_data.insert(tk.END, "Timing started, stopped receiving data\n")
                        self.update_time_diff()  # Start updating the time difference
            except Exception as e:
                self.txt_data.insert(tk.END, f"Read error: {e}\n")
                break

    def format_time_diff(self, time_diff):
        """Format the time difference (in seconds) to seconds:milliseconds:microseconds"""
        seconds = int(time_diff)
        milliseconds = int((time_diff - seconds) * 1000)
        microseconds = int((time_diff - seconds - milliseconds / 1000) * 1_000_000)
        return f"{seconds}:{milliseconds:03d}:{microseconds:03d}"

    def update_time_diff(self):
        if self.is_timing:
            time_diff = time.perf_counter() - self.start_time
            formatted_time = self.format_time_diff(time_diff)
            self.lbl_time_diff.config(text=f"Latency (s:ms:μs): {formatted_time}")
            self.root.after(10, self.update_time_diff)  # Update the time difference every 10 milliseconds

    def pause_timing(self):
        if self.is_timing:
            time_diff = time.perf_counter() - self.start_time
            formatted_time = self.format_time_diff(time_diff)
            self.lbl_time_diff.config(text=f"Latency (s:ms:μs): {formatted_time}")
            self.is_timing = False
            self.txt_data.insert(tk.END, "Timing paused\n")

    def on_closing(self):
        self.disconnect_serial()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialMonitor(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
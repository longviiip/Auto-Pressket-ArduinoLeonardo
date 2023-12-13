import serial
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import keyboard
from plyer import notification

class ArduinoController:
    def __init__(self):
        self.serial_connection = None
        self.is_sending = False
        self.thread = None
        self.root = None  
        self.last_send_time = 0 
        self.interval = 0.01

    def connect(self, serial_port):
        try:
            self.serial_connection = serial.Serial(serial_port, baudrate=9600, timeout=1)
            time.sleep(2)
        except Exception as e:
            messagebox.showerror("Lỗi kết nối", f"Lỗi kết nối: {e}")

    def disconnect(self):
        if self.serial_connection:
            self.serial_connection.close()

    def send_signal(self, key):
        try:
            if self.serial_connection and self.is_sending:
                current_time = time.time()
                # Kiểm tra nếu đã đủ thời gian giữa các lần gửi tín hiệu
                if current_time - self.last_send_time >= self.interval:
                    self.serial_connection.write(key.encode())
                    self.serial_connection.flush()
                    print(f"Đã gửi tín hiệu '{key}' đến Arduino.")
                    self.last_send_time = current_time  # Cập nhật thời điểm cuối cùng gửi tín hiệu
        except Exception as e:
            print(f"Lỗi gửi tín hiệu: {e}")
        finally:
            if self.is_sending:
                # Gọi lại hàm send_signal sau một khoảng thời gian
                self.thread = threading.Timer(self.interval, self.send_signal, args=(key,))
                self.thread.start()

    def toggle_sending(self, serial_port, key, interval):
        if not self.is_sending:
            self.is_sending = True
            self.interval = interval
            self.connect(serial_port)

            # Thêm hàm chờ đợi trước khi gửi tín hiệu
            self.root.after(100, self.send_signal, key)
        else:
            self.is_sending = False
            if self.thread:
                self.thread.cancel()
            self.disconnect()

class ArduinoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Arduino Control App")

        self.arduino_controller = ArduinoController()
        self.is_sending = False

        # Create and place widgets
        self.serial_label = ttk.Label(root, text="Nhập cổng COM của Arduino:")
        self.serial_entry = ttk.Entry(root, state=tk.NORMAL)  

        self.key_label = ttk.Label(root, text="Nhập ký tự muốn gửi đến Arduino:")
        self.key_entry = ttk.Entry(root, state=tk.NORMAL)

        self.interval_label = ttk.Label(root, text="Nhập thời gian giữa các lần gửi tín hiệu (s):")
        self.interval_entry = ttk.Entry(root, state=tk.NORMAL)

        self.toggle_button = ttk.Button(root, text="Bắt đầu", command=self.toggle_sending)

        # Layout
        self.serial_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.serial_entry.grid(row=0, column=1, padx=10, pady=5)

        self.key_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.key_entry.grid(row=1, column=1, padx=10, pady=5)

        self.interval_label.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        self.interval_entry.grid(row=2, column=1, padx=10, pady=5)

        self.toggle_button.grid(row=3, column=0, columnspan=2, pady=10)

      
        keyboard.on_press_key("F1", self.on_f1_pressed)

    def toggle_sending(self):
        serial_port = self.serial_entry.get()
        key = self.key_entry.get()
        interval = self.interval_entry.get()

        if not all([serial_port, key, interval]):
            messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin.")
            return

        try:
            interval = float(interval)
        except ValueError:
            messagebox.showerror("Lỗi", "Thời gian giữa các lần gửi tín hiệu phải là một số.")
            return

        if interval <= 0:
            messagebox.showerror("Lỗi", "Thời gian giữa các lần gửi tín hiệu phải lớn hơn 0.")
            return

        if not self.is_sending:
            self.is_sending = True
            self.arduino_controller.root = self.root  # Truyền root vào controller để sử dụng after
            self.arduino_controller.toggle_sending(serial_port, key, interval)
            self.toggle_button.config(text="Dừng")

            # Chuyển trạng thái của các ô nhập thành "disabled"
            self.serial_entry["state"] = tk.DISABLED
            self.key_entry["state"] = tk.DISABLED
            self.interval_entry["state"] = tk.DISABLED
        else:
            self.is_sending = False
            self.arduino_controller.toggle_sending(serial_port, key, interval)
            self.toggle_button.config(text="Bắt đầu")

            # Chuyển trạng thái của các ô nhập thành "normal"
            self.serial_entry["state"] = tk.NORMAL
            self.key_entry["state"] = tk.NORMAL
            self.interval_entry["state"] = tk.NORMAL

    def on_f1_pressed(self, event):
      
        self.toggle_sending()

if __name__ == "__main__":
    root = tk.Tk()
    app = ArduinoApp(root)
    root.mainloop()

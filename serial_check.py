import serial
import serial.tools.list_ports

ports = serial.tools.list_ports.comports()
print("Checking COM ports...")

for port in ports:
    try:
        s = serial.Serial(port.device)
        s.close()
        print(f"{port.device} → Available")
    except (OSError, serial.SerialException):
        print(f"{port.device} → Busy")

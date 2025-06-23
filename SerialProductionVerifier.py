from ctypes import *
import os


dll_path = r"C:\SiLabs\MCU\Utilities\FLASH Programming\Dynamic DLL Build\SiUtil.dll"
libc = WinDLL(dll_path)

# Function signatures
libc.ConnectUSB.argtypes = [c_char_p, c_int, c_int, c_int]
libc.ConnectUSB.restype = c_long

libc.GetRAMMemory.argtypes = [POINTER(c_ubyte), c_ulong, c_uint]
libc.GetRAMMemory.restype = c_long

libc.GetDeviceName.argtypes = [POINTER(c_char_p)]
libc.GetDeviceName.restype = c_long

libc.USBDebugDevices.argtypes = [POINTER(c_ulong)]
libc.USBDebugDevices.restype = c_long

libc.GetUSBDeviceSN.argtypes = [c_ulong, POINTER(c_char_p)]
libc.GetUSBDeviceSN.restype = c_long

libc.GetUSBDLLVersion.argtypes = [POINTER(c_char_p)]  
libc.GetUSBDLLVersion.restype = c_long

libc.DisconnectUSB.argtypes = []
libc.DisconnectUSB.restype = c_long

libc.Connected.argtypes = []
libc.Connected.restype = c_bool

libc.GetErrorMsg.argtypes = [c_long]
libc.GetErrorMsg.restype = c_char_p

# Menu
def print_menu():
    print("\n--- SiUtil Function Menu ---")
    print("1. ConnectUSB")
    print("2. GetRAMMemory")
    print("3. GetDeviceName")
    print("4. USBDebugDevices")
    print("5. GetUSBDeviceSN")
    print("6. GetUSBDLLVersion")
    print("7. Batch Mode")
    print("8. DisconnectUSB")
    print("9. Connected")
    print("0. Exit")

# Error explanation
def explain_error(hr):
    return libc.GetErrorMsg(hr).decode(errors='ignore')

# Function definitions
def connect_usb():
    serial = b""
    result = libc.ConnectUSB(serial, 1, 1, 0)
    return result, "ConnectUSB"

def get_ram_memory(address=None, length=None):
    if address is None or length is None:
        try:
            address_hex = input("Enter the starting address (e.g., B5): ").strip()
            address = int(address_hex, 16)
        except ValueError:
            return -1, "Invalid hex address entered."
        try:
            length = int(input("Enter the number of bytes to read (1-10): ").strip())
            if not (1 <= length <= 10):
                return -1, "Length must be between 1 and 10."
        except ValueError:
            return -1, "Invalid length entered."

    buf = (c_ubyte * length)()
    result = libc.GetRAMMemory(buf, address, length)

    if result == 0:
        data = [f"0x{b:02X}" for b in buf]
        return result, f"{length} bytes read @0x{address:02X}: {' '.join(data)}"
    else:
        return result, f"GetRAMMemory failed @0x{address:02X}"

def get_device_name():
    name_ptr = c_char_p()
    result = libc.GetDeviceName(byref(name_ptr))
    if result == 0:
        return result, f"Device Name: {name_ptr.value.decode()}"
    return result, "GetDeviceName"

def usb_debug_devices():
    count = c_ulong()
    result = libc.USBDebugDevices(byref(count))
    if result == 0:
        return result, f"Connected USB Debug devices: {count.value}"
    return result, "USBDebugDevices"

def get_usb_device_sn():
    serial_ptr = c_char_p()
    result = libc.GetUSBDeviceSN(0, byref(serial_ptr))
    if result == 0:
        return result, f"Serial Number: {serial_ptr.value.decode()}"
    return result, "GetUSBDeviceSN"

def get_usb_dll_version():
    version_ptr = c_char_p()
    result = libc.GetUSBDLLVersion(byref(version_ptr))
    if result == 0:
        return result, f"DLL Version: {version_ptr.value.decode()}"
    return result, "GetUSBDLLVersion"

def disconnect_usb():
    result = libc.DisconnectUSB()
    if result == 0:
        return result, "USB connection disconnected."
    return result, "DisconnectUSB failed."

def connected():
    is_connected = libc.Connected()
    return 0, f"Connected? {'Yes' if is_connected else 'No'}"

# Function map
functions = {
    "1": connect_usb,
    "2": get_ram_memory,
    "3": get_device_name,
    "4": usb_debug_devices,
    "5": get_usb_device_sn,
    "6": get_usb_dll_version,
    "8": disconnect_usb,
    "9": connected,
}



# Main loop
while True:
    
    print_menu()
    choice = input("Enter function number: ").strip()
    if choice == "0":
        print("Exiting...")
        break
    elif choice == "7":
        sequence = input("Enter the functions to execute in order (e.g., 4-5-6): ").strip()
        steps = sequence.split("-")
        ram_params = None

        # Pre-fetch RAM parameters
        if "2" in steps:
            try:
                address_hex = input("GetRAMMemory - Enter starting address (hex): ").strip()
                address = int(address_hex, 16)
                length = int(input("GetRAMMemory - Length (1-10): ").strip())
                if not (1 <= length <= 10):
                    raise ValueError
                ram_params = (address, length)
            except ValueError:
                print(" Invalid parameters for GetRAMMemory. Batch canceled.")
                continue

        print("\nExecuting Batch:")
        for step in steps:
            func = functions.get(step)
            if func:
                try:
                    if step == "2":
                        result, output = func(*ram_params)
                    else:
                        result, output = func()
                    if result == 0:
                        print(f"[{step}]  {output}")
                    else:
                        print(f"[{step}]  Error (HRESULT: 0x{result:X}): {output}")
                        print(f"     Explanation: {explain_error(result)}")
                except Exception as e:
                    print(f"[{step}]  Exception occurred: {e}")
            else:
                print(f"[{step}]  Invalid step")
    else:
        func = functions.get(choice)
        if func:
            try:
                if choice == "2":
                    result, output = get_ram_memory()
                else:
                    result, output = func()
                if result == 0:
                    print(f" Success: {output}")
                else:
                    print(f" Error (HRESULT: 0x{result:X}): {output}")
                    print(f" Explanation: {explain_error(result)}")
            except Exception as e:
                print(f" Exception occurred: {e}")
        else:
            print("Invalid selection. Please enter a number between 0-9.")

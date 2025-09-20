import subprocess
import time

def get_paired_devices():
    """Returns a list of already paired Bluetooth devices."""
    try:
        result = subprocess.run(
            ['bluetoothctl', 'paired-devices'],
            capture_output=True, text=True, check=True
        )
        devices = []
        for line in result.stdout.strip().split('\n'):
            parts = line.split(' ', 2)
            if len(parts) == 3:
                devices.append({'mac_address': parts[1], 'name': parts[2]})
        return devices
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []

def scan_bluetooth_devices():
    """
    Scans for Bluetooth devices for a few seconds and returns a list of discovered devices.
    This is a blocking operation.
    """
    try:
        # The bluetoothctl scan process is interactive, so we run it in a specific way.
        proc = subprocess.Popen(
            ['bluetoothctl'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Start the scan, wait, get the list of devices, then stop the scan.
        proc.stdin.write("scan on\n")
        proc.stdin.flush()
        time.sleep(5) # Scan for 5 seconds
        proc.stdin.write("scan off\n")
        proc.stdin.flush()
        proc.stdin.write("devices\n")
        proc.stdin.flush()
        proc.stdin.write("quit\n")
        proc.stdin.flush()

        stdout, _ = proc.communicate(timeout=10)
        
        devices = []
        seen_macs = set()
        for line in stdout.strip().split('\n'):
            if line.startswith('Device '):
                parts = line.split(' ', 2)
                if len(parts) == 3 and parts[1] not in seen_macs:
                    devices.append({'mac_address': parts[1], 'name': parts[2]})
                    seen_macs.add(parts[1])
        return devices
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []

def pair_trust_connect_device(mac_address):
    """Pairs, trusts, and connects to a specific Bluetooth device."""
    try:
        commands = f"pair {mac_address}\ntrust {mac_address}\nconnect {mac_address}\nquit\n"
        proc = subprocess.run(
            ['bluetoothctl'],
            input=commands,
            capture_output=True,
            text=True,
            timeout=15
        )

        output = proc.stdout.lower()
        if "connection successful" in output or "pairing successful" in output:
            return (True, f"Successfully connected to device {mac_address}.")
        else:
            error = proc.stderr.strip()
            if "device already exists" in output:
                 return (True, f"Device {mac_address} is already paired/connected.")
            return (False, f"Failed to connect to {mac_address}. Details: {error or output}")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return (False, "Operation failed or bluetoothctl not found.")

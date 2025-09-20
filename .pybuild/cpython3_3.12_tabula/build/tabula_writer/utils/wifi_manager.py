import subprocess
import re

def get_current_connection():
    """Checks for the currently active Wi-Fi connection."""
    try:
        # Get all Wi-Fi devices, terse mode, only the ACTIVE and SSID fields
        result = subprocess.run(
            ['nmcli', '-t', '-f', 'ACTIVE,SSID', 'dev', 'wifi'],
            capture_output=True, text=True, check=True
        )
        for line in result.stdout.strip().split('\n'):
            parts = line.split(':')
            # The active connection will have 'yes' as the first part
            if parts[0] == 'yes' and len(parts) > 1:
                return parts[1] # Return the SSID
        return None # No active connection found
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def scan_wifi_networks():
    """Scans for available Wi-Fi networks using nmcli and returns a list of them."""
    try:
        # The command lists available Wi-Fi networks and their details.
        # --terse and --fields make the output easy to parse.
        # The 'rescan yes' argument forces a new scan.
        subprocess.run(['nmcli', 'dev', 'wifi', 'rescan'], check=True, capture_output=True)
        
        result = subprocess.run(
            ['nmcli', '--terse', '--fields', 'SSID,SIGNAL,SECURITY', 'dev', 'wifi', 'list'],
            capture_output=True, text=True, check=True
        )
        
        networks = []
        seen_ssids = set()
        for line in result.stdout.strip().split('\n'):
            # The output is colon-delimited: SSID:SIGNAL:SECURITY
            parts = line.split(':', 2)
            if len(parts) == 3 and parts[0] and parts[0] not in seen_ssids:
                networks.append({
                    'ssid': parts[0].replace('\\:', ':'), # Handle escaped colons in SSID
                    'signal': int(parts[1]),
                    'security': parts[2]
                })
                seen_ssids.add(parts[0])
        
        # Sort by signal strength, strongest first
        return sorted(networks, key=lambda x: x['signal'], reverse=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Handle cases where nmcli isn't available or fails
        return []

def connect_to_wifi(ssid, password=None):
    """Connects to a Wi-Fi network using nmcli."""
    try:
        command = ['nmcli', 'dev', 'wifi', 'connect', ssid]
        if password:
            command.extend(['password', password])
        
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            return (True, f"Successfully connected to {ssid}")
        else:
            # Try to find a more specific error message from nmcli's output
            error_message = result.stderr.strip()
            if 'Error:' in error_message:
                error_message = error_message.split('Error:')[1].strip()
            return (False, f"Failed to connect: {error_message}")
    except FileNotFoundError:
        return (False, "nmcli command not found. Please ensure NetworkManager is installed.")

import subprocess
import json
from datetime import datetime

def scan_network():
    results = {
        "timestamp": datetime.now().isoformat(),
        "interfaces": {},
        "vpn_active": False,
        "issues": []
    }
    
    # Get interfaces using ip command
    result = subprocess.run(["ip", "addr", "show"], capture_output=True, text=True)
    lines = result.stdout.split('\n')
    
    current_iface = None
    for line in lines:
        if ': ' in line and 'LOOPBACK' not in line:
            parts = line.split(': ')
            if len(parts) >= 2:
                current_iface = parts[1].split('@')[0]
                results["interfaces"][current_iface] = {"status": "UP", "ip": "unknown"}
        elif 'inet ' in line and current_iface:
            ip = line.split('inet ')[1].split('/')[0]
            results["interfaces"][current_iface]["ip"] = ip
    
    # Add loopback
    results["interfaces"]["lo"] = {"status": "UP", "ip": "127.0.0.1"}
    
    # Check for VPN
    tun_check = subprocess.run(["ip", "link", "show", "tun0"], capture_output=True, text=True)
    wg_check = subprocess.run(["ip", "link", "show", "wg0"], capture_output=True, text=True)
    
    if tun_check.returncode == 0 or wg_check.returncode == 0:
        results["vpn_active"] = True
    else:
        results["issues"].append({
            "type": "vpn_down",
            "detail": "No active VPN interface detected",
            "impact": "Tools targeting VPN ranges will fail",
            "fix": "Connect to VPN: sudo openvpn your_config.ovpn"
        })
    
    return results

if __name__ == "__main__":
    print(json.dumps(scan_network(), indent=2))

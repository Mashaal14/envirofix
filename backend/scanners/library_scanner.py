import subprocess
import json
from datetime import datetime

CRITICAL_LIBS = ["libssl", "libpcap", "libc", "libpython3"]

def scan_libraries():
    results = {
        "timestamp": datetime.now().isoformat(),
        "libraries": {},
        "issues": []
    }

    ldconfig = subprocess.run(
        ["ldconfig", "-p"],
        capture_output=True, text=True
    )

    for lib in CRITICAL_LIBS:
        results["libraries"][lib] = []
        for line in ldconfig.stdout.splitlines():
            if lib in line.lower():
                results["libraries"][lib].append(line.strip())

    for lib in CRITICAL_LIBS:
        dpkg_out = subprocess.run(
            ["dpkg", "-l", f"{lib}*"],
            capture_output=True, text=True
        )
        for line in dpkg_out.stdout.splitlines():
            if line.startswith("ii"):
                parts = line.split()
                if len(parts) >= 3:
                    name    = parts[1]
                    version = parts[2]
                    results["libraries"][f"{name}_version"] = version

    return results

if __name__ == "__main__":
    print(json.dumps(scan_libraries(), indent=2))
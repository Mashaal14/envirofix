import subprocess
import json
from datetime import datetime

def scan_apt():
    results = {
        "timestamp": datetime.now().isoformat(),
        "broken_packages": [],
        "held_packages": [],
        "apt_errors": [],
        "total_installed": 0
    }

    out = subprocess.run(
        ["dpkg", "--get-selections"],
        capture_output=True, text=True
    )
    for line in out.stdout.splitlines():
        parts = line.split()
        if len(parts) == 2:
            if parts[1] == "deinstall":
                results["broken_packages"].append(parts[0])
            elif parts[1] == "hold":
                results["held_packages"].append(parts[0])
            elif parts[1] == "install":
                results["total_installed"] += 1

    apt_check = subprocess.run(
        ["apt-get", "--dry-run", "update"],
        capture_output=True, text=True
    )
    stderr = apt_check.stderr.lower()
    stdout = apt_check.stdout.lower()
    if "error" in stderr or "err:" in stdout or "no_pubkey" in stderr:
        results["apt_errors"].append(apt_check.stderr[:500])

    return results

if __name__ == "__main__":
    print(json.dumps(scan_apt(), indent=2))
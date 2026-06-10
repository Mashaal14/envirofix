import subprocess
import json
from datetime import datetime

def scan_kernel():
    results = {
        "kernel_version": "",
        "kernel_headers_installed": False,
        "dkms_installed": False,
        "issues": []
    }
    
    # Get kernel version
    uname = subprocess.run(["uname", "-r"], capture_output=True, text=True)
    kernel = uname.stdout.strip()
    results["kernel_version"] = kernel
    
    # Check if exact header package is installed
    exact_pkg = f"linux-headers-{kernel}"
    check_exact = subprocess.run(["dpkg", "-s", exact_pkg], capture_output=True, text=True)
    # Check metapackage
    meta_pkg = "linux-headers-amd64"
    check_meta = subprocess.run(["dpkg", "-s", meta_pkg], capture_output=True, text=True)
    
    if check_exact.returncode == 0 or check_meta.returncode == 0:
        results["kernel_headers_installed"] = True
    else:
        results["kernel_headers_installed"] = False
        results["issues"].append({
            "type": "missing_headers",
            "detail": f"Kernel headers for {kernel} are not installed.",
            "fix": f"sudo apt install {exact_pkg}"
        })
    
    # Check DKMS
    dkms = subprocess.run(["which", "dkms"], capture_output=True, text=True)
    results["dkms_installed"] = dkms.returncode == 0
    
    return results

if __name__ == "__main__":
    print(json.dumps(scan_kernel(), indent=2))

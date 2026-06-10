import subprocess
import json
import re
from datetime import datetime

def get_upgradable_count():
    """Return number of upgradable packages"""
    result = subprocess.run(["apt", "list", "--upgradable", "2>/dev/null"], 
                            shell=True, capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')
    # First line is header, count rest
    count = len([l for l in lines if l and not l.startswith("Listing")])
    return count

def get_broken_dependencies():
    result = subprocess.run(["apt", "--fix-broken", "install", "-s"],
                            capture_output=True, text=True)
    if "Unmet dependencies" in result.stderr or "Depends:" in result.stderr:
        return {"has_broken": True, "details": result.stderr[:500]}
    return {"has_broken": False}

def get_version_conflicts():
    packages = ["libfdisk1", "libblkid1", "libuuid1", "util-linux", "mount"]
    versions = {}
    for pkg in packages:
        r = subprocess.run(["dpkg", "-l", pkg], capture_output=True, text=True)
        for line in r.stdout.split('\n'):
            if line.startswith('ii'):
                parts = line.split()
                if len(parts) >= 3:
                    versions[pkg] = parts[2]
    conflicts = []
    if versions:
        first = next(iter(versions.values()))
        for pkg, ver in versions.items():
            if ver != first:
                conflicts.append({"package": pkg, "version": ver, "expected": first})
    return conflicts

def get_kernel_info():
    kernel = subprocess.run(["uname", "-r"], capture_output=True, text=True).stdout.strip()
    headers_check = subprocess.run(["dpkg", "-l", f"linux-headers-{kernel}"], capture_output=True, text=True)
    headers_installed = "ii" in headers_check.stdout
    if not headers_installed:
        meta_check = subprocess.run(["dpkg", "-l", "linux-headers-amd64"], capture_output=True, text=True)
        headers_installed = "ii" in meta_check.stdout
    return {"version": kernel, "headers_installed": headers_installed}

def full_system_scan():
    upgradable = get_upgradable_count()
    broken = get_broken_dependencies()
    conflicts = get_version_conflicts()
    kernel = get_kernel_info()

    issues = []
    if broken["has_broken"]:
        issues.append({
            "severity": "critical",
            "title": "Broken Dependencies",
            "detail": "Package dependency conflicts detected.",
            "tool": "apt",
            "fix": "sudo apt --fix-broken install -y"
        })
    if conflicts:
        issues.append({
            "severity": "critical",
            "title": "Version Conflicts",
            "detail": f"Version mismatches: {conflicts}",
            "tool": "apt",
            "fix": "sudo apt --fix-broken install -y"
        })
    if not kernel["headers_installed"]:
        issues.append({
            "severity": "warning",
            "title": "Kernel Headers Missing",
            "detail": f"Headers for {kernel['version']} not found.",
            "tool": "kernel",
            "fix": f"sudo apt install linux-headers-{kernel['version']}"
        })
    if upgradable > 0:
        issues.append({
            "severity": "warning",
            "title": "Packages Outdated",
            "detail": f"{upgradable} package(s) can be upgraded.",
            "tool": "apt",
            "fix": "sudo apt update && sudo apt upgrade -y"
        })

    return {
        "timestamp": datetime.now().isoformat(),
        "kernel": kernel,
        "broken_dependencies": broken,
        "version_conflicts": conflicts,
        "upgradable_count": upgradable,
        "issues": issues
    }

if __name__ == "__main__":
    print(json.dumps(full_system_scan(), indent=2))

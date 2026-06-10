import subprocess
import json
import re

def analyze_dependency_issues():
    """Detect broken dependencies and version mismatches"""
    issues = []
    
    # Run apt --fix-broken install simulation
    result = subprocess.run(
        ["apt", "--fix-broken", "install", "-s"],
        capture_output=True, text=True
    )
    
    if "Depends:" in result.stderr or "Unmet dependencies" in result.stderr:
        issues.append({
            "type": "broken_dependencies",
            "detail": "Package dependency conflicts detected",
            "severity": "critical",
            "fix": "sudo apt --fix-broken install -y",
            "output": result.stderr[:500]
        })
    
    return issues

def get_package_conflicts():
    """Check for package version conflicts"""
    result = subprocess.run(
        ["dpkg", "-l"],
        capture_output=True, text=True
    )
    
    packages = {}
    conflicts = []
    
    for line in result.stdout.split('\n'):
        if line.startswith('ii '):
            parts = line.split()
            if len(parts) >= 3:
                name = parts[1]
                version = parts[2]
                packages[name] = version
    
    # Check for common conflicts
    check_pairs = [
        ('libfdisk1', 'libblkid1'),
        ('libuuid1', 'util-linux'),
        ('mount', 'util-linux')
    ]
    
    for p1, p2 in check_pairs:
        if p1 in packages and p2 in packages:
            v1 = packages[p1]
            v2 = packages[p2]
            if v1 != v2:
                conflicts.append({
                    "package1": p1,
                    "version1": v1,
                    "package2": p2,
                    "version2": v2,
                    "severity": "critical",
                    "fix": "sudo apt --fix-broken install -y"
                })
    
    return conflicts

def analyze_system_state():
    """Complete system analysis"""
    return {
        "kernel": get_kernel_info(),
        "dependencies": get_package_conflicts(),
        "broken_packages": analyze_dependency_issues(),
        "suggested_fixes": generate_fixes()
    }

def get_kernel_info():
    kernel = subprocess.run(["uname", "-r"], capture_output=True, text=True).stdout.strip()
    return {"version": kernel, "headers_installed": check_headers(kernel)}

def check_headers(kernel):
    result = subprocess.run(["dpkg", "-l", f"linux-headers-{kernel}"], capture_output=True, text=True)
    return "ii" in result.stdout

def generate_fixes():
    return [
        "sudo apt --fix-broken install -y",
        "sudo apt update && sudo apt upgrade -y",
        "sudo apt autoremove -y"
    ]

if __name__ == "__main__":
    print(json.dumps(analyze_system_state(), indent=2))

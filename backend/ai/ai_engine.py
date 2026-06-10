import subprocess
import json
import requests
import sys
import re
from datetime import datetime

OLLAMA_URL = "http://host.docker.internal:11434/api/generate"
MODEL_NAME = "deepseek-r1:8b"

def get_actual_kernel_headers_package():
    """Get the ACTUAL available headers package from the system"""
    kernel = subprocess.run(["uname", "-r"], capture_output=True, text=True).stdout.strip()
    
    # Run apt-cache search to find available headers
    result = subprocess.run(
        ["apt-cache", "search", "linux-headers"],
        capture_output=True, text=True
    )
    
    available = []
    for line in result.stdout.split('\n'):
        if 'linux-headers' in line:
            parts = line.split()
            if parts:
                available.append(parts[0])
    
    # Look for specific matches
    for pkg in available:
        if 'amd64' in pkg and 'linux-headers' in pkg:
            if kernel.replace('+', '-') in pkg or kernel.split('+')[0] in pkg:
                return pkg
    
    # Fallback to metapackage
    if 'linux-headers-amd64' in available:
        return 'linux-headers-amd64'
    
    # Return first available
    return available[0] if available else 'linux-headers-amd64'

def analyse_issue(issue_data):
    """Analyze issue using REAL system data"""
    
    # Extract issue text
    if isinstance(issue_data, dict):
        issue_text = issue_data.get('issue', '')
        tool = issue_data.get('tool', 'general')
    else:
        issue_text = str(issue_data)
        tool = 'general'
    
    # Get REAL system information
    kernel_version = subprocess.run(["uname", "-r"], capture_output=True, text=True).stdout.strip()
    actual_package = get_actual_kernel_headers_package()
    
    # Check if headers are installed
    headers_check = subprocess.run(
        ["dpkg", "-l", actual_package],
        capture_output=True, text=True
    )
    headers_installed = "ii" in headers_check.stdout
    
    # For kernel header issues, provide direct fix without waiting for AI
    if "header" in issue_text.lower() or tool == "kernel":
        return {
            "severity": "warning",
            "root_cause": f"Kernel headers for version {kernel_version} are missing or not installed.",
            "affected_components": ["DKMS modules", "VirtualBox", "VMware tools", "Wireless drivers"],
            "fix_steps": [
                "sudo apt update",
                f"sudo apt install -y {actual_package}"
            ],
            "explanation": f"Your system is running kernel {kernel_version}. The header files needed for compiling kernel modules are not installed. On Kali Linux, the correct package is {actual_package}.",
            "risk_level": "Safe",
            "teaches": "Kernel headers provide the API for compiling kernel modules. Always check available packages with 'apt search linux-headers' as the exact package name may differ from the kernel version.",
            "confidence": "high"
        }
    
    # For other issues, try DeepSeek-R1
    try:
        prompt = f"""Analyze this Kali Linux issue and provide a fix.

REAL SYSTEM DATA:
- Kernel: {kernel_version}
- Available headers package: {actual_package}

ISSUE: {issue_text}
TOOL: {tool}

Return ONLY valid JSON with these fields:
- severity (critical/warning/info)
- root_cause (technical explanation)
- affected_components (array)
- fix_steps (array of actual commands)
- explanation (simple explanation)
- risk_level (Safe/Caution/Hold)
- teaches (educational message)
- confidence (high/medium/low)"""

        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.3, "num_predict": 1500}
        }
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=90)
        if response.status_code == 200:
            ai_text = response.json().get('response', '')
            # Extract JSON
            json_match = re.search(r'\{.*\}', ai_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result
    except Exception as e:
        print(f"AI error: {e}")
    
    # Fallback response
    return {
        "severity": "info",
        "root_cause": f"Unable to analyze with AI. Issue: {issue_text}",
        "affected_components": ["System"],
        "fix_steps": ["Check system logs for details"],
        "explanation": "AI analysis temporarily unavailable",
        "risk_level": "Caution",
        "teaches": "System maintenance is important for stability",
        "confidence": "low"
    }

def warmup_model():
    """Warm up the model"""
    try:
        payload = {"model": MODEL_NAME, "prompt": "Hello", "stream": False}
        requests.post(OLLAMA_URL, json=payload, timeout=30)
        print("✅ DeepSeek-R1 warmed up")
        return True
    except Exception as e:
        print(f"⚠️ Warmup failed: {e}")
        return False

if __name__ == "__main__":
    test = {"issue": "Missing kernel headers", "tool": "kernel"}
    result = analyse_issue(test)
    print(json.dumps(result, indent=2))

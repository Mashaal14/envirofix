from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import subprocess
import json
from scanners.system_scanner import full_system_scan

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/system/scan")
def system_scan():
    return full_system_scan()

@app.get("/alerts")
def get_alerts():
    scan = full_system_scan()
    alerts = []
    for i, issue in enumerate(scan.get("issues", [])):
        alerts.append({
            "id": i+1,
            "severity": issue["severity"],
            "title": issue["title"],
            "detail": issue["detail"],
            "tool": issue["tool"],
            "fix": issue["fix"],
            "risk_level": "Hold" if issue["severity"] == "critical" else "Caution",
            "created_at": scan["timestamp"]
        })
    return alerts

@app.get("/system")
def get_system():
    scan = full_system_scan()
    return {
        "kernel": scan["kernel"],
        "broken_dependencies": scan["broken_dependencies"]["has_broken"],
        "upgradable": scan["upgradable_count"],
        "total_issues": len(scan["issues"])
    }

@app.post("/scan-and-alert")
def scan_and_alert():
    scan = full_system_scan()
    return {"status": "success", "alerts_created": len(scan["issues"]), "upgradable": scan["upgradable_count"]}

@app.post("/analyse")
def analyse(issue: dict):
    # Get the latest full scan
    scan = full_system_scan()
    prompt = f"""You are EnviroFix, an expert Kali Linux diagnostic AI.

REAL SYSTEM STATE:
{json.dumps(scan, indent=2)}

USER ISSUE: {issue.get('issue', '')}
TOOL: {issue.get('tool', 'system')}

Based on the actual system data, provide a precise diagnosis and fix steps.
Return JSON with: severity, root_cause, affected_components, fix_steps, explanation, risk_level, teaches, confidence.
If there are upgradable packages, recommend 'sudo apt update && sudo apt upgrade -y'.
If broken dependencies, recommend 'sudo apt --fix-broken install -y'.
Do NOT guess.
"""
    try:
        import requests
        resp = requests.post("http://host.docker.internal:11434/api/generate",
                             json={"model": "deepseek-r1:8b", "prompt": prompt, "stream": False},
                             timeout=90)
        if resp.status_code == 200:
            text = resp.json().get("response", "")
            import re
            m = re.search(r'\{.*\}', text, re.DOTALL)
            if m:
                return json.loads(m.group())
    except Exception as e:
        print("AI error:", e)
    # Fallback using real data
    if scan["upgradable_count"] > 0:
        return {
            "severity": "warning",
            "root_cause": f"{scan['upgradable_count']} packages are outdated.",
            "affected_components": ["system packages"],
            "fix_steps": ["sudo apt update", "sudo apt upgrade -y"],
            "explanation": "Keeping packages updated prevents security issues and bugs.",
            "risk_level": "Safe",
            "teaches": "Regular updates maintain system health.",
            "confidence": "high"
        }
    if not scan["kernel"]["headers_installed"]:
        return {
            "severity": "warning",
            "root_cause": "Kernel headers missing.",
            "affected_components": ["DKMS", "kernel modules"],
            "fix_steps": [f"sudo apt install linux-headers-{scan['kernel']['version']}"],
            "explanation": "Headers are needed for compiling kernel modules.",
            "risk_level": "Caution",
            "teaches": "Install headers to enable DKMS.",
            "confidence": "high"
        }
    return {
        "severity": "info",
        "root_cause": "System appears healthy.",
        "affected_components": [],
        "fix_steps": ["sudo apt update"],
        "explanation": "No critical issues found.",
        "risk_level": "Safe",
        "teaches": "Continue regular maintenance.",
        "confidence": "high"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7070)

@app.get("/upgradable-packages")
def get_upgradable_packages():
    """Get list of upgradable packages"""
    import subprocess
    result = subprocess.run(["apt", "list", "--upgradable", "2>/dev/null"], 
                            shell=True, capture_output=True, text=True)
    packages = []
    lines = result.stdout.strip().split('\n')
    for line in lines[1:]:  # Skip header
        if line and '/' in line:
            pkg_name = line.split('/')[0].strip()
            packages.append(pkg_name)
    return packages[:50]  # Return first 50 packages

@app.get("/upgradable-packages")
def get_upgradable_packages():
    """Get list of upgradable packages"""
    import subprocess
    result = subprocess.run(["apt", "list", "--upgradable", "2>/dev/null"], 
                            shell=True, capture_output=True, text=True)
    packages = []
    lines = result.stdout.strip().split('\n')
    for line in lines[1:]:  # Skip header
        if line and '/' in line:
            pkg_name = line.split('/')[0].strip()
            packages.append(pkg_name)
    return packages[:50]  # Return first 50 packages

@app.post("/analyse")
def analyse(issue: dict):
    """Enhanced AI analysis using real system state"""
    from scanners.system_scanner import full_system_scan
    import requests, json, re
    
    # Get real system state
    system_state = full_system_scan()
    
    # Build prompt with actual data
    prompt = f"""You are EnviroFix, an expert Kali Linux diagnostician.

REAL SYSTEM STATE (from live scan):
{json.dumps(system_state, indent=2)}

USER REPORTED ISSUE: {issue.get('issue', '')}
TOOL: {issue.get('tool', 'system')}

Based ONLY on the actual system data above, provide:
- severity (critical/warning/info)
- root_cause (exact problem from the data)
- affected_components (list)
- fix_steps (commands that will actually solve it)
- explanation (simple)
- risk_level (Safe/Caution/Hold)
- teaches (educational message)
- confidence (high/medium/low)

If there are no real issues, respond with severity=info and explain system is healthy.
Do NOT hallucinate. Use the provided data.
"""
    try:
        resp = requests.post("http://host.docker.internal:11434/api/generate",
                             json={"model": "deepseek-r1:8b", "prompt": prompt, "stream": False},
                             timeout=90)
        if resp.status_code == 200:
            text = resp.json().get("response", "")
            m = re.search(r'\{.*\}', text, re.DOTALL)
            if m:
                return json.loads(m.group())
    except Exception as e:
        print("AI error:", e)
    
    # Fallback based on real system state
    if system_state["kernel"]["headers_installed"] is False:
        return {
            "severity": "warning",
            "root_cause": f"Kernel headers for {system_state['kernel']['version']} are missing.",
            "affected_components": ["DKMS", "kernel modules"],
            "fix_steps": [f"sudo apt install linux-headers-{system_state['kernel']['version'].split('+')[0]}"],
            "explanation": "Kernel headers are needed to compile kernel modules.",
            "risk_level": "Caution",
            "teaches": "Install headers to enable DKMS and out-of-tree modules.",
            "confidence": "high"
        }
    if system_state["upgradable_count"] > 0:
        return {
            "severity": "warning",
            "root_cause": f"{system_state['upgradable_count']} packages are outdated.",
            "affected_components": ["system packages"],
            "fix_steps": ["sudo apt update", "sudo apt upgrade -y"],
            "explanation": "Keeping packages updated prevents security issues.",
            "risk_level": "Safe",
            "teaches": "Regular updates maintain system health.",
            "confidence": "high"
        }
    return {
        "severity": "info",
        "root_cause": "System appears healthy.",
        "affected_components": [],
        "fix_steps": ["sudo apt update"],
        "explanation": "No critical issues found.",
        "risk_level": "Safe",
        "teaches": "Continue regular maintenance.",
        "confidence": "high"
    }

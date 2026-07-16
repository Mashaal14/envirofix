from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
import subprocess
import json
from scanners.system_scanner import full_system_scan

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Mock AI mode: skip the Ollama/deepseek-r1 call (which needs ~16GB+ RAM) and go
# straight to the rule-based fallback below, using real scan data. Set USE_OLLAMA=false
# for low-resource deployments (e.g. small cloud instances without a local LLM).
USE_OLLAMA = os.getenv("USE_OLLAMA", "true").lower() == "true"

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

    if USE_OLLAMA:
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
    # Fallback using real data (this is also what mock mode returns directly)
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7070)

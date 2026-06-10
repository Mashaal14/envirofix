from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from scanners.kernel_scanner import scan_kernel
from scanners.network_scanner import scan_network
from scanners.apt_scanner import scan_apt
from scanners.gpg_scanner import scan_gpg
from scanners.library_scanner import scan_libraries

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/scan")
def scan():
    kernel = scan_kernel()
    network = scan_network()
    apt = scan_apt()
    gpg = scan_gpg()
    libs = scan_libraries()
    total_issues = (len(kernel.get("issues", [])) + len(network.get("issues", [])) +
                    len(apt.get("broken_packages", [])) + len(gpg.get("expired_keys", [])) +
                    len(libs.get("issues", [])))
    return {
        "summary": {"total_issues": total_issues, "status": "issues_found" if total_issues > 0 else "healthy"},
        "kernel": kernel,
        "network": network,
        "apt": apt,
        "gpg": gpg,
        "libraries": libs
    }

@app.get("/alerts")
def alerts():
    kernel = scan_kernel()
    alerts_list = []
    for i, issue in enumerate(kernel.get("issues", [])):
        alerts_list.append({
            "id": i+1,
            "severity": "warning",
            "title": "Kernel Issue",
            "detail": issue if isinstance(issue, str) else issue.get("detail", str(issue)),
            "tool": "kernel",
            "fix": "sudo apt install linux-headers-$(uname -r)",
            "risk_level": "Caution",
            "created_at": datetime.now().isoformat()
        })
    return alerts_list

@app.get("/system")
def system():
    return {"kernel": scan_kernel(), "network": scan_network()}

@app.get("/history")
def history():
    return []

@app.get("/rag/status")
def rag_status():
    return {"indexed_chunks": 120, "last_scrape": datetime.now().isoformat()}

@app.post("/analyse")
def analyse(issue: dict):
    return {
        "severity": "warning",
        "root_cause": "Kernel headers missing for your running kernel.",
        "fix_steps": ["sudo apt update", "sudo apt install linux-headers-$(uname -r)"],
        "confidence": "high"
    }

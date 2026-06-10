import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scanners.apt_scanner     import scan_apt
from scanners.gpg_scanner     import scan_gpg
from scanners.kernel_scanner  import scan_kernel
from scanners.library_scanner import scan_libraries
from scanners.network_scanner import scan_network
from db.database              import init_db, SessionLocal, ScanResult
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
##from ai.scraper import run_full_scrape

scheduler = BackgroundScheduler()
#scheduler.add_job(run_full_scrape, 'interval', hours=6)
scheduler.start()

from ai.ai_engine import warmup_model
warmup_model()  # ensure model is in RAM before scan begins

def run_full_scan():
    print("EnviroFix — running full system scan...")

    report = {
        "scan_time": datetime.now().isoformat(),
        "apt":       scan_apt(),
        "gpg":       scan_gpg(),
        "kernel":    scan_kernel(),
        "libraries": scan_libraries(),
        "network":   scan_network()
    }

    total_issues = (
        len(report["apt"]["apt_errors"])      +
        len(report["apt"]["broken_packages"]) +
        len(report["gpg"]["missing_keys"])    +
        len(report["gpg"]["expired_keys"])    +
        len(report["kernel"]["issues"])       +
        len(report["network"]["issues"])
    )

    report["summary"] = {
        "total_issues": total_issues,
        "status": "healthy" if total_issues == 0 else "issues_found"
    }

    init_db()
    db = SessionLocal()
    db.add(ScanResult(
        scan_type = "full",
        status    = report["summary"]["status"],
        data      = json.dumps(report)
    ))
    db.commit()
    db.close()

    print(f"Scan complete — issues found: {total_issues}")
    return report

if __name__ == "__main__":
    result = run_full_scan()
    print(json.dumps(result, indent=2))
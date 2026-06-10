#!/usr/bin/env python3
"""
EnviroFix Background Daemon - Runs silently, sends desktop notifications
"""

import time
import subprocess
import json
import os
from datetime import datetime
from pathlib import Path

# Configuration
CHECK_INTERVAL = 300  # 5 minutes (user can change)
NOTIFICATION_ENABLED = True

def send_notification(title, message, urgency="normal"):
    """Send desktop notification on Linux"""
    try:
        subprocess.run([
            "notify-send",
            "--icon=" + str(Path(__file__).parent / "icon.png"),
            "--urgency", urgency,
            "--expire-time", "10000",  # 10 seconds
            title,
            message
        ], check=False)
    except:
        pass  # Silent fail if no desktop environment

def check_system_health():
    """Run scan and return issues"""
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:7070/scan"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data.get("summary", {}).get("total_issues", 0), data
        return 0, {}
    except:
        return 0, {}

def get_ai_fix_commands(issue):
    """Get AI-generated fix for an issue"""
    try:
        result = subprocess.run(
            ["curl", "-s", "-X", "POST", "http://localhost:7070/analyse",
             "-H", "Content-Type: application/json",
             "-d", json.dumps({"issue": issue, "auto_detected": True})],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return {}
    except:
        return {}

def main():
    print("🔍 EnviroFix Background Daemon Starting...")
    print(f"⏱️  Checking every {CHECK_INTERVAL // 60} minutes")
    print("📢 Desktop notifications enabled")
    
    last_issue_count = 0
    
    while True:
        try:
            issue_count, scan_data = check_system_health()
            
            if issue_count > 0 and issue_count != last_issue_count:
                # New issues detected!
                issues = []
                
                # Collect issues from scan
                kernel_issues = scan_data.get("kernel", {}).get("issues", [])
                network_issues = scan_data.get("network", {}).get("issues", [])
                
                for issue in kernel_issues + network_issues:
                    if isinstance(issue, dict):
                        issue_text = issue.get("detail", str(issue))
                    else:
                        issue_text = str(issue)
                    issues.append(issue_text)
                
                # Send notification
                if NOTIFICATION_ENABLED and issues:
                    title = f"⚠️ EnviroFix: {issue_count} Issue(s) Detected"
                    message = issues[0][:100] + ("..." if len(issues[0]) > 100 else "")
                    send_notification(title, message, "critical")
                    
                    # Also create clickable alert file for dashboard
                    alert_file = Path("/tmp/envirofix_last_alert.json")
                    alert_file.write_text(json.dumps({
                        "timestamp": datetime.now().isoformat(),
                        "issues": issues,
                        "scan_data": scan_data
                    }))
                
                last_issue_count = issue_count
            
            elif issue_count == 0 and last_issue_count > 0:
                # Issues resolved
                send_notification("✅ EnviroFix", "All issues have been resolved!", "normal")
                last_issue_count = 0
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n👋 EnviroFix daemon stopped")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()

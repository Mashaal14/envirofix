#!/usr/bin/env python3
import subprocess

def send_notification(title, message):
    """Send desktop notification"""
    try:
        subprocess.run([
            "notify-send",
            "--urgency", "critical",
            "--expire-time", "5000",
            title,
            message
        ])
        print(f"✅ Notification sent: {title}")
    except Exception as e:
        print(f"❌ Failed to send: {e}")

# Test notification
send_notification("🔔 EnviroFix Alert", "Kernel headers missing! Click to fix at http://localhost:3000")

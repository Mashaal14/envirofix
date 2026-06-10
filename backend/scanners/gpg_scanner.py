import subprocess
import json
import shutil
from datetime import datetime, timedelta


def scan_gpg() -> dict:
    results = {
        "timestamp":      datetime.now().isoformat(),
        "valid_keys":     [],
        "expired_keys":   [],
        "expiring_soon":  [],
        "missing_keys":   [],
        "predictions":    [],   # NEW — predictive warnings
        "summary": {
            "total_valid":   0,
            "total_expired": 0,
            "total_missing": 0,
            "health":        "healthy"
        }
    }

    # ── 1. CHECK FOR MISSING KEYS VIA APT DRY-RUN ──────────
    try:
        apt_out = subprocess.run(
            ["apt-get", "--dry-run", "update"],
            capture_output=True, text=True, timeout=60
        )
        for line in apt_out.stderr.splitlines():
            if "NO_PUBKEY" in line or "no_pubkey" in line.lower():
                key = line.strip().split()[-1]
                results["missing_keys"].append({
                    "key_id": key,
                    "severity": "critical",
                    "fix": (
                        f"sudo apt-key adv --keyserver keyserver.ubuntu.com "
                        f"--recv-keys {key}"
                    ),
                    "alternative_fix": (
                        f"sudo gpg --keyserver hkp://keyserver.ubuntu.com:80 "
                        f"--recv-keys {key} && "
                        f"sudo gpg --export {key} | sudo apt-key add -"
                    ),
                    "impact": (
                        "APT cannot verify packages from this repository. "
                        "Updates and installs from this source are blocked."
                    )
                })
    except subprocess.TimeoutExpired:
        results["missing_keys"].append({
            "key_id": "unknown",
            "severity": "warning",
            "fix": "apt-get update timed out — check network connectivity",
            "impact": "Could not verify GPG key status"
        })
    except FileNotFoundError:
        pass  # apt-get not available in this environment

    # ── 2. CHECK INSTALLED GPG KEYS WITH EXPIRY DATES ───────
    if not shutil.which("gpg"):
        results["predictions"].append({
            "type":       "environment_warning",
            "title":      "gpg not installed",
            "severity":   "warning",
            "action":     "sudo apt install gnupg",
            "urgency":    "Medium"
        })
        _finalise_summary(results)
        return results

    try:
        key_out = subprocess.run(
            ["gpg", "--list-keys", "--with-colons"],
            capture_output=True, text=True, timeout=30
        )
        _parse_gpg_colons(key_out.stdout, results)
    except subprocess.TimeoutExpired:
        # Fall back to plain --list-keys
        try:
            key_out = subprocess.run(
                ["gpg", "--list-keys"],
                capture_output=True, text=True, timeout=30
            )
            _parse_gpg_plain(key_out.stdout, results)
        except Exception:
            pass
    except FileNotFoundError:
        pass

    # ── 3. APT KEYRING (SYSTEM-LEVEL KEYS) ──────────────────
    try:
        apt_key_out = subprocess.run(
            ["apt-key", "list"],
            capture_output=True, text=True, timeout=20
        )
        _parse_apt_keyring(apt_key_out.stdout, results)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    _finalise_summary(results)
    return results


# ── PARSER: GPG --WITH-COLONS FORMAT ────────────────────────
def _parse_gpg_colons(output: str, results: dict):
    """
    Parse the machine-readable colon-delimited gpg output.
    Field 7 is the expiry timestamp (Unix epoch or empty).
    """
    now = datetime.now()

    for line in output.splitlines():
        parts = line.split(":")
        if len(parts) < 10:
            continue

        record_type = parts[0]   # pub, sub, uid, etc.
        validity    = parts[1]   # e=expired, r=revoked, u=ultimate, etc.
        key_id      = parts[4] if len(parts) > 4 else "unknown"
        created_ts  = parts[5] if len(parts) > 5 else ""
        expires_ts  = parts[6] if len(parts) > 6 else ""

        if record_type not in ("pub", "sub"):
            continue

        # Build base key entry
        key_entry = {
            "key_id":     key_id,
            "type":       record_type,
            "validity":   validity,
            "created":    _ts_to_iso(created_ts),
            "expires":    _ts_to_iso(expires_ts) if expires_ts else "never",
        }

        if validity == "e":
            # Already expired
            key_entry["severity"] = "critical"
            key_entry["fix"] = (
                f"sudo apt-key adv --keyserver keyserver.ubuntu.com "
                f"--refresh-keys {key_id}"
            )
            key_entry["impact"] = (
                "Expired key — packages signed with this key cannot be "
                "verified. Repository updates will fail."
            )
            results["expired_keys"].append(key_entry)

        elif expires_ts and expires_ts.isdigit():
            expires_dt  = datetime.fromtimestamp(int(expires_ts))
            days_left   = (expires_dt - now).days

            if days_left <= 0:
                # Expired but gpg not marking it as 'e' yet
                key_entry["severity"]      = "critical"
                key_entry["days_left"]     = 0
                key_entry["expires_date"]  = expires_dt.strftime("%Y-%m-%d")
                key_entry["fix"]           = (
                    f"sudo apt-key adv --keyserver keyserver.ubuntu.com "
                    f"--refresh-keys {key_id}"
                )
                results["expired_keys"].append(key_entry)

            elif days_left <= 7:
                # CRITICAL — expires this week
                key_entry.update(_expiry_warning(key_id, days_left, expires_dt, "critical"))
                results["expiring_soon"].append(key_entry)
                results["predictions"].append({
                    "type":                 "key_expiry_imminent",
                    "title":                f"GPG key expires in {days_left} day(s)",
                    "key_id":               key_id,
                    "severity":             "critical",
                    "predicted_failure":    expires_dt.isoformat(),
                    "action":               f"sudo apt-key adv --keyserver keyserver.ubuntu.com --refresh-keys {key_id}",
                    "urgency":              "Critical — act today",
                    "impact":               "All repository updates will fail when key expires"
                })

            elif days_left <= 14:
                # WARNING — expires within 2 weeks
                key_entry.update(_expiry_warning(key_id, days_left, expires_dt, "warning"))
                results["expiring_soon"].append(key_entry)
                results["predictions"].append({
                    "type":              "key_expiry_soon",
                    "title":             f"GPG key expires in {days_left} days",
                    "key_id":            key_id,
                    "severity":          "warning",
                    "predicted_failure": expires_dt.isoformat(),
                    "action":            f"sudo apt-key adv --keyserver keyserver.ubuntu.com --refresh-keys {key_id}",
                    "urgency":           "High — renew within 7 days",
                    "impact":            "Repository access will break on expiry date"
                })

            elif days_left <= 30:
                # INFO — expires within a month
                key_entry.update(_expiry_warning(key_id, days_left, expires_dt, "info"))
                results["expiring_soon"].append(key_entry)
                results["predictions"].append({
                    "type":              "key_expiry_upcoming",
                    "title":             f"GPG key expires in {days_left} days",
                    "key_id":            key_id,
                    "severity":          "info",
                    "predicted_failure": expires_dt.isoformat(),
                    "action":            f"sudo apt-key adv --keyserver keyserver.ubuntu.com --refresh-keys {key_id}",
                    "urgency":           "Low — schedule renewal",
                    "impact":            "Plan renewal before this date to avoid repository failures"
                })

            else:
                # Valid with plenty of time
                key_entry["days_until_expiry"] = days_left
                key_entry["expires_date"]       = expires_dt.strftime("%Y-%m-%d")
                results["valid_keys"].append(key_entry)
        else:
            # No expiry — permanent key
            key_entry["expires"] = "never"
            results["valid_keys"].append(key_entry)


# ── PARSER: GPG PLAIN FORMAT (FALLBACK) ─────────────────────
def _parse_gpg_plain(output: str, results: dict):
    """Fallback parser for non-colon gpg output."""
    for line in output.splitlines():
        line_lower = line.lower()
        if "expired" in line_lower:
            results["expired_keys"].append({
                "raw":      line.strip(),
                "severity": "critical",
                "fix":      "sudo apt-key adv --keyserver keyserver.ubuntu.com --refresh-keys",
                "impact":   "Key expired — repository verification failing"
            })
        elif "expires" in line_lower:
            results["expiring_soon"].append({
                "raw":      line.strip(),
                "severity": "warning",
                "fix":      "sudo apt-key adv --keyserver keyserver.ubuntu.com --refresh-keys",
                "urgency":  "Check expiry date and renew if within 30 days"
            })
        elif line.startswith("pub"):
            results["valid_keys"].append({
                "raw":     line.strip(),
                "expires": "unknown — use gpg --with-colons for full details"
            })


# ── PARSER: APT KEYRING ──────────────────────────────────────
def _parse_apt_keyring(output: str, results: dict):
    """
    Parse apt-key list output to catch system-level expired keys
    not visible in user GPG keyring.
    """
    for line in output.splitlines():
        if "expired" in line.lower():
            results["expired_keys"].append({
                "raw":      line.strip(),
                "source":   "apt-keyring",
                "severity": "critical",
                "fix":      "sudo apt-key adv --keyserver keyserver.ubuntu.com --refresh-keys",
                "impact":   "System apt key expired — package verification failing"
            })


# ── HELPERS ──────────────────────────────────────────────────
def _ts_to_iso(ts: str) -> str:
    """Convert Unix timestamp string to ISO date string."""
    if ts and ts.isdigit():
        try:
            return datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d")
        except (ValueError, OSError):
            return ts
    return ts or "unknown"


def _expiry_warning(key_id: str, days_left: int, expires_dt: datetime, severity: str) -> dict:
    return {
        "days_left":    days_left,
        "expires_date": expires_dt.strftime("%Y-%m-%d"),
        "severity":     severity,
        "fix":          (
            f"sudo apt-key adv --keyserver keyserver.ubuntu.com "
            f"--refresh-keys {key_id}"
        ),
        "urgency": (
            "Critical — act today" if days_left <= 7
            else "High — renew within 7 days" if days_left <= 14
            else "Low — schedule renewal"
        )
    }


def _finalise_summary(results: dict):
    """Calculate summary counts and overall health status."""
    results["summary"]["total_valid"]   = len(results["valid_keys"])
    results["summary"]["total_expired"] = len(results["expired_keys"])
    results["summary"]["total_missing"] = len(results["missing_keys"])
    results["summary"]["total_expiring_soon"] = len(results["expiring_soon"])
    results["summary"]["predictions_count"]   = len(results["predictions"])

    if results["expired_keys"] or results["missing_keys"]:
        results["summary"]["health"] = "critical"
    elif any(p["severity"] == "critical" for p in results["predictions"]):
        results["summary"]["health"] = "critical"
    elif results["expiring_soon"]:
        results["summary"]["health"] = "warning"
    else:
        results["summary"]["health"] = "healthy"


if __name__ == "__main__":
    print(json.dumps(scan_gpg(), indent=2))

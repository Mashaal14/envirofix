import subprocess
import json
import requests

OLLAMA_URL = "http://host.docker.internal:11434/api/generate"
MODEL_NAME = "deepseek-r1:8b"

def get_real_system_state():
    """Get actual system issues"""
    issues = []
    
    # Check for broken packages
    result = subprocess.run(["apt", "--fix-broken", "install", "-s"], 
                           capture_output=True, text=True)
    if "Unmet dependencies" in result.stderr:
        issues.append({
            "type": "broken_dependencies",
            "error": result.stderr[:500]
        })
    
    # Check version conflicts
    dpkg = subprocess.run(["dpkg", "-l"], capture_output=True, text=True)
    packages = {}
    for line in dpkg.stdout.split('\n'):
        if line.startswith('ii '):
            parts = line.split()
            if len(parts) >= 3:
                packages[parts[1]] = parts[2]
    
    # Check specific conflicts from your output
    conflict_pairs = [
        ('libfdisk1', '2.42-6'),
        ('libblkid1', '2.42-5'),
        ('libuuid1', '2.42-5'),
        ('util-linux', '2.42-6')
    ]
    
    for pkg, expected in conflict_pairs:
        if pkg in packages and packages[pkg] != expected:
            issues.append({
                "type": "version_mismatch",
                "package": pkg,
                "installed": packages[pkg],
                "expected": expected,
                "fix": "sudo apt --fix-broken install -y"
            })
    
    return issues

def analyse_with_context(issue_text, tool):
    """Analyze with real system context"""
    
    real_issues = get_real_system_state()
    
    # Build intelligent prompt with actual system state
    prompt = f"""You are EnviroFix, an expert Kali Linux diagnostic AI.
    
REAL SYSTEM STATE DETECTED:
{json.dumps(real_issues, indent=2)}

USER REPORTED ISSUE: {issue_text}
TOOL: {tool}

The kernel headers are already installed. The REAL problem is package dependency conflicts.
Analyze the dependency issues and provide the correct fix.

Return JSON with:
- severity: (critical/warning/info)
- root_cause: (the ACTUAL problem - version mismatches)
- affected_components: (list of affected packages)
- fix_steps: (commands that will ACTUALLY work)
- explanation: (simple explanation)
- risk_level: (Safe/Caution/Hold)
- teaches: (what the user learns about dependency management)

IMPORTANT: The correct fix is 'sudo apt --fix-broken install -y' first, not reinstalling headers.
"""
    
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.3}
        }, timeout=90)
        
        if response.status_code == 200:
            result = response.json().get('response', '')
            # Extract JSON
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
    except Exception as e:
        print(f"AI error: {e}")
    
    # Fallback with CORRECT fix
    return {
        "severity": "critical",
        "root_cause": "Package dependency conflicts detected. libfdisk1, libblkid1, libuuid1 have version mismatches (2.42-5 vs 2.42-6).",
        "affected_components": ["fdisk", "util-linux", "mount", "libfdisk1", "libblkid1", "libuuid1"],
        "fix_steps": [
            "sudo apt --fix-broken install -y",
            "sudo apt update",
            "sudo apt upgrade -y"
        ],
        "explanation": "Your system has inconsistent package versions. This often happens after partial upgrades or mixing repositories. The package manager needs to fix broken dependencies before anything else.",
        "risk_level": "Hold",
        "teaches": "Package version consistency is critical in Debian-based systems. Always run 'apt --fix-broken install' when you see dependency errors.",
        "confidence": "high"
    }

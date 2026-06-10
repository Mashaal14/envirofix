# Save as test_ai.py in your project root
import sys, os
sys.path.insert(0, '/home/kali/envirofix')
from backend.ai.ai_engine import analyse_issue

test_issue = {
    "type": "missing_kernel_headers",
    "detail": "linux-headers-6.18.12+kali-amd64 not installed",
    "kernel_version": "6.18.12+kali-amd64",
    "impact": "Cannot compile kernel modules or dkms"
}

result = analyse_issue(test_issue)
import json
print(json.dumps(result, indent=2))

from datetime import datetime
from pathlib import Path
import json

AUDIT_PATH = Path("artifacts/audit/access_audit.jsonl")
AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)

def write_access_audit(role: str, endpoint: str, action: str, allowed: bool):
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "role": role,
        "endpoint": endpoint,
        "action": action,
        "allowed": allowed,
    }
    with AUDIT_PATH.open("a") as f:
        f.write(json.dumps(record) + "\n")
    return record

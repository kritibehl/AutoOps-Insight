from fastapi import Header, HTTPException

TOKEN_ROLE_MAP = {
    "support-l1-token": "support_l1",
    "service-owner-token": "service_owner",
    "admin-token": "admin",
    "dev-token": "admin",
}

ROLE_PERMISSIONS = {
    "support_l1": {"ingest", "read_reports"},
    "service_owner": {"ingest", "read_reports", "escalate"},
    "admin": {"ingest", "read_reports", "escalate", "admin"},
}

def get_role(x_autoops_token: str | None = Header(default=None, alias="X-AutoOps-Token")):
    if not x_autoops_token:
        raise HTTPException(status_code=401, detail="Missing X-AutoOps-Token")

    role = TOKEN_ROLE_MAP.get(x_autoops_token)
    if not role:
        raise HTTPException(status_code=403, detail="Invalid AutoOps token")

    return role

def require_permission(role: str, permission: str):
    allowed = ROLE_PERMISSIONS.get(role, set())
    if permission not in allowed:
        raise HTTPException(status_code=403, detail=f"Role {role} lacks {permission} permission")

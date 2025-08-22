import json
from pathlib import Path
from typing import Dict, List

ROLES_FILE = Path(__file__).resolve().parents[2] / "models" / "roles.json"


def _ensure_roles_file() -> None:
    ROLES_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not ROLES_FILE.exists():
        ROLES_FILE.write_text(json.dumps({"roles": []}, ensure_ascii=False, indent=2), encoding="utf-8")


def list_roles() -> List[Dict]:
    _ensure_roles_file()
    data = json.loads(ROLES_FILE.read_text(encoding="utf-8"))
    return data.get("roles", [])


def add_or_update_role(name: str, base_model: str, adapter_path: str) -> None:
    _ensure_roles_file()
    data = json.loads(ROLES_FILE.read_text(encoding="utf-8"))
    roles = data.get("roles", [])
    exists = False
    for r in roles:
        if r.get("name") == name:
            r["base_model"] = base_model
            r["adapter_path"] = adapter_path
            exists = True
            break
    if not exists:
        roles.append({"name": name, "base_model": base_model, "adapter_path": adapter_path})
    data["roles"] = roles
    ROLES_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_role(name: str) -> Dict:
    for r in list_roles():
        if r.get("name") == name:
            return r
    raise KeyError(f"Role not found: {name}")

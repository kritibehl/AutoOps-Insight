from __future__ import annotations

import os
from typing import Any, Dict, List

import yaml

RULES_CONFIG_PATH = os.getenv("AUTOOPS_RULES_PATH", "config/rules.yaml")


def load_rules_config() -> List[Dict[str, Any]]:
    with open(RULES_CONFIG_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    rules = data.get("rules", [])
    if not isinstance(rules, list):
        raise ValueError("config/rules.yaml must contain a top-level 'rules' list")
    return rules


def reload_rules_config() -> List[Dict[str, Any]]:
    return load_rules_config()

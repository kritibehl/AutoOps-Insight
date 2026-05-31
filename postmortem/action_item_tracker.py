import json
from pathlib import Path

ACTION_ITEMS = [
    {"owner": "platform_runtime_team", "action": "add dependency timeout regression coverage", "status": "open", "priority": "high"},
    {"owner": "sre_oncall", "action": "tighten retry-budget alerting", "status": "open", "priority": "high"},
    {"owner": "service_owner", "action": "document rollback criteria", "status": "in_progress", "priority": "medium"},
    {"owner": "release_engineering", "action": "add deployment correlation review", "status": "open", "priority": "medium"}
]

def summarize_action_items(items):
    return {
        "total_action_items": len(items),
        "open_items": sum(1 for i in items if i["status"] == "open"),
        "in_progress_items": sum(1 for i in items if i["status"] == "in_progress"),
        "high_priority_items": sum(1 for i in items if i["priority"] == "high"),
        "items": items
    }

def main():
    summary = summarize_action_items(ACTION_ITEMS)
    Path("postmortem/action_item_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()

import subprocess
import json
import os

def run_bandit_scan(path_to_scan=".", output_file="bandit_report.json"):
    """
    Runs Bandit static analysis on the specified path and saves output to a JSON file.
    """
    print(f"🔍 Running Bandit scan on: {path_to_scan}")
    command = [
        "bandit", "-r", path_to_scan,
        "-f", "json",
        "-o", output_file
    ]
    subprocess.run(command)
    print(f"✅ Scan complete. Output saved to {output_file}")

def summarize_findings(report_path="bandit_report.json"):
    """
    Parses Bandit output and prints a summary of the top 3 findings.
    """
    if not os.path.exists(report_path):
        print("⚠️ Bandit report not found.")
        return

    with open(report_path) as f:
        data = json.load(f)
        issues = data.get("results", [])
        if not issues:
            print("🎉 No security issues found!")
            return

        print(f"\n⚠️ Found {len(issues)} issues. Showing top 3:\n")

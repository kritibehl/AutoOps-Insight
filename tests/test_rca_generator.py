import json
from pathlib import Path
from fastapi.testclient import TestClient

from main import app
from rca.generate_rca import generate_markdown

client = TestClient(app)

def test_generate_rca_markdown_contains_core_sections():
    data = json.loads(Path("rca/escalation_chain.json").read_text())
    output = generate_markdown(data)

    assert "Probable cause" in output
    assert "Impacted services" in output
    assert "Timeline" in output
    assert "Rollback candidate" in output
    assert "Next actions" in output

def test_rca_demo_endpoint():
    r = client.get("/rca/demo")
    assert r.status_code == 200
    data = r.json()

    assert data["rollback_candidate"] is True
    assert data["release_risk"] == "high"
    assert "agentgrid" in data["impacted_services"]

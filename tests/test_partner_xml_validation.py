from integrations.parse_partner_payload import parse_partner_payload

def test_valid_partner_payload_extracts_fields():
    result = parse_partner_payload("integrations/sample_partner_payload.xml")

    assert result["valid"] is True
    assert result["extracted_fields"]["partner_id"] == "partner_analytics_042"
    assert result["extracted_fields"]["deployment_id"] == "DEP-1001"
    assert result["support_routing_risk"] == "route_to_integration_stability_review"

def test_malformed_partner_payload_detects_errors():
    result = parse_partner_payload("integrations/malformed_partner_payload.xml")

    assert result["valid"] is False
    assert "missing_required_field:deployment_id" in result["validation_errors"]
    assert "invalid_integer_field:response_latency_ms" in result["validation_errors"]

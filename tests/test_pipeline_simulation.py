from pipeline_simulation.run_pipeline_simulation import RAW_EVENTS, run_pipeline

def test_pipeline_simulation_runs_all_stages():
    output = run_pipeline(RAW_EVENTS)

    assert output["pipeline_status"] == "PASS"
    assert output["summary"]["records_received"] == 4
    assert output["summary"]["records_valid"] == 4
    assert output["summary"]["warehouse_rows_ready"] == 3
    assert output["summary"]["anomaly_count"] == 2

    stages = [stage["stage"] for stage in output["stages"]]
    assert stages == [
        "ingest",
        "aggregate",
        "warehouse",
        "anomaly_detection",
        "dashboard",
    ]

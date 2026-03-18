# Power BI Dashboard Plan

## Pages
1. CI Failure Trends Over Time
2. Flaky / Failure Category Distribution
3. Root Cause Category Counts
4. Deployment Regression Spikes
5. Release Risk by Service / Pipeline

## Visuals
- Line chart: daily failure_events
- Stacked column: failure_family by day
- Heatmap: pipeline_name vs day
- KPI cards: release_blocking_events, regression_flag count
- Table: highest regression_delta windows

## Notes
Import the CSVs in Power BI and create relationships on day / week_start / pipeline_name as needed.

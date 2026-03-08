# AutoOps Insight Report

Generated at: 2026-03-08T01:52:38.607111+00:00

## Release Risk Summary

- Release risk: **high**
- Total analyses: **8**
- Release-blocking incidents: **8**

## Top Failure Families

- `timeout`: 7
- `retry_exhausted`: 1

## Top Recurring Signatures

- `timeout:733da8a4e20740af` | family=timeout | severity=high | count=7 | first_seen=2026-03-08T01:45:06.301515+00:00 | last_seen=2026-03-08T01:48:02.340941+00:00

## Recent Failure Family Distribution

- `timeout`: count=4 | share=80.0%
- `retry_exhausted`: count=1 | share=20.0%

## Recent Signature Concentration

- Total recent items: 5
- Unique signatures: 2
- Top signature: timeout:733da8a4e20740af
- Top signature count: 4
- Top signature share: 80.0%

## Window Comparison

- Recent window size: 5
- Baseline window size: 3
- Recent release-blocker rate: 100.0%
- Baseline release-blocker rate: 100.0%
- Delta: 0.0 percentage points

## Recent Family Trend

- `timeout`: recent=4 | baseline=3 | delta=1
- `retry_exhausted`: recent=1 | baseline=0 | delta=1

## Detected Anomalies

- [high] recurring_signature_concentration: Top signature timeout:733da8a4e20740af accounts for 80.0% of recent analyses.
- [high] repeated_signature: Signature timeout:733da8a4e20740af has recurred 7 times with severity high.
- [high] release_blocker_saturation: All recent analyses are marked release-blocking.

## Recent Analyses

- id=8 | created_at=2026-03-08T01:48:43.114266+00:00 | family=retry_exhausted | severity=medium | signature=retry_exhausted:44fbfad41b02c18b | release_blocking=True
- id=7 | created_at=2026-03-08T01:48:02.340941+00:00 | family=timeout | severity=high | signature=timeout:733da8a4e20740af | release_blocking=True
- id=6 | created_at=2026-03-08T01:48:01.593224+00:00 | family=timeout | severity=high | signature=timeout:733da8a4e20740af | release_blocking=True
- id=5 | created_at=2026-03-08T01:47:58.806046+00:00 | family=timeout | severity=high | signature=timeout:733da8a4e20740af | release_blocking=True
- id=4 | created_at=2026-03-08T01:47:43.749083+00:00 | family=timeout | severity=high | signature=timeout:733da8a4e20740af | release_blocking=True
- id=3 | created_at=2026-03-08T01:45:06.322692+00:00 | family=timeout | severity=high | signature=timeout:733da8a4e20740af | release_blocking=True
- id=2 | created_at=2026-03-08T01:45:06.312946+00:00 | family=timeout | severity=high | signature=timeout:733da8a4e20740af | release_blocking=True
- id=1 | created_at=2026-03-08T01:45:06.301515+00:00 | family=timeout | severity=high | signature=timeout:733da8a4e20740af | release_blocking=True

## Operational Recommendation

- Repeated failure signatures or concentrated release-blocking patterns indicate elevated release risk.
- Review recurring signatures, failure-family spikes, and recent blocker concentration before promotion.

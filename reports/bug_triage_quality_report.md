# Bug Triage Quality Report

- Bugs reviewed: 3
- P0 review count: 1
- High regression risk count: 1
- Pipeline status: PASS

## Failure families

```json
{
  "retry_storm": 1,
  "auth_scope_regression": 1,
  "dependency_timeout": 1
}
```

## Triaged bugs

```json
[
  {
    "bug_id": "BUG-101",
    "service": "checkout-api",
    "failure_family": "retry_storm",
    "priority": "p0_review",
    "regression_risk": "medium",
    "recurring_failure": false,
    "recommended_owner": "release_engineering",
    "investigation_summary": "checkout-api issue classified as retry_storm with high customer impact."
  },
  {
    "bug_id": "BUG-102",
    "service": "partner-reporting-api",
    "failure_family": "auth_scope_regression",
    "priority": "p2",
    "regression_risk": "high",
    "recurring_failure": false,
    "recommended_owner": "release_engineering",
    "investigation_summary": "partner-reporting-api issue classified as auth_scope_regression with medium customer impact."
  },
  {
    "bug_id": "BUG-103",
    "service": "payment-api",
    "failure_family": "dependency_timeout",
    "priority": "p1",
    "regression_risk": "low",
    "recurring_failure": false,
    "recommended_owner": "payment-api_owner",
    "investigation_summary": "payment-api issue classified as dependency_timeout with high customer impact."
  }
]
```

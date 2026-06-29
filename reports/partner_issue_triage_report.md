# Partner Issue Triage Report

## Affected Partner

`external_integration_partner`

## Issue Type

API / authentication / dashboard

## Affected Service

`partner-reporting-api`

## Severity

high

## Confidence

0.82

## Reported Symptom

Partner dashboard fails to load playback analytics after API release.

## Evidence

- HTTP 403 from `partner-reporting-api`
- API response: invalid partner token scope
- auth scope validation failure in logs
- dashboard analytics request rejected at API layer
- SQL signal shows partner analytics export rows dropped by 42%
- recent release `release-204` correlated with issue window

## Likely Root Cause

Partner API authentication scope regression after release.

## Recommended Action

internal_escalation

## Escalation Path

1. support_l1
2. partner_support_l2
3. partner-reporting-api owner
4. auth platform owner
5. release engineering

## Partner-Safe Summary

We detected that partner analytics dashboard requests are being rejected by the reporting API after a recent release. The issue appears related to API authentication scope validation. Engineering review is recommended before asking the partner to rotate credentials.

## Troubleshooting Checklist

- Confirm partner token scope and expected permissions.
- Compare API behavior before and after `release-204`.
- Review auth validation logs for partner-specific failures.
- Check SQL export volume drop for affected partner.
- Escalate internally if the release changed scope validation.
- Monitor dashboard recovery after remediation.

## Operational Value

This report converts partner-facing symptoms, HTTP status, logs, API responses, SQL signals, and release correlation into a support-ready troubleshooting summary.

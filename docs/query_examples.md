# Query Examples

## Fetch live metrics

```bash
curl https://autoops-api-126325674316.us-central1.run.app/support/metrics/live
Transition incident
curl -X POST \
"https://autoops-api-126325674316.us-central1.run.app/incidents/INC-1001/transition/live?actor=kriti&old_state=new&new_state=triaged"


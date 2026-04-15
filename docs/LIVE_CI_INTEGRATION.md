# Live CI Integration

Each repo can forward failed GitHub Actions runs to AutoOps using a workflow like this:

```yaml
name: AutoOps Failure Forwarder

on:
  workflow_dispatch:

jobs:
  forward:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Create failure log
        run: |
          cat > failure.log <<'LOG'
          ERROR dns lookup failed for payments.internal: no such host
          WARN retrying request to payments.internal after resolver error
          LOG

      - name: Send to AutoOps
        env:
          AUTOOPS_URL: ${{ secrets.AUTOOPS_URL }}
          AUTOOPS_TOKEN: ${{ secrets.AUTOOPS_TOKEN }}
        run: |
          curl -s -X POST "${AUTOOPS_URL}/integrations/github-actions/ingest" \
            -H "X-AutoOps-Token: ${AUTOOPS_TOKEN}" \
            -H "X-Repo-Name: ${GITHUB_REPOSITORY}" \
            -H "X-Workflow-Name: ${GITHUB_WORKFLOW}" \
            -H "X-Run-Id: ${GITHUB_RUN_ID}" \
            -F "file=@failure.log"

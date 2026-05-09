# GraphQL Examples

## Fetch support metrics

```graphql
query {
  supportMetrics {
    totalSupportIncidents
    escalationCount
    topIssueFamily {
      issueFamily
      count
    }
  }
}
Fetch recurring blockers
query {
  recurringCustomerBlockers {
    issue
    count
    action
  }
}


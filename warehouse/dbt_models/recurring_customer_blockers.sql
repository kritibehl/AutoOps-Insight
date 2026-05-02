SELECT
    signature,
    issue_family,
    MAX(recurrence_total) AS recurrence_total,
    COUNT(*) AS observed_count
FROM support_incidents
GROUP BY signature, issue_family
HAVING recurrence_total >= 3
ORDER BY recurrence_total DESC;

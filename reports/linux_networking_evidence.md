# Linux Networking Evidence

## Purpose

This artifact documents Linux/TCP-IP diagnostic commands used for network incident triage. It is evidence of troubleshooting workflow design, not a claim of production network ownership.

## Diagnostic commands

| Command | Purpose |
|---|---|
| `ping <host>` | basic reachability and packet loss check |
| `traceroute <host>` | path and hop-level reachability investigation |
| `dig <host>` | DNS lookup and resolver validation |
| `nslookup <host>` | DNS lookup cross-check |
| `curl -v <url>` | HTTP/TLS/API response inspection |
| `nc -vz <host> <port>` | TCP port reachability check |
| `ss -tulpn` | local listening sockets and process mapping |
| `lsof -i :<port>` | process using a local port |
| `iptables -L -n` | local firewall rule review |
| `tcpdump -i any host <host>` | packet-level capture for targeted investigation |

## Example workflow

1. Confirm basic reachability with `ping`.
2. Validate DNS with `dig` and `nslookup`.
3. Check TCP reachability with `nc -vz`.
4. Inspect HTTP/TLS behavior with `curl -v`.
5. Review local listeners with `ss -tulpn` and `lsof -i`.
6. Check firewall rules with `iptables -L -n`.
7. Capture targeted traffic with `tcpdump` only when needed.

## Safe scope

This artifact covers Linux networking and TCP/IP diagnostics. It does not claim BGP, OSPF, or ISIS routing-lab experience.

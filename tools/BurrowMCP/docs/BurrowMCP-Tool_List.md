# BurrowMCP — Tool Reference
**Version:** 0.1 (Living Document — updated as tools are added)
**Last updated:** 2026-05-05

This is a reference for what you can ask Claude to do via BurrowMCP tools
in Claude Desktop. Ask naturally — Claude knows when to call these.

---

## Lab Status

**get_lab_status()**
Overall health snapshot of all Burrow nodes.
Ask: "What's the lab status?" / "How are all the nodes doing?"

---

## Node Information

**get_node_info(node)**
Detailed info about a specific node — uptime, OS, memory, CPU.
Ask: "Tell me about Krypton1t3" / "What's EagleEye11's uptime?"
Nodes: EagleEye11, Krypton1t3, SkorpiOm, Jynx13

---

## Disk Space

**check_disk_space(node)**
Disk usage on a specific node. Useful for catching drives filling up.
Ask: "Check disk space on EagleEye11" / "Is Krypton1t3 running low on space?"

---

## Failed Services

**check_failed_services(node)**
Lists any systemd services in a failed state on a node.
Ask: "Any failed services on SkorpiOm?" / "Check Krypton1t3 for broken services"

---

## Wazuh Alerts

**get_wazuh_alerts(n=20)**
Returns the most recent n alerts from the Wazuh manager container on EagleEye11.
Parsed from NDJSON — shows timestamp, rule level, agent name, description,
groups, and MITRE tactic if tagged.
Ask: "Show me the latest Wazuh alerts" / "Any security alerts?" / 
     "Get me the last 50 Wazuh alerts"
Default: 20 alerts. Override: "get me the last 50"

---

## Splunk Search

**splunk_search(query, earliest, latest)**
Run a SPL search against Splunk on EagleEye11.
Ask: "Search Splunk for failed logins in the last hour"
     "Show me Splunk events from SkorpiOm today"
     "Run a Splunk search for [anything]"

---

## Notes
- All tools log to /Volumes/Bird's Nest/BurrowMCP/logs/burrowmcp.log
- Tools reach nodes via SSH (key-based) or docker exec (Wazuh)
- Tailscale mesh is the transport layer — nodes must be on Tailscale to reach
- EagleEye11 is the hub: Wazuh manager, Splunk, and BurrowMCP all live here
- If a node is unreachable, check Tailscale first: `tailscale status`

---

## Coming Soon (Session 8+)
- get_wazuh_agent_status() — agent health from manager side
- Splunk alert integration
- BurrowVoice → BurrowMCP handoff
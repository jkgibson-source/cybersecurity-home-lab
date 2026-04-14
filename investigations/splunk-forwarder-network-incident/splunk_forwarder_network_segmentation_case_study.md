# SOC Incident Report: Splunk Forwarder Connectivity Failure

## Summary
A Splunk Universal Forwarder on SkorpiOm failed to send logs to Splunk Enterprise on EagleEye11 due to network segmentation.

## Timeline
- Forwarder inactive
- Verified configs
- Checked port 9997
- Discovered network mismatch
- Reconnected to correct network
- Logs resumed

## Root Cause
SkorpiOm was connected to a different network than EagleEye11.

## Diagram
![Network Diagram](splunk_network_diagram.svg)

## Resolution
- Reconnected device to correct network
- Verified ingestion

## Detection & Response
- Identified ingestion failure via Splunk health dashboard
- Investigated forwarder status
- Validated connectivity
- Restored pipeline

## Lessons Learned
- Always verify network layer first
- Use static IPs or hostnames

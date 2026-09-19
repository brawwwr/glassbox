---
title: Pi-hole blocklists that did not break things
date: 2026-07-12
tags: [homelab, pihole, dns]
---

# Pi-hole blocklists that did not break things

After a month of tuning, the blocklist set that blocks a lot without breaking the TV apps:

- StevenBlack unified (base)
- OISD small
- A short personal allowlist: the smart-TV telemetry domain that also serves the app store, and the
  thermostat's cloud endpoint.

Blocked percentage sits around 18-22% of queries. The TV app store broke twice before I found the
allowlist domain; symptom was an infinite spinner, not an error.

Query log is useful for spotting new devices phoning home. The doorbell talks to a domain every 30 seconds.

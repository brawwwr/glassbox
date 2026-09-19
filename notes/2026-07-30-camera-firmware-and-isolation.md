---
title: Camera firmware update and isolation check
date: 2026-07-30
tags: [security, iot, homelab]
---

# Camera firmware update and isolation check

Updated the two outdoor cameras to the latest firmware. Release notes mention an authentication fix.

Verified isolation afterward: from the IoT VLAN, tried to reach the NAS on 445 and the desktop on 3389.
Both blocked at the firewall as expected. The cameras can still reach NTP and their cloud endpoint.

Pi-hole shows the cameras now query a new telemetry domain after the update. Blocked it; recording still works.

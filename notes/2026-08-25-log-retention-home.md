---
title: Log retention at home
date: 2026-08-25
tags: [security, logging, homelab]
---

# Log retention at home

What I keep and for how long:

- Firewall: 30 days, rotated, on the firewall itself; weekly copy to the NAS.
- Pi-hole query log: 7 days. Longer is creepy and not useful.
- Wireguard handshakes: 90 days. Small, and it is the remote access path.
- Camera motion events: 14 days, then gone.

Anything that identifies a person (query log, camera) gets the shortest retention. Anything about
the perimeter gets the longest.

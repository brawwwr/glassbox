---
title: Home lab inventory, June 2026
date: 2026-06-03
tags: [homelab, hardware]
---

# Home lab inventory, June 2026

Current state of the rack (well, the shelf) as of early June.

- Main desktop: i9, 112 GB DDR5, RTX 4070 12 GB, 1 TB NVMe (C:), 2 TB NVMe (F:). Windows 11 Pro.
- NAS: 4-bay, two 8 TB drives mirrored, running a plain SMB share. Uptime 211 days.
- Switch: 8-port managed gigabit. Ports 1-4 are the trusted VLAN, 5-8 are IoT.
- Router: consumer box in bridge mode behind a small firewall appliance.
- Raspberry Pi 4 (8 GB) running Pi-hole and a Wireguard endpoint.

Things I keep meaning to do: label the cables, move the Pi to a proper case with a fan,
and write down the switch admin password somewhere that is not my head.

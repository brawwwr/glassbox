---
title: Wireguard on the Pi for remote access
date: 2026-07-20
tags: [homelab, vpn, wireguard]
---

# Wireguard on the Pi for remote access

Set up Wireguard on the Pi so I can reach the NAS from my phone.

- Server on the Pi, UDP 51820 forwarded from the firewall.
- One peer per device; keys generated on the device, never copied around.
- AllowedIPs on the phone limited to the trusted subnet and the Pi itself, so it is split-tunnel.
- Dynamic DNS updater running on the firewall so the phone config uses a hostname.

Handshake works on cellular. Throughput from the coffee shop was about 40 Mbps, limited by upstream.
Rotated the phone's key once already after reinstalling the app.

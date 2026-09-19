---
title: Installing the second NVMe, what went wrong
date: 2026-07-05
tags: [hardware, troubleshooting]
---

# Installing the second NVMe, what went wrong

Installed the 2 TB NVMe. Two hiccups.

First, the drive did not show up in Explorer. It was there in Disk Management as unallocated; needed
Initialize Disk (GPT), then New Simple Volume. Formatted NTFS with default allocation size. Letter F:.

Second, the heatsink that came with the motherboard did not fit with the drive's own label sticker,
which is thicker than it looks. Removed the sticker (keeping it in the box for warranty), then fine.

Idle temp 38 C, under a 100 GB copy 61 C. Acceptable.

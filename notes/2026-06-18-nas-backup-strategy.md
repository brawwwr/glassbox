---
title: NAS backup strategy (3-2-1, finally)
date: 2026-06-18
tags: [homelab, backup, nas]
---

# NAS backup strategy (3-2-1, finally)

The NAS mirror is redundancy, not backup. Wrote down an actual 3-2-1 plan:

1. Primary: NAS mirrored pair (live data).
2. Local second copy: nightly rsync to a USB 8 TB drive on the desktop, versioned with --link-dest so I get
   cheap daily snapshots. Keep 30 days.
3. Offsite: weekly encrypted upload of the photo and documents folders to a cloud bucket. Restic, repository
   key stored in the password manager. Everything else is re-downloadable and not worth the egress.

Restore test: monthly, pick three random files from the offsite copy and restore them to a temp folder.
First test done 2026-06-17: all three restored, checksums matched. Took 4 minutes.

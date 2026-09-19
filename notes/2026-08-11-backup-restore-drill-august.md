---
title: August restore drill
date: 2026-08-11
tags: [backup, drill]
---

# August restore drill

Monthly restore test from the offsite restic repository.

Picked: a 2019 photo, a tax PDF from 2023, and the home network diagram. All restored, checksums matched.
Restore of 3 files took 2 minutes 50 seconds including repository unlock.

Also verified that the nightly local rsync snapshots exist for every day in July. They do. Snapshot folder
for the month is 41 GB total thanks to hard links; the actual changed data was about 6 GB.

One change: added the glassbox project folder to the nightly rsync include list.

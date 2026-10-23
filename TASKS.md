# TASKS.md — Worktree Fleet board

Coordinator-owned. Only the coordinator writes this board. Entry format:
slug, one-line outcome, worktree, status (QUEUED / ACTIVE / IN-REVIEW /
DONE / KILLED), acceptance test.

| slug | outcome | worktree | status | acceptance test |
| --- | --- | --- | --- | --- |
| gallery-thumb-incremental | build_gallery.py reuses up-to-date thumbnails instead of regenerating all of them on every run | ../gif-vault-wt/gallery-thumb-incremental | DONE | Two consecutive `python3 tools/build_gallery.py` runs exit 0; the second run rewrites no thumbnails (mtimes unchanged); docs/data.json is byte-identical between runs and lists every GIF under projects/ |

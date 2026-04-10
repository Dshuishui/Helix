---
name: shared
description: |
  Internal shared utilities for AutoDNA skills. Not a user-facing skill.
  Contains autodna_store.py for inter-Skill data passing via filesystem.
  Do not activate directly.
---

# AutoDNA Shared Utilities

This package provides shared scripts used by all AutoDNA Skills.

## autodna_store.py

Inter-Skill filesystem store. Used by all AutoDNA Skills to pass large outputs
by file ID instead of embedding full text in each invocation message.

See `scripts/autodna_store.py` for full documentation.

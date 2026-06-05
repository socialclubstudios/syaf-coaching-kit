# SYAF Coaching Kit

Built for SYAF coaches outside the SCS Cowork org. Distributed as a manual `.plugin` zip (not via the SCS marketplace) — install through Cowork's "Install plugin from file" path.

## What's inside

- **`process-syaf-call`** — Process a coaching call transcript into the SYAF student vault. Extracts metadata, matches the student profile, writes the coaching log, captures wins/flags/action items.
- **`student-briefing`** — Pre-call student briefing. Pulls current focus, coaching history, action items, wins, and flags from the vault.

## Setup

`student-briefing` reads from the SYAF brain vault. On first run it will check for the vault locally (default: `~/Documents/obsidian/syaf-brain/`); if not found, it'll guide you through cloning the GitHub repo.

## Connectors

Slack, ClickUp, Granola, Google Calendar.

## Updates

This plugin doesn't auto-update — get the next version from Peter when he ships one (Slack or Drive handoff).

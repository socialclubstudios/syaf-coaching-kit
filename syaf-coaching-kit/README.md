# SYAF Coaching Kit

The SYAF coaching toolkit for coaches — process coaching call transcripts into the student vault, prep pre-call briefings, sync Drive recordings, and write Skool 1-on-1 recaps.

## Install

- **Marketplace (recommended):** `/plugin marketplace add socialclubstudios/syaf-coaching-kit` then `/plugin install syaf-coaching-kit`
- **From a `.plugin` zip:** Claude Code → *Install plugin from file*.

## What's inside

- **`process-syaf-call`** — Process a coaching call transcript into the SYAF student vault. Extracts metadata, matches the student profile, writes the coaching log, captures wins/flags/action items.
- **`student-briefing`** — Pre-call student briefing. Pulls current focus, coaching history, action items, wins, and flags from the vault.
- **`sync-syaf-recordings`** — Pull coaching recordings from Google Drive and transcribe them (AssemblyAI) into the vault.
- **`skool-1on1-recap`** — Turn an intro advisory call transcript into a ready-to-paste Skool community post that recaps the call for the named student and the broader SYAF Accelerator group.

## Setup

The skills read and write the SYAF brain vault. On first run they look for it locally (default: `~/Documents/obsidian/syaf-brain/`); if it's missing, they'll point you to clone it. `sync-syaf-recordings` also needs an AssemblyAI API key — set `$ASSEMBLYAI_API_KEY` or save it to `~/.assemblyai_api_key`.

## Connectors

Slack, ClickUp, Granola, Google Calendar, Google Drive.

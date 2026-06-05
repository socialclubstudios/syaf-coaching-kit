# SYAF Coaching Kit

A standalone Claude Code marketplace holding one plugin — `syaf-coaching-kit` — for SYAF coaches. It's the same coaching toolkit Peter uses, packaged so coaches can install it directly and pull updates over git instead of receiving one-off `.plugin` zips.

## Install

```
/plugin marketplace add socialclubstudios/syaf-coaching-kit
/plugin install syaf-coaching-kit
```

New coach setting up from scratch (vault + plugin, step by step): see **[COACH-ONBOARDING.md](COACH-ONBOARDING.md)**.

## What's inside

| Skill | What it does |
|-------|--------------|
| `student-briefing` | Pre-call briefing — focus, coaching history, action items, wins, flags from the vault |
| `process-syaf-call` | Process a call transcript into a student profile update + coaching log |
| `sync-syaf-recordings` | Pull recordings from Google Drive, transcribe (AssemblyAI), file into the vault |

All three read/write the **SYAF student vault** (`petervndr/syaf-brain`), cloned to `~/Documents/obsidian/syaf-brain`. The plugin is useless without it — do the vault setup first.

## Maintainer

This repo is **generated**, not hand-edited. The source of truth is `~/.claude/skills/` plus the manifest at `Skillmaster/dist-cowork/plugins-external/syaf-coaching-kit/skills.manifest`. To ship an update:

```bash
~/Peter\ OS/Skillmaster/dist-cowork/publish-cowork.sh --syaf-repo
cd ~/claude/socialclubstudios/syaf-coaching-kit && git add -A && git commit -m "Update" && git push
```

Editing files here directly will be overwritten on the next publish (except `README.md`, `COACH-ONBOARDING.md`, and `.git`).

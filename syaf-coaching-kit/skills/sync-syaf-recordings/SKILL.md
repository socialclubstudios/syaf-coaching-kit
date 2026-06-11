---
name: sync-syaf-recordings
description: Check the SYAF call recordings Drive folder for new videos, download, transcribe with AssemblyAI, infer speakers, file transcripts into the SYAF vault, and update affected student profiles. Triggers on "sync SYAF recordings", "check for new SYAF calls", "transcribe new SYAF recordings", "process the SYAF Drive folder", "transcribe the latest coaching call", or any time a new recording has been uploaded to the SYAF shared Drive.
---

# Sync SYAF Call Recordings

Detect new recordings in the SYAF Drive folder, transcribe them with AssemblyAI speaker diarization, infer which SYAF students and coaches are speaking, file the transcript into the vault, update student profiles, and open the result for Skool posting.

## When to use

- "Sync SYAF recordings" / "check for new SYAF calls"
- "Transcribe the latest coaching call"
- "I uploaded a new recording to Drive"
- Any time someone drops a new `.mp4` into the SYAF recordings folder on Drive
- Periodic sweeps to catch up on a backlog of unprocessed recordings

**Do NOT use for:**
- Non-SYAF recordings — use `transcribe-video` for podcast interviews, testimonials, or one-off files
- Granola or Fathom calls — use `sync-granola` or `sweep-fathom` for those

---

## Config

| Key | Value |
|-----|-------|
| **Drive folder ID** | `1bYs_e32fOGFZHJvbm5wv8KhV64Bx93va` |
| **Transcription script** | `scripts/transcribe.py` (bundled with this skill) |
| **Tmp download path** | `/tmp/<filename>` |
| **Known coaches (not students)** | Peter Vander Wall, Brian Mayoral, Ryan Bakke, Zach, Cassidy, Kristin, McKenzie |

### SYAF vault path (portable)

Check these paths in order and use the first that exists:
1. `~/obsidian/syaf/`
2. `~/Documents/obsidian/syaf/`
3. `~/Documents/obsidian/syaf-brain/`

Key subfolders:
- **Transcripts:** `<vault>/Transcripts/`
- **Students:** `<vault>/Students/`

If none of these paths exist, stop and tell the user:

> SYAF vault not found. Clone it locally:
> ```
> mkdir -p ~/obsidian && cd ~/obsidian && gh repo clone petervndr/syaf-brain syaf
> ```
> Then rerun this command.

---

## Prerequisites

### AssemblyAI API key

Stored at one of:
- `~/.assemblyai_api_key` (preferred — file with the key as the only contents)
- `$ASSEMBLYAI_API_KEY` environment variable

If neither exists, tell the user: "I need an AssemblyAI API key. Sign up at assemblyai.com (free tier covers ~3 hrs/month). Save the key at `~/.assemblyai_api_key` or export `ASSEMBLYAI_API_KEY`."

### System dependencies

- **Python 3** — pre-installed on macOS
- **ffmpeg** — required for re-encoding large files. Install with `brew install ffmpeg` if missing.

---

## Workflow

### Step 0: Choose mode

Before doing anything else, ask the user:

> Process just the **latest recording**, or **catch up** on all unprocessed recordings?
> - **Latest only** — grabs the single newest file, transcribes it. Best for "I just ran a call."
> - **Catch up** — scans the full folder, compares against existing transcripts, processes everything new. Best for backlog.

**Default:** If the user just says "sync SYAF recordings" or "transcribe the latest call" without specifying, default to **Latest only**.

Only do the full sweep if they explicitly choose "Catch up" or say something like "process all new recordings" / "check for any I've missed."

### Step 1: Find recordings

Use the Google Drive MCP tools to list the SYAF recordings folder:

- Use the `listFolder` tool with folder ID `1bYs_e32fOGFZHJvbm5wv8KhV64Bx93va`
- Filter for video/audio files (`.mp4`, `.mov`, `.m4a`, `.mp3`, `.wav`, `.webm`)

**If mode is "Latest only":**
- Sort by name (filenames typically start with dates) or by modified date
- Pick the single most recent file
- Check whether a transcript already exists for that date in `<vault>/Transcripts/` — if yes, tell the user "The latest recording already has a transcript" and stop

**If mode is "Catch up":**
- For each video file, derive the expected transcript date prefix from the filename
- Check whether a matching `.md` already exists in `<vault>/Transcripts/` (match by date prefix `YYYY-MM-DD`)
- A file is "new" if no matching transcript exists
- If no new files exist, tell the user: "All recordings already have transcripts. Nothing to process." Stop.

### Step 2: Download

Download each new recording using the Google Drive MCP `downloadFile` tool, saving to `/tmp/<filename>`.

If the MCP download tool doesn't support saving to a local path, fall back to:

```bash
gws drive files get \
  --params '{"fileId": "<FILE_ID>", "alt": "media"}' \
  -o /tmp/<filename>
```

Monitor the download progress. For large files this may take a few minutes.

### Step 3: Transcribe

Once downloaded, find the bundled transcription script and run it:

```bash
SKILL_DIR="$(find ~/.claude -path '*/sync-syaf-recordings/scripts/transcribe.py' -print -quit 2>/dev/null)"
if [ -z "$SKILL_DIR" ]; then
  SKILL_DIR="$(find . -path '*/sync-syaf-recordings/scripts/transcribe.py' -print -quit 2>/dev/null)"
fi
python3 "$SKILL_DIR" "/tmp/<filename>" "/tmp/<stem>.transcript.json"
```

The script automatically:
- Re-encodes files >12 MB to 24 kbps mono mp3 using `ffmpeg` (produces `/tmp/<stem>.low.mp3`)
- Uploads via curl to AssemblyAI `/v2/upload`
- Requests transcription with `speaker_labels: true`, `speech_models: ["universal-2"]`
- Polls until complete
- Writes JSON: `{transcript_id, audio_duration_sec, speaker_count, utterances: [{speaker, start_ms, end_ms, text}], full_text}`

If the script exits with `ERROR: curl upload failed: Broken pipe`, the re-encoded `.low.mp3` already exists at `/tmp/<stem>.low.mp3`. Re-run the script on that file directly (it's under 12 MB so no re-encode):

```bash
python3 "$SKILL_DIR" "/tmp/<stem>.low.mp3" "/tmp/<stem>.transcript.json"
```

### Step 4: Infer speakers

Read the JSON output. For each unique speaker label (`A`, `B`, `C`, etc.), identify who they are.

#### Known hosts — match from filename first

| Filename pattern | Host |
|---|---|
| `office hours w peter` | Peter Vander Wall |
| `office hours w peter + ryan` | Peter Vander Wall + Ryan Bakke |
| `building a sellable business` | Peter Vander Wall |
| `how to hire an operator` | Peter Vander Wall |
| `fulfillment call` / `marketing + fulfillment` | Peter Vander Wall + Ryan Bakke |
| (generic date only, e.g. `2026-04-22.mp4`) | Unknown until transcript read |

Peter Vander Wall is the default host for most calls. Brian Mayoral runs dedicated sales coaching sessions. Ryan Bakke runs fulfillment coaching.

#### Transcript clues (in priority order)

**HIGH confidence:**
- Direct address: "Hey, Justin" or "So, Cheree" — the person being addressed is that speaker
- Self-introduction: "I'm Brian" / "this is Peter" — that speaker is that person
- Framework names: "Sell Up Download," "Sell Up" — Brian Mayoral's proprietary framework → Speaker is Brian
- "myself, Ryan and Peter" / "my team at Social Club Studios" → Peter or SCS context
- "I got about two months left [in the program]" → a student nearing end of SYAF cohort
- Named role-play: "All right, Justin, you're up" → Justin is the next speaker

**MEDIUM confidence:**
- Revenue / niche match: read SYAF student profiles, cross-reference what the speaker says about their firm (revenue, niche, offer, client count) against intake snapshots
- Recurring patterns: students who ask lots of questions are usually newer; coaches give extended answers and frame concepts

**LOW confidence / UNKNOWN:**
- A speaker appears only briefly with no identifying content — leave as `Unknown / possible silent attendee`

#### After identification, produce for each speaker
- Best-guess name (or UNKNOWN)
- Confidence: HIGH / MEDIUM / LOW / UNKNOWN
- 1–2 supporting quotes from the transcript

### Step 5: Name the transcript file

Use the pattern: `YYYY-MM-DD {Call Type} - {Host}.md`

**Call type conventions:**

| File name pattern | Call Type |
|---|---|
| `office hours w peter` | `Marketing Call` |
| `office hours w peter + ryan` | `Marketing + Fulfillment Call` |
| `building a sellable business` | `Building a Sellable Business` |
| `how to hire an operator` | `How to Hire an Operator` |
| Brian is host (sales coaching) | `Sales Coaching` |
| Onboarding session | `Onboarding Call` |
| Generic / unclear | Use the topic inferred from the first 5 minutes of transcript |

**Host in filename:** Last name(s) only if multiple, or first name if solo is clearer. Examples:
- Peter alone → `- Peter`
- Peter + Ryan → `- Peter + Ryan`
- Brian alone → `- Brian`

Full examples:
- `2026-04-22 Sales Coaching - Brian.md`
- `2026-04-24 Marketing Call - Peter.md`
- `2026-03-20 Marketing + Fulfillment Call - Peter + Ryan.md`

### Step 6: Build the transcript file

Write to `<vault>/Transcripts/<filename>.md`.

```markdown
---
type: transcript
date: YYYY-MM-DD
tags: [transcript]
call_type: "marketing-call | sales-coaching | fulfillment-call | onboarding | other"
host: "Full Name"
students_present: [Student Name, Student Name]
duration_minutes: <int>
related: []
---

## Call Details

| Field | Details |
|-------|---------|
| **Date** | YYYY-MM-DD |
| **Host** | Full Name |
| **Call type** | Human-readable call type |
| **Duration** | ~X minutes |
| **Source** | Drive: `<original filename>` |

## Students Mentioned

- [[Student Profile Wikilink]] — 1–2 sentence summary of what they discussed on this call

**Approximate time-in-call by speaker** (for navigation):

| Speaker | First | Last | Turns |
|---|---|---|---|
| Name | MM:SS | MM:SS | N |

## Summary

[2–5 paragraphs. Cover each student's segment with timestamps. Note key coaching moments, decisions made, and anything that will show up in action items. Write for someone who needs to know what happened without watching the recording.]

## Action Items

- **[Name]:** [action item]
- **[Name]:** [action item]

## Speaker Guesses

### Speaker A
- **Identity:** [Name or UNKNOWN]
- **Confidence:** HIGH | MEDIUM | LOW | UNKNOWN
- **Evidence:** [quote or reasoning]

[repeat for each speaker]

## Transcript

[Full transcript with mapped speaker names in format:]

[Full Name]
(MM:SS) Utterance text

[Full Name]
(MM:SS) Utterance text
```

**Speaker format in Transcript section:** Each utterance on two lines — `[Full Name]` then `(MM:SS) text` — with a blank line between utterances. Use confirmed names, not `[Speaker A]`.

### Step 7: Update student profiles

For every student mentioned in the call (not coaches), append a coaching log entry to their profile at `<vault>/Students/<student file>.md`.

Follow the existing coaching log format exactly:

```markdown
### YYYY-MM-DD — {Call Type} ({Coach First Name})

**Context:** [1 sentence: what call was this, why was this student there]

**Discussion:**
- [bullet 1]
- [bullet 2]
- [bullet 3]

**Action items:**
- [ ] [item for this student]

**Coach notes:** [1–2 sentences of team-facing observation — is momentum up/down, any red flags, what to watch next call]

*Source: [[YYYY-MM-DD {Call Type} - {Host}]]*
```

Then add the new transcript to the student's `## Source Meetings` section.

**What to write for students who are silent attendees** (on the call but didn't speak): note them in the transcript's `## Students Mentioned` section but skip the coaching log entry. Don't log "so-and-so was present but said nothing."

### Step 8: Notify

Tell the user:
- Transcript file path
- **Suggested Skool replay title** (formatted per Step 9)
- Speaker guesses (name + confidence, one line each)
- Which student profiles were updated
- Any action items flagged

### Step 9: Skool replay title + open for posting

**First, generate the Skool replay title.** Every call posted in the cohort's Skool classroom uses this exact title format:

`<Topic> w <Host first name> | YYYY-MM-DD`

Rules:
- **≤ 50 characters total** — Skool's hard title cap. The ` w <Host> | YYYY-MM-DD` suffix eats ~20–21 chars, so keep the Topic to ~28–30 chars. Count the full string before finalizing.
- **Host** = first name only — `Peter`, `Ryan`, or `Brian` (whoever hosted). Use `Peter + Ryan` only if both genuinely co-hosted and it still fits ≤50.
- **Date** = the true date the call happened, in `YYYY-MM-DD` — use the real call date even if the recording filename is misdated.
- **Topic** = a punchy, benefit/topic-forward phrase capturing the call's main theme or signature framework (name the framework when there is one). No surrounding quotes, no trailing punctuation.

Examples:
- `AI Lead-Gen & Niche Strategy w Peter | 2026-05-29`
- `The Nighthawk Role & SOPs w Ryan | 2026-05-27`
- `Get 30 Referrals in 30 Days w Brian | 2026-06-03`
- `The Hunter/Gatherer Model w Ryan | 2026-05-18`

**Then open the transcript** so the user can copy the relevant sections into the Skool client portal:

```bash
open "<vault>/Transcripts/<filename>.md"
```

Tell the user:

> Transcript is open. Post the replay in this cohort's Skool classroom using the title above, and copy the **Summary** and **Action Items** sections into the post body.

If multiple transcripts were processed (catch-up mode), open each one and list them — each with its own Skool replay title.

---

## Speaker Reference (known SYAF regulars)

Keep this updated as new recurring attendees appear:

| Name | Role | Tells |
|---|---|---|
| **Peter Vander Wall** | CEO, SCS — SYAF marketing coach | "Social Club Studios," "scaling with ads," addresses student questions on marketing/funnel/content |
| **Brian Mayoral** | Co-founder, Sell Up — SYAF sales coach | "Sell Up Download," "pull cash forward," runs role-play sessions, mentions "Sell Up" framework by name |
| **Ryan Bakke** | Co-founder, TS365 — SYAF fulfillment coach | Tax strategy language, mentions TS365, fulfillment / service delivery topics |
| **Zach** | Community manager | Check-ins, accountability, admin |

---

## Failure Modes

- **`curl upload failed: Broken pipe`** — re-encoded file already exists at `/tmp/<stem>.low.mp3`. Re-run the script on that file directly.
- **Google Drive MCP auth error** — the user needs to reconnect their Google Drive in Cowork settings. If running outside Cowork, fall back to `gws auth login`.
- **AssemblyAI `speech_model` error** — if the API returns an error about `speech_model`, verify the script uses `speech_models` (plural, list) not `speech_model` (singular string). The `/v2` endpoint requires the list form.
- **Speaker with zero lines** — AssemblyAI sometimes creates a speaker label for a brief cough or background noise. If a speaker has <3 utterances totaling <10 words, they're likely ambient noise — note as `(ambient / unclear)` and exclude from student update.
- **Duplicate date in Transcripts folder** — if a transcript already exists for the same date, check whether it's a different call type (e.g., both an office hours and a separate onboarding call on the same day). Use a distinguishing suffix: `2026-04-07 Onboarding Call - Peter (2).md`.
- **Student not in vault** — if a speaker is clearly a SYAF student but has no profile in `<vault>/Students/`, flag it to the user: "Found a student named [X] on this call with no profile. Should I create one?"
- **ffmpeg not installed** — tell the user: "ffmpeg is required to process large recordings. Install it with `brew install ffmpeg`."

---

## Connections

- Transcription script: `scripts/transcribe.py` (bundled with this skill)
- SYAF vault conventions: `<vault>/AGENTS.md`
- Related skills: `transcribe-video` (general-purpose transcription with inbox gate), `process-syaf-call` (process a transcript you already have)

---
name: process-syaf-call
description: Process a SYAF coaching call transcript — saves raw transcript, updates each student's profile with coaching log entries, wins, flags, and action items. Triggers on "process this call", "SYAF transcript", "process coaching call", "update student notes from call".
---

# Process SYAF Call Transcript

Take a coaching call transcript from Scale Your Accounting Firm (SYAF) and process it into the student intelligence vault.

### SYAF vault path (portable)

Check these paths in order and use the first that exists:
1. `~/obsidian/syaf/`
2. `~/obsidian/syaf_brain/`
3. `~/Documents/obsidian/syaf/`
4. `~/Documents/obsidian/syaf-brain/`

If none exist, stop and tell the user:

> SYAF vault not found. Clone it locally:
> ```
> mkdir -p ~/obsidian && cd ~/obsidian && gh repo clone petervndr/syaf-brain syaf
> ```
> Then rerun this command.

---

## Config

| Key | Value |
|-----|-------|
| **Vault path** | `<vault>` (see portable path discovery above) |
| **Students folder** | `<vault>/Students/` |
| **Transcripts folder** | `<vault>/Transcripts/` |
| **Maps folder** | `<vault>/Maps/` |
| **Coach names (exclude from student matching)** | Peter, Brian, Ryan, Zach, Cassidy, Kristin, Mckenzie, Sittie |
| **Granola MCP tools** | `mcp__claude_ai_Granola__list_meetings`, `mcp__claude_ai_Granola__get_meeting_transcript` |

---

## Input

The user provides a call transcript in one of three ways:

1. **Pasted text** — transcript is directly in the user's message
2. **File path** — user provides a path to a `.md`, `.txt`, or `.csv` file. Read it with the Read tool.
3. **Granola meeting** — user says "process the Granola call from today" or similar. Use the Granola MCP tools to fetch it.

If the input method is ambiguous, ask.

---

## Processing Pipeline

### Step 1: Acquire Transcript

Read the transcript from the provided source. Store the full raw text.

### Step 2: Extract Metadata

Determine the following from the transcript content, filename, Granola metadata, or user context:

| Field | How to determine |
|-------|-----------------|
| **Date** | Parse from transcript, filename, or Granola metadata. If ambiguous, default to today. |
| **Call type** | `group-coaching` (multiple students, hosted by Peter/Brian/Ryan), `onboarding` (Zach + 1 student, first call), `check-in` (Zach + 1 student, follow-up). Default to `group-coaching` if unclear. |
| **Host** | The coach who ran the call. Infer from the first coach name appearing as a speaker. |
| **Call topic** | `Marketing Call`, `Sales Call`, `Fulfillment Call`, `Onboarding Call`, `Check-in Call`. Infer from host: Peter → Marketing, Brian → Sales, Ryan → Fulfillment, Zach → Onboarding or Check-in. |

### Step 3: Build Student Roster

List all files in `<vault>/Students/` using the Glob tool with pattern `*.md`.

Parse each filename into match tokens:
- Filename format: `{First} {Last} - {Firm Name}.md`
- Extract: `first_name`, `last_name`, `firm_name`, `full_path`

This roster is used for matching in Step 4.

### Step 4: Identify Students

Scan the transcript for student matches:

1. **Speaker labels** — look for patterns like `Name:`, `**Name**:`, or `[Name]` at the start of lines. Match each against the roster by first name (case-insensitive).
2. **Body mentions** — scan the full text for first names, last names, or firm names from the roster. Only count as "mentioned" if there is substantive discussion about them (not just a passing reference like "like what Colin did").

Produce two lists:
- `students_speaking` — students who had speaker labels in the transcript
- `students_mentioned_only` — students discussed but not speaking

**Exclude** all coach names from matching (see Config table above).

If a speaker cannot be matched to any student or coach, add to `unmatched_speakers` list.

### Step 5: Save Transcript Note

Create a new file using the Write tool:

**Path:** `<vault>/Transcripts/{YYYY-MM-DD} {Call Topic} - {Host}.md`

Examples:
- `2026-04-07 Marketing Call - Peter.md`
- `2026-04-10 Onboarding Call - Zach.md`
- `2026-04-15 Check-in Call - Zach.md`

If a file already exists at that path, append ` (2)` before `.md` and warn the user.

**Content:**

```markdown
---
type: transcript
date: {YYYY-MM-DD}
tags: [transcript]
call_type: "{group-coaching|onboarding|check-in}"
host: "{Host}"
students_present: [{list of first names}]
related: []
---

## Call Details

| Field | Details |
|-------|---------|
| **Date** | {YYYY-MM-DD} |
| **Host** | {Host} |
| **Call type** | {Call Topic} |
| **Duration** | {if known, otherwise "Unknown"} |

## Students Mentioned

{Wikilinks to each student note, one per line, prefixed with bullet}
- [[{First} {Last} - {Firm Name}]]

## Transcript

{Full raw transcript pasted here}
```

### Step 6: Analyze Per Student

For each identified student (both speaking and mentioned-only), extract:

- **What they discussed** or what was discussed about them
- **Coaching advice** given to them by the host
- **Action items** assigned to them (explicit tasks, not vague suggestions)
- **Wins** — closed a client, revenue milestone, launched something, got a referral, first discovery call, hired someone, specific result from coaching advice
- **Flags** — no progress across 2+ calls, overwhelmed/stuck/confused, mentioned canceling, missed calls/went silent, revenue declined, avoiding action items

**Classification rules:**
- Only elevate to Win or Flag when there is clear evidence in the transcript
- Ambiguous = stays in Coaching Log discussion only
- Do NOT infer sentiment — use what was actually said

### Step 7: Update Student Notes

For each student, use the Read tool to load their current note, then use the Edit tool to update the following sections.

**IMPORTANT:** Use the Edit tool to append content. Find the section header and append after the existing content in that section (before the next `##` header). Do NOT overwrite existing entries.

#### a) Coaching Log (group calls only)

Append under `## Coaching Log`:

```markdown
### {YYYY-MM-DD} — {Call Topic} ({Host})

**Context:** {1 sentence — what brought this student up on the call}

**Discussion:**
- {Factual bullet points — what student said, what coach advised}
- {Include specific numbers, names, frameworks referenced}

**Action items:**
- [ ] {Specific task}

{Only include the following line if there are notable soft observations:}
**Coach notes:** {Optional — soft observations about engagement, confidence, sentiment}

*Source: [[{YYYY-MM-DD} {Call Topic} - {Host}]]*
```

If the student was discussed but did NOT speak, the Context line should say: "Discussed by {Host} — {Student first name} was not on the call."

#### b) Zach Check-ins (Zach's 1-on-1 calls only)

Append under `## Zach Check-ins` instead of Coaching Log:

```markdown
### {YYYY-MM-DD} — {Onboarding Call | 30-day check-in | 60-day check-in | 90-day check-in}
- **Sentiment:** {Positive | Neutral | Concerned}
- **Summary:** {2-3 sentences on what was discussed}
- **Action items:** {bulleted list, or "None"}
- **Feedback:** {Any complaints, praise, or suggestions the student shared about the program — quote directly when possible}
- **Next check-in:** {date if mentioned, otherwise "TBD"}

*Source: [[{YYYY-MM-DD} Check-in Call - Zach]]*
```

#### c) Wins

If a win was identified, append under `## Wins`:

```markdown
- **{YYYY-MM-DD}** — {Description of the win} (from [[{YYYY-MM-DD} {Call Topic} - {Host}]])
```

#### d) Flags & Concerns

If a flag was identified, append under `## Flags & Concerns`:

```markdown
- **{YYYY-MM-DD}** — {Description of the concern} (from [[{YYYY-MM-DD} {Call Topic} - {Host}]])
```

Do NOT remove old flags. If an old flag is resolved, append a resolution note on a new line below it.

#### e) Current Focus

Update ONLY if the student or coach explicitly stated a new focus. Look for phrases like:
- "For the next few weeks, focus on..."
- "My priority right now is..."
- "Let's have you work on..."

If updating, replace the content under `## Current Focus` (do not append — this section is current state, not a log).

If nothing explicit was stated, do NOT touch this section.

#### f) Source Meetings

Append under `## Source Meetings`:

```markdown
- [[{YYYY-MM-DD} {Call Topic} - {Host}]]
```

### Step 8: Handle Unknown Speakers

If any speakers could not be matched to a student or coach:

- Do NOT create a new student note (student notes require onboarding form data)
- List them in the summary report as "Unmatched Speakers"
- Suggest: "If this is a new student, create their note first using the onboarding form, then rerun this skill."

### Step 9: Update Map (conditional)

Only update `Maps/Map - All Students.md` if:
- A student's status changed (e.g., refunded, re-activated)
- A new student note was created in a separate step before this run

Do NOT update the map's Quick Stats after every call — that would be noisy. Stats are updated manually or during periodic reviews.

### Step 10: Print Summary

Output to chat:

```markdown
## Call Processed

**Date:** {YYYY-MM-DD}
**Type:** {Call Topic}
**Host:** {Host}
**Transcript saved:** [[{YYYY-MM-DD} {Call Topic} - {Host}]]

### Students Updated ({count})
- [[{Student Name} - {Firm}]] — {what was updated: coaching log, win, flag, current focus}

### Wins ({count})
- **{Student first name}** — {win description}

### Flags ({count})
- **{Student first name}** — {flag description}

### Action Items ({count})
- **{Student first name}** — {action item}

### Unmatched Speakers ({count})
- {name} — create a student note and rerun, or ignore if not a student
```

If there are no wins, flags, or unmatched speakers, show "None" for that section.

---

## Rules

1. **Use Write tool for new files, Edit tool for updates** — never use Obsidian MCP tools
2. **Never modify Intake Snapshot** — that section is set from the onboarding form and never changes
3. **Never delete existing entries** — only append. Old flags stay; add resolution notes below them.
4. **Quote when revealing** — if a student said something telling, quote it in the Discussion bullets rather than paraphrasing
5. **Be specific with numbers** — "$2K/mo client" not "new client", "3 discovery calls this week" not "getting some calls"
6. **One coaching log entry per student per call** — even if they came up multiple times, consolidate into one entry
7. **Wikilinks everywhere** — every reference to a student or transcript uses `[[wikilinks]]`
8. **Coach notes are optional** — only include if there's a genuine soft observation worth recording. Most entries won't have this field.
9. **Action items must be specific** — "work on marketing" is not an action item. "Record 3 short-form videos about tax planning by Friday" is.
10. **Passing mentions are not entries** — if a student's name comes up only in passing ("like what Colin did last week"), do not create a Coaching Log entry for them unless there is substantive discussion or coaching content about them
11. **Never invent firm names** — if a student's firm name is unknown, use just `{First} {Last}.md` for the filename and leave the `firm` field empty in frontmatter. Do not guess or make up a business name.
12. **Always include the full transcript** — the transcript note must contain the complete raw transcript text in the `## Transcript` section. Never use placeholders, file path references, or "omitted for space" comments. The vault is the source of truth.

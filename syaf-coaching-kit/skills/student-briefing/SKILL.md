---
name: student-briefing
description: Quick student status briefing before a call — pulls current focus, recent coaching history, open action items, wins, and flags from the SYAF vault. Triggers on "how's [name] doing", "brief me on [name]", "student briefing", "prep for call with [name]".
---

# SYAF Student Briefing

Pull a concise, actionable briefing on a SYAF student from the Obsidian vault at `~/Documents/obsidian/syaf-brain/`. Designed for Zach (community manager) or any coach to review before a call.

If that directory doesn't exist on this machine, stop and tell the user:

> SYAF vault not found at `~/Documents/obsidian/syaf-brain/`. Clone it locally first:
> ```
> mkdir -p ~/Documents/obsidian && cd ~/Documents/obsidian && gh repo clone petervndr/syaf-brain
> ```
> Then rerun this command.

---

## Config

| Key | Value |
|-----|-------|
| **Vault path** | `~/Documents/obsidian/syaf-brain/` |
| **Students folder** | `~/Documents/obsidian/syaf-brain/Students/` |

---

## Input

The user provides a student name. It can be:
- First name only ("how's Kerrie doing?")
- Full name ("brief me on Kerrie Spain")
- Partial match ("prep for call with Peyton")

If ambiguous (multiple matches), list the options and ask which one.

---

## Process

### Step 1: Find the student note

Use Glob to search `~/Documents/obsidian/syaf-brain/Students/` for files matching the name. Match on first name, last name, or firm name from the filename. Case-insensitive.

If no match, say so and list all student files so the user can pick.

### Step 2: Read the student note

Use the Read tool to load the full note.

### Step 3: Generate the briefing

Output a structured briefing in this exact format:

```
## [Student Name] — [Firm Name]

**Status:** [active/refunded]
**Coach:** [assigned coach]
**Revenue:** [from frontmatter or intake]
**Niche:** [from frontmatter]
**Member since:** [join_date]

---

### Current Focus
[Contents of ## Current Focus section — copy verbatim, this is what they should be working on RIGHT NOW]

---

### Last Coaching Interaction
[Most recent entry from ## Coaching Log OR ## Zach Check-ins, whichever is more recent]
- **Date:** [date]
- **Call:** [call name from the entry header]
- **Summary:** [2-3 sentence summary of the discussion]
- **Open action items:** [list any unchecked items from that entry — items with `- [ ]`]

---

### Recent Wins
[Last 3 entries from ## Wins, or "None yet" if empty]

---

### Active Flags
[All entries from ## Flags & Concerns, or "None" if empty]

---

### Zach Check-in History
[All entries from ## Zach Check-ins, or "No check-ins yet — this will be the first"]

---

### Suggested Talking Points
[Generate 2-4 specific talking points based on the briefing above. These should be things Zach can bring up naturally in conversation:]
- [Based on open action items: "Ask if she's watched the Brock workshop yet"]
- [Based on flags: "Check in on how the client payment issue resolved"]
- [Based on current focus: "See if she's started posting content yet"]
- [Based on time since last interaction: "It's been X weeks since her last call — ask what she's been working on"]
```

---

## Rules

1. **Keep it scannable** — Zach should be able to read this in 60 seconds before a call
2. **Copy Current Focus verbatim** — don't summarize it, that section is already concise
3. **Only show unchecked action items** — checked items (`- [x]`) are done, skip them
4. **Suggested talking points must be specific** — not generic ("ask how things are going"). Reference actual content from their note.
5. **If the student has no coaching log entries**, say "No coaching history yet — this is their first interaction" and suggest pulling up their Intake Snapshot to review their situation
6. **Calculate days since last interaction** — use the date from the most recent coaching log or check-in entry compared to today's date. Flag if it's been more than 30 days.
7. **For multi-student briefings** — if the user asks for multiple students ("brief me on my calls today"), run the briefing for each student sequentially

---

## Example Output

```
## Savannah Arrington — Cypress Bookkeeper

**Status:** Active
**Coach:** Brian (Sales), Peter (Marketing)
**Revenue:** $25,000
**Niche:** Specialty medical + law firms
**Member since:** 2026-02-09

---

### Current Focus
Create short-form content showcasing the client dashboard to get in front of specialty medical and law firm prospects. Focus on pain-point-specific videos (one topic per video), not VSL or CRM setup yet.

---

### Last Coaching Interaction
- **Date:** 2026-04-04 (3 days ago)
- **Call:** Marketing Call (Peter)
- **Summary:** Presented her Claude-built client dashboard — first student to ship one. Peter coached on content strategy: use the dashboard as content, one pain point per video, flip-camera format. Pointed to Short Form Content Playbook.
- **Open action items:**
  - [ ] Identify 3-5 more dashboard-aligned pain points
  - [ ] Go through the Short Form Content Playbook in School
  - [ ] Start posting short-form content daily
  - [ ] Connect dashboard to QuickBooks sandbox

---

### Recent Wins
- **2026-04-04** — Built a full client dashboard using Claude Code (first SYAF student to ship one)

---

### Active Flags
- Very early stage — $25K, 5 clients
- No niche (now resolved — specialty medical + law firms)
- Low pricing ($350-$500)

---

### Zach Check-in History
No check-ins yet — this will be the first.

---

### Suggested Talking Points
- Ask if she's started posting short-form content yet (main action item from last call)
- Ask if she connected the dashboard to a QuickBooks sandbox for demos
- This is the first check-in — ask what she likes most about the program so far and if anything is unclear
- Her pricing is low ($350-$500/mo) — if she mentions money stress, it's a known issue the coaches are working on
```

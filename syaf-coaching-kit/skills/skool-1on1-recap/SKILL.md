---
name: skool-1on1-recap
description: Generate a Skool community post recapping an intro advisory call with a new SYAF Accelerator member. Takes a call transcript, extracts firm details and the tactical moves Peter gave the student, and outputs a ready-to-paste post that serves both the named student and the broader group. Use when Peter pastes an intro advisory call transcript or says "recap this 1-on-1", "skool post from this call", "intro advisory recap", "skool-1on1-recap", "write up [name]'s intro call for school", or "post the recap from my call with [name]".
---

# Skool 1-on-1 Recap

Turn an intro advisory call transcript into a Skool community post that recaps the call for the named student AND helps the broader SYAF Accelerator group pull tactical value out of it.

## When to use this skill

- Peter just finished an intro 1-on-1 advisory call with a new member of the SYAF Accelerator
- The deliverable is a Skool community post (not a private summary)
- Student is being tagged and named publicly

For other SYAF call types (group coaching, ongoing 1-on-1s, Zach check-ins), use `process-syaf-call` instead.

---

## SYAF vault path (portable)

Check these paths in order and use the first that exists:

1. `~/obsidian/syaf/`
2. `~/Documents/obsidian/syaf/`
3. `~/Documents/obsidian/syaf-brain/`

If none exist, skip the vault filing steps and warn the user that the transcript and post archive copy couldn't be saved. Still produce the post in chat.

---

## Voice principles

Before drafting the post, read Peter's voice principles file from this skill's `references/voice-principles.md`.

This is required, not optional. The post output must comply with everything in that file. Specifically banned in the output:

- Em dashes (use commas, colons, or periods instead)
- "dive into," "game-changing," "straightforward," "leverage," "synergize," "circle back," "touch base"
- Fragment question setups ("The best part?", "The wild thing?", "The scary truth?")
- Hidden truth reveals ("Here's what nobody tells you...", "No one's saying this out loud, but...")
- Flip contrasts ("It's not X, it's Y")
- Poetic reductions ("Leadership isn't control, it's clarity")
- Balanced reframes ("Everyone's chasing X, few are doing Y")
- Sentences starting with "I think" or "I believe" when stating something directly
- Paragraphs longer than 3 sentences

---

## Config

| Key | Value |
|-----|-------|
| **Vault path** | `<vault>` (see portable path discovery above) |
| **Transcripts folder** | `<vault>/Transcripts/` |
| **Skool posts folder** | `<vault>/Skool Posts/` (create if missing) |
| **Coach names (exclude from speaker matching)** | Peter, Brian, Ryan, Zach, Cassidy, Kristin, Mckenzie, Sittie |
| **Default tactical move count** | 3 (allow 2 if the call only covered two themes, 4 only if unusually broad) |
| **Target post length** | 350-500 words |
| **Voice file** | `references/voice-principles.md` (bundled with this skill) |

---

## Input

The user provides:

1. **The transcript** — pasted directly into the message, or as a file path to `.md`/`.txt`
2. **(Optional) student's Skool @ handle** — for the tag. If not provided, ask.

If the user triggers the skill with a student name but no transcript, ask for the transcript before proceeding.

---

## Pipeline

### Step 1: Read voice principles

Use the Read tool to load `references/voice-principles.md` (relative to this skill's folder). Hold this in working memory for Step 6 (drafting) and Step 7 (scrub).

### Step 2: Acquire transcript

Read the transcript from the provided source. Store the full raw text.

### Step 3: Extract metadata

Parse the transcript to identify:

| Field | How to determine |
|-------|-----------------|
| **Call date** | From transcript header, filename, or message context. Default to today if not stated. |
| **Student name** | First non-coach speaker who introduces themselves or whose firm is being discussed. Exclude coach names (see Config). |
| **Firm name** | From the student's intro of their business. |
| **Other attendees** | Team members, partners, or vendors on the call. Note them for context but the post is about the student. |

### Step 4: Confirm student and handle

If the student's Skool handle wasn't provided in the input, ask:

> "Got the call with {Student Name} from {Firm}. What's their Skool @ handle for the tag?"

Wait for the user's reply before drafting.

### Step 5: Extract intro session content

Pull the following from the transcript:

**Firm snapshot:**

- Firm name and year founded (if stated)
- Current stage: revenue, client count, or team size
- What they offer / what they're built around
- Team members mentioned on the call

**Current focus and situation:**

- What they're trying to push or grow next
- Where they're stuck or what they came to the program to solve
- Constraints they mentioned (small team, no time for social, prefers async, etc.)

**Tactical moves Peter gave them:**

- Look for explicit recommendations: phrases like "first thing I'd be doing," "I would do X," "what I would recommend is Y," "go talk to Brian about Z"
- Extract 3 moves by default. Use 2 if the call only covered two themes. Use 4 only if the call was unusually broad.
- For each move, capture: what to do, and why it matters for this student specifically

**Generalizable lessons:**

- Identify 2-4 principles Peter taught that apply to anyone in a similar spot
- Each should be one-sentence-able and useful even without firm context

**Next step:**

- Specific commitment or scheduled follow-up (e.g., "workshop with Brian tomorrow," "come to Friday office hours")

### Step 6: Draft the post

Follow this template exactly:

```markdown
**Title:** Welcome @{handle}: first {N} moves from your intro call

**Body:**

Just wrapped my intro advisory call with @{handle} of {Firm Name}. Quick recap for {First name}, plus a few things the rest of you can borrow.

**Meet {First name}**

- Firm: {Firm name}{, founded {year} if known}
- Stage: {revenue, client count, or team scale}
- Built around: {what their offer is}
- Team: {1-3 key team members if mentioned on the call}

**Where {First name} is focused right now**

{2-4 sentences. Describe the situation, what they're trying to push, what's pulling them in different directions, and what they came to the program to solve. Written so other members can read it and self-identify.}

**The first {N} tactical moves I gave {First name}**

1. **{Move headline.}** {2-4 sentences. State what to do and why it matters for where they specifically are. Include relevant specifics from the call (names of frameworks, internal people they should talk to, etc.).}

2. **{Move 2 headline.}** {Same structure.}

3. **{Move 3 headline.}** {Same structure.}

**If you're in a similar spot**

- **{Lesson 1 headline.}** {1 sentence elaborating the principle.}
- **{Lesson 2 headline.}** {1 sentence.}
- **{Lesson 3 headline.}** {1 sentence.}

**Next step for {First name}:** {specific commitment from the call}
```

Drafting rules:

- Use the student's first name once introduced; don't repeat the full name
- Bold the headline of each tactical move and each lesson
- Each tactical move: 2-4 sentences. Each lesson: 1 sentence.
- Vary sentence length within paragraphs
- Use connectors like "so," "because," "for example"
- Do NOT add a separate "action items" bullet list; weave the action into each move's paragraph
- Do NOT add a closing line beyond the "Next step" anchor

### Step 7: Banned pattern scrub

Before showing the post to the user, scan and rewrite any of:

- Em dashes (replace with commas, colons, or periods)
- Any banned word or phrase from voice-principles.md
- Fragment question setups
- Hidden truth reveals
- Flip contrasts ("not X, but Y")
- Poetic reductions and balanced reframes
- Any paragraph longer than 3 sentences

If any banned pattern survives, rewrite that sentence before output.

### Step 8: File the transcript

Save the raw transcript to the SYAF vault for searchability and downstream processing:

**Path:** `<vault>/Transcripts/{YYYY-MM-DD} Intro Advisory - {First Name} {Last Name}.md`

**Content:**

```markdown
---
type: transcript
date: {YYYY-MM-DD}
tags: [transcript, intro-advisory]
call_type: "intro-advisory"
host: "Peter"
student: "{First Name} {Last Name}"
firm: "{Firm Name}"
related: []
---

## Call Details

| Field | Details |
|-------|---------|
| **Date** | {YYYY-MM-DD} |
| **Host** | Peter |
| **Call type** | Intro Advisory |
| **Student** | {First Name} {Last Name} ({Firm Name}) |
| **Attendees** | {Other attendees if any, otherwise "None"} |

## Transcript

{Full raw transcript pasted here}
```

If a file already exists at that path, append ` (2)` before `.md` and warn the user.

If the vault isn't mounted, skip this step and note it in the summary.

### Step 9: Save the post

Save the drafted post to:

**Path:** `<vault>/Skool Posts/{YYYY-MM-DD} Intro Advisory Recap - {First Name}.md`

Create the `Skool Posts` folder if it doesn't exist.

If the vault isn't mounted, save the post to the current Cowork outputs directory and provide a `computer://` link in the summary.

### Step 10: Present to user

Output to chat:

```markdown
## Skool post ready

**Student:** {First Name} {Last Name} ({Firm Name})
**Date:** {YYYY-MM-DD}
**Word count:** ~{count}

**Post archived:** {link or path}
**Transcript filed:** [[{YYYY-MM-DD} Intro Advisory - {First Name} {Last Name}]] (or "not filed, vault not mounted")

---

{Full post content here, formatted for easy copy-paste into Skool}

---

Anything to tweak before you paste it in?
```

---

## Rules

1. **Voice principles are non-negotiable.** The post must pass the banned-pattern scrub in Step 7. If a banned pattern slips through, rewrite before showing to the user.
2. **Use the avatar's words.** If the call surfaces real client-language phrases the student or Peter said (like "I quoted this job wrong," "my profit per project is all over the place"), use them verbatim in the post. They're worth more than any rewrite.
3. **3 moves is the default.** Use 2 only if the call genuinely covered two themes. Use 4 only if the call was unusually broad.
4. **First name only after first use.** Avoid corporate-feeling repetition of full names throughout the post.
5. **Never include sensitive details.** Skip exact client names the student mentioned, internal financials they wouldn't want public, or anything said in confidence. When in doubt, generalize or omit.
6. **The post must stand on its own.** Other members reading it cold should be able to extract real value without needing the transcript.
7. **No emojis** unless Peter explicitly asks for them.
8. **Tag the student in both the title and the opening line.** Both should include the `@handle`.
9. **One Skool post per intro call.** Follow-up calls with the same student are not this skill's job; use `process-syaf-call` for ongoing coaching updates.
10. **Don't touch the student's vault note.** Updating coaching logs is `process-syaf-call`'s job. This skill files the transcript copy and produces the post only.
11. **Never invent details.** If the firm's founding year, revenue, or team size wasn't stated on the call, leave it out instead of guessing.
12. **Hold the line on word count.** If the draft runs over 500 words, tighten before presenting. Skool engagement drops fast past that.

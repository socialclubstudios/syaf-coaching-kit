# Load Client Brain (Shared Reference)

Used by: client-intake-brief, positioning-guide, vsl-writer, method-vsl, offer-creation, ad-scripts, ad-body-copy, welcome-sequence, reactivation-sequence, proof-stack-sequence, sales-assets, faq-scripts, testimonial-questions, cp1-generator, cp2-generator.

## What this is

Every SCS client has a knowledge folder in the shared Obsidian vault at `~/obsidian/scs_team/Knowledge/Clients/[Client Name]/`. This folder holds accumulated team intelligence on that client — voice card, ICP notes, proven angles, open flags, recent wins, and deliverables from earlier pipeline runs.

Before generating anything for a named client, check this folder. Layering in the latest team intel makes your output match what the team already knows, not just what was captured in the original intake.

The `~/` prefix is important — it's portable across machines. Any team member with the `scs_team` vault cloned to `~/obsidian/scs_team/` gets the same behavior. Do NOT use absolute paths like `/Users/petervndr/obsidian/...`.

## The read pattern

### Step 1: Build the folder path

```
~/obsidian/scs_team/Knowledge/Clients/<Client Name>/
```

`<Client Name>` matches the Google Drive folder format (e.g., `Tax Strategy 365`, `GTG Tax`). Case matters. Use the firm name, not the firm-name-and-owner-name `//` format.

### Step 2: Check if the folder exists

```bash
CLIENT_BRAIN="$HOME/obsidian/scs_team/Knowledge/Clients/<Client Name>"
if [ -d "$CLIENT_BRAIN" ]; then
  echo "Brain found — loading"
  ls "$CLIENT_BRAIN"
else
  echo "No brain folder — skipping, will rely on other inputs"
fi
```

### Step 3: Read the contents

If the folder exists:
1. List all `.md` files in the folder.
2. Read the main client note first (usually `<Client Name>.md`).
3. Read any subnotes (testimonials, angles, positioning notes, session recaps).

Do NOT descend into unrelated subdirectories — stick to the client's folder and direct children.

## What to prioritize

The client note in Obsidian typically includes these sections. Treat each as signal:

| Section | Why it matters |
|---|---|
| **Voice card** | KEEP/TRANSLATE/DROP rules — authoritative over anything in a brain-dump brief |
| **ICP / Avatar** | Refined avatar, often narrower than the initial intake |
| **Approved angles** | What's tested, landing, and safe to echo |
| **Open flags** | Client-specific watch-outs (things that bombed, sensitive topics, compliance issues) |
| **Recent wins** | New testimonials, case studies, or dollar results since the last pipeline run |
| **Content pillars** | Approved pillars from positioning — already reviewed by Kristin |
| **Source Meetings** | Granola transcript links for recent calls — use for freshest voice/tone |

## Conflict resolution

If the Obsidian note says one thing and an older Drive doc (e.g., an unrevised positioning guide) says another, **prefer the Obsidian version**. It's been curated by the team after review. When you surface output to the user, flag the discrepancy explicitly so they know the brain overrode the older doc.

Example:
> Note: I used the voice card from the Obsidian client note, which differs from the voice card in the original brain-dump brief. If the older version was intentional, let me know.

## What NOT to do

- **Don't write to the vault.** This pattern reads only. Writing deliverables back into Obsidian is the job of `client-knowledge-sync` and `cp1-knowledge-sync`.
- **Don't fail hard if the vault isn't present.** Team members without the vault cloned should still be able to run the skill — just skip Step 0 and continue.
- **Don't hardcode `/Users/petervndr/...`.** Always use `~/` or `$HOME`.
- **Don't load the full vault.** Only the specific client's folder. Reading `Knowledge/Clients/` as a whole will dump 50+ client notes into context for no reason.

## Insertion snippet for individual skills

Paste this as **Step 0** at the top of the skill's workflow, before any existing "Inputs" or "Step 1" section:

```markdown
## Step 0: Load Client Brain (Obsidian)

Before gathering other inputs, check for existing team intelligence on this client in the shared Obsidian vault:

1. Build the path: `~/obsidian/scs_team/Knowledge/Clients/<Client Name>/`
2. If it exists, list the folder and read the main client note plus any subnotes. Treat voice card, approved angles, open flags, and recent wins as authoritative — they reflect the team's latest thinking.
3. If it doesn't exist, skip silently and continue with the normal input flow.

See [`../_shared/load-client-brain.md`](../_shared/load-client-brain.md) for the full pattern, including conflict resolution rules and what sections to prioritize.
```

# SYAF Coach Setup

Two pieces: the **student brain** (an Obsidian vault) and the **coaching plugin** for Claude Code. Do **Part 1 first** — the plugin reads and writes to the vault, so the vault has to exist locally before the tools are useful.

---

## Part 1 — The SYAF student vault

The vault is a private GitHub repo (`petervndr/syaf-brain`) that syncs straight into Obsidian. Edit a note locally and it pushes to GitHub; Peter's updates pull down automatically.

### 1. Prerequisites
- **Obsidian** — download from https://obsidian.md/download
- **Git** — open Terminal and run `git --version`. If it's missing, run `xcode-select --install` and accept the prompt.
- **A GitHub account**, and accept the invite to `petervndr/syaf-brain` (check your email, or open https://github.com/petervndr/syaf-brain — you'll see you've been added).

### 2. Connect Git to GitHub (so you can pull *and* push)
Easiest path is the GitHub CLI:
```bash
brew install gh        # no Homebrew yet? install it first: https://brew.sh
gh auth login          # choose: GitHub.com → HTTPS → Login with a web browser
```
That stores your credentials so `git pull`/`push` just work.
*(Alternative: create a Personal Access Token with `repo` scope at https://github.com/settings/tokens and paste it when git asks for a password.)*

### 3. Clone the vault to the exact path the tools expect
```bash
mkdir -p ~/Documents/obsidian
git clone https://github.com/petervndr/syaf-brain.git ~/Documents/obsidian/syaf-brain
```
> ⚠️ **Clone it — do not use GitHub's "Download ZIP."** A ZIP has no Git history, so it can never sync. It has to be a `git clone`.

### 4. Open it as a vault in Obsidian
- Obsidian → **Open folder as vault** → select `~/Documents/obsidian/syaf-brain`.
- When prompted, **Trust author & enable plugins** (the vault ships with the Git plugin pre-configured).
- If community plugins are off: Settings → **Community plugins** → turn off **Restricted Mode**.

### 5. Turn on auto-sync
- Settings → **Community plugins** → make sure **Git** is enabled. (If Obsidian offers to install "Obsidian Git," accept it.)
- Settings → **Git** → confirm **Auto pull on startup** is on, and set an auto commit-and-sync interval (e.g. every 10 min) if it isn't already.
- Test it: `Cmd+P` → **Git: Pull** (should report up to date) → make a tiny edit → `Cmd+P` → **Git: Commit-and-sync** → confirm the commit shows up on GitHub.

**Done when:** you can see `Students/`, `Transcripts/`, `Maps/`, `Templates/`, and `AGENTS.md`, and a test edit syncs to GitHub.

---

## Part 2 — The coaching plugin (Claude Code)

The coaching skills run inside Claude Code and read/write the vault from Part 1.

### 1. Prerequisites
- **Claude Code** installed and signed in — https://claude.com/claude-code
- Accept the invite to `socialclubstudios/syaf-coaching-kit` (check GitHub, same as the vault).

### 2. Add the marketplace and install
In Claude Code:
```
/plugin marketplace add socialclubstudios/syaf-coaching-kit
/plugin install syaf-coaching-kit
```
Restart Claude Code if it prompts you to.

### 3. What you get
- **`student-briefing`** — "brief me on [name]" before a call. Pulls current focus, coaching history, action items, wins, and flags from the vault.
- **`process-syaf-call`** — turn a call transcript into a student profile update + coaching log (wins, flags, action items).
- **`sync-syaf-recordings`** — pull recordings from Google Drive and transcribe them into the vault. Needs an **AssemblyAI API key** set as `$ASSEMBLYAI_API_KEY` or saved to `~/.assemblyai_api_key`, plus Google Drive access — ask Peter for both.

> The first time a connector (Slack, ClickUp, Granola, Google Calendar/Drive) is used, Claude Code will prompt you to authenticate it. `student-briefing` and `process-syaf-call` work off the vault alone.

### Updating later
```
/plugin marketplace update socialclubstudios/syaf-coaching-kit
```
then reinstall. Because it's a real repo (not a one-off zip), updates are a pull away.

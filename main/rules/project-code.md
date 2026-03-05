# Project Rules

## Technical Identity

- **Role:** Senior React Native & JavaScript Developer
- **Responsibilities:** Code, fix projects, commit, push, create PRs, review code

## Directory

- **Projects are located in `../code/` (shared across all agents)**. All agents read/write to the same project folder.
- **Write tool only works inside this workspace.** All code edits must be under the workspace directory.
- Example: to edit `pi-manager/app/screens/X.tsx`, use path **`../code/pi-manager/app/screens/X.tsx`** (relative to workspace root).

## Exec / Write timeouts (large files or many operations)

Exec and Write have time limits. To avoid being cut off:

1. **Large files:** Prefer writing in **smaller chunks** (e.g. one component, one function, or one logical block at a time) instead of one huge Write. If a single Write fails or times out, retry with a smaller edit or use the shell fallback below.
2. **Shell fallback when Write times out:** If Write tool fails or times out, write the file via shell, e.g.:
   ```bash
   cat > path/to/file.tsx << 'EOF'
   ... content ...
   EOF
   ```
   Use the **full path** to the file (e.g. under workspace or under `reactnative/...`). Escaping: inside the heredoc, avoid unescaped `'`; if the content contains `'`, use a different delimiter or `printf`/`echo -e` with care.
3. **Many operations in a row:** If you need to touch many files, do a few at a time and confirm, or split into separate steps, so one long burst does not hit the exec limit.

## Project-Specific Rules

- **Before coding:** Check if project has `AGENTS.md` or `.cursor/` folder
- If exists, read those rules and follow them
- Project-specific rules take precedence over workspace rules

## Code Review Workflow

- After making code changes, send only the modified portions for review (not the entire file)
- Highlight what was changed for clarity
- **ALWAYS confirm before making code changes** - report what will change and get explicit approval

## Jira Rules

- **Always return original content** - When displaying ticket information (title, description, comments, etc.), return the original text as-is without translation. Only summarize or translate if user explicitly requests translation.

# AGENTS.md - Workspace Config

## Project Directory

- All projects are located in `/Volumes/SSD512/code`
- Always work within this directory for code operations

## Git Operations

- **Always use `gh` CLI** for all git operations (commit, push, PR, review, etc.)
- Do not use git commands directly (git commit, git push, etc.)
- Use gh CLI for creating PRs, viewing PRs, commenting on PRs
- **Before committing:** Check if project has `.rule_git` folder. If exists, read and follow those rules
- **Before starting code work:** Pull latest code from main branch
- **After push completion:** Checkout back to the main branch

## Code Review Workflow

- After making code changes, send only the modified portions for review (not the entire file)
- Highlight what was changed for clarity

## Safety

- Don't exfiltrate private data. Ever.
- **ALWAYS confirm before making code changes** - report changes, get approval, then proceed
- **ALWAYS confirm before git operations** - report commits/pushes, get approval, then proceed

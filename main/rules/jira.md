# Jira Rules

## Environment Setup

**Important:** Before running any Jira commands, if commands failed, try to run:
```bash
source ~/.zshrc
```

This loads Jira environment variables (JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN) from your shell configuration.

---

## Ticket Handling Workflow

Note: jira env already setted up at .zshrc, example: `echo $JIRA_API_TOKEN`
1. **Read & understand ticket first** - When asked to check a ticket:
   - Read title, description, requirements carefully
   - Understand the goal and scope of the ticket

2. **Initial confirmation**:
   - Summarize the ticket (do not translate)
   - Ask user which project/folder this ticket belongs to
   - Only proceed when user confirms

3. **Create execution plan** - After initial confirmation:
   - List out the plan with details:
     - Find project/folder location
     - Find relevant files to modify
     - Find related code patterns
     - What code changes to make
     - Commit message and approach
     - Branch name to work on
     - Create PR and assign to whom
     - Update ticket status to what
     - Assign ticket to whom
   - Present plan and ask for final confirmation
   - Only proceed when user approves the plan

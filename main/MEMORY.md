# MEMORY.md - Working Notes & Preferences

> Last updated: 2026-03-11
> Project: Pi Manager (React Native + Node.js)

---

## 👤 About Levi (User)

**Name:** Levi
**Role:** OpenClaw user, AI-assisted developer
**Tech Stack:** React Native, JavaScript, Node.js
**Device:** Raspberry Pi 5 (8GB RAM)
**Timezone:** Asia/Saigon
**Language:** Vietnamese (prefers responses in Vietnamese)

### Communication Preferences

- **Language:** Vietnamese for conversation, English for code/docs
- **Style:** Direct, concise, no filler words
- **Code Changes:** Requires explicit confirmation before committing
- **Updates:** Prefers bullet points over paragraphs
- **Testing:** Tests via Telegram Mini App, not browser

### When Things Go Wrong

- Explain root cause briefly
- Provide solution immediately
- No blame, focus on fixing
- Show error logs when relevant

---

## 🛠️ Development Workflow

### Pre-Commit Checklist

- [ ] Test locally
- [ ] Check for console errors
- [ ] Verify no breaking changes
- [ ] Update docs if API changed
- [ ] Remove console.log statements

### Commit Message Format

```
type: description (max 72 chars)

Optional body explaining WHY (not WHAT)

- feat: New feature
- fix: Bug fix
- docs: Documentation
- chore: Maintenance
```

### PR Requirements

- Clear description (what/why/how)
- Testing checklist
- Screenshots for UI changes
- Links to related issues

---

## 🐛 Debugging Strategy

### When Errors Occur

1. Check logs first (server log, browser console)
2. Reproduce steps consistently
3. Isolate the issue (frontend/backend/network?)
4. Search error message online
5. Try minimal reproduction

### Common Error Patterns

| Error | Likely Cause | Solution |
|-------|-------------|----------|
| `Cannot read property` | null/undefined | Add null check |
| `CORS error` | Missing origin | Update ALLOWED_ORIGINS |
| `502 Bad Gateway` | Server down | Check server process |
| `Socket not connected` | Auth failed | Verify auth flow |
| `--announce requires --session isolated` | CLI flag conflict | Check payload type |

### Essential Commands

```bash
# Check running processes
ps aux | grep node
ps aux | grep cloudflared

# Kill all Node processes
killall -9 node cloudflared

# View server logs
tail -f /tmp/server.log
tail -100 /tmp/start.log

# Test endpoint
curl -v http://localhost:3001/api/health

# Restart server
cd server && npm run dev
```

---

## 🧪 Testing Approach

### Unit Tests

- Write for critical business logic
- Mock external dependencies
- Test edge cases, not just happy path

### Integration Tests

- Test socket events end-to-end
- Test API endpoints with auth
- Test CLI commands

### Manual Testing

- Test in production-like environment
- Test on actual device (Telegram app)
- Test error states
- Test loading states

### Before Merge Checklist

- [ ] All tests pass
- [ ] Manual test completed
- [ ] No console errors
- [ ] Performance acceptable
- [ ] No breaking changes

---

## 🔄 Session Management

### End of Session

- Commit all changes
- Push to remote branch
- Update PR description
- Note pending tasks in chat

### Start of New Session

- Pull latest changes
- Check pending PRs
- Review recent commits
- Read relevant docs
- Ask for context recap if needed

### When Context Is Lost

- Check `git log` for recent changes
- Read MEMORY.md for preferences
- Ask user to recap if needed
- **Don't pretend to remember**

---

## 💻 Code Quality

### Code Review Checklist

- [ ] No hardcoded values (use env vars)
- [ ] Error handling in place
- [ ] Loading states for async operations
- [ ] Consistent naming conventions
- [ ] No console.log in production
- [ ] TypeScript types correct
- [ ] Comments explain WHY, not WHAT

### Performance Guidelines

- Avoid unnecessary re-renders
- Debounce API calls
- Lazy load heavy components
- Cache expensive computations
- Monitor memory usage

### Security Rules

- Never commit secrets/tokens
- Validate all user inputs
- Check auth before mutations
- Use environment variables
- Whitelist allowed origins

---

## 🤖 AI Collaboration Tips

### For Best Results

**✅ Do:**
- Provide full context
- Share error messages verbatim
- State expected behavior clearly
- Give feedback when solution doesn't work

**❌ Don't:**
- Assume AI remembers from previous sessions
- Hide error messages
- Bundle multiple tasks in one message
- Give vague requirements ("fix it")

### When AI Makes Mistakes

- Point out exactly what's wrong
- Provide additional info to fix
- Don't hesitate to ask for retry
- Share correct solution if you know it

---

## 📚 Project Onboarding

### New Project Checklist

**1. Setup**
- [ ] Read README.md
- [ ] Install dependencies
- [ ] Configure env vars
- [ ] Run hello world test

**2. Architecture**
- [ ] Understand folder structure
- [ ] Identify entry points
- [ ] Map data flow
- [ ] Find key config files

**3. Development**
- [ ] Setup hot reload
- [ ] Configure debugger
- [ ] Test deploy process
- [ ] Know how to check logs

**4. Team & Process**
- [ ] Know who to ask for what
- [ ] Understand code review process
- [ ] Know deployment pipeline
- [ ] Know rollback procedure

---

## 🎯 OpenClaw Specific Notes

### Gateway Integration

- Gateway runs on port 8080 (default)
- Use `openclaw` CLI for cron operations
- Token stored in Gateway session config
- Never commit Gateway tokens

### Cronjob CLI Flags

**Critical:** OpenClaw CLI has specific session requirements:

- **System Events:** `--session main` (NO --announce)
- **Agent Tasks:** `--session isolated` + `--announce`

**Common Errors:**
- `--announce requires --session isolated` → Using --announce with system events
- `Isolated jobs require --message` → Using isolated with system events

**Solution:** Always check payload type before building CLI args

### Server Startup

```bash
# Always kill old processes first
killall -9 node cloudflared
sleep 2

# Start full stack
yarn start:full

# Wait 45s for complete startup
# Check /tmp/start.log for URL
```

### Browser Testing Limitations

- No Telegram auth context
- Use DEBUG mode for browser testing
- Real testing must be in Telegram app
- Socket connections may fail without auth

---

## 📝 Notes Template

### Task Completion Format

```markdown
## ✅ [Task Name] - Complete

**What was done:**
- Point 1
- Point 2

**Files changed:**
- `path/to/file.ts`

**Testing:**
- [ ] Test case 1
- [ ] Test case 2

**Next steps:**
- [ ] Pending task
```

### Bug Fix Format

```markdown
## 🐛 [Bug Name] - Fixed

**Problem:**
Description of the issue

**Root Cause:**
Why it happened

**Solution:**
How it was fixed

**Files changed:**
- `path/to/file.ts`

**Testing:**
- [ ] Reproduce original bug
- [ ] Verify fix works
```

---

*This file should be updated periodically with new learnings and preferences.*

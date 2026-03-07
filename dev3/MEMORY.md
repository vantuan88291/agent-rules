# MEMORY.md - Pi Manager Project Notes

## 📦 Project Overview

**Name:** Pi Manager  
**Type:** React Native Web + Node.js Backend  
**Purpose:** Mobile-first dashboard for remotely managing Raspberry Pi via Telegram Mini App  
**Location:** `/home/vantuan88291/.openclaw/workspace/code/reactnative/pi-manager`  
**Repo:** https://github.com/vantuan88291/pi-manager

---

## 🚀 Startup & Tunnel Issues

### Problem: Cloudflare Tunnel URL Changes on Restart

**Issue:** Each time `yarn start:full` runs, Cloudflare creates a NEW tunnel URL.  
**Symptom:** WebSocket connection fails with error like:
```
WebSocket connection to 'wss://old-url.trycloudflare.com/socket.io/' failed
```

**Root Cause:** Metro bundler bakes `EXPO_PUBLIC_SOCKET_URL` into JS bundle at build time.  
When tunnel restarts with new URL, the built frontend still tries to connect to old URL.

**Solution:** Use runtime URL detection instead of build-time injection:

```typescript
// app/services/socket/SocketManager.ts
const getSocketUrl = () => {
  if (typeof window !== "undefined" && window.location?.origin) {
    return window.location.origin  // Use current domain at runtime
  }
  return process.env.EXPO_PUBLIC_SOCKET_URL || "http://localhost:3001"
}
```

**Key Files Modified:**
- `app/services/socket/SocketManager.ts` - Runtime URL detection
- `scripts/start-with-tunnel.sh` - Removed sed URL injection steps
- `.env` - Set `EXPO_PUBLIC_SOCKET_URL=__TUNNEL_URL__` (placeholder, not used at runtime)

**Test:** After fix, can restart tunnel multiple times without rebuild - app auto-connects to new URL.

---

## 🎨 UI Changes vs Full Rebuild

### Rule: UI/Frontend Changes Don't Need Tunnel Restart

**When you CAN skip tunnel restart:**
- ✅ CSS/styling changes (padding, margins, colors, fonts)
- ✅ Component layout changes
- ✅ Text/translation updates
- ✅ Debug UI additions
- ✅ Any change that doesn't affect socket/auth logic

**Command:** Just rebuild web, don't restart tunnel:
```bash
cd /home/vantuan88291/.openclaw/workspace/code/reactnative/pi-manager
rm -rf dist
npx expo export --platform web
sed -i 's|<title>Pi Manager</title>|<title>Pi Manager</title>\n    <script src="https://telegram.org/js/telegram-web-app.js"></script>|' dist/index.html
rm -rf server/public/*
cp -r dist/* server/public/
# Server auto-reloads via tsx watch
```

**When you MUST restart tunnel:**
- ❌ Backend code changes (server/*.ts)
- ❌ Socket authentication logic
- ❌ Environment variable changes (TELEGRAM_BOT_TOKEN, etc.)
- ❌ New API endpoints
- ❌ Whitelist/auth changes

**Command:** Full restart:
```bash
yarn start:full
```

---

## 📝 Git Workflow

### Standard Branch Workflow

1. **Checkout master and pull latest:**
   ```bash
   git checkout master
   git pull
   ```

2. **Create new feature branch:**
   ```bash
   git checkout -b feat/feature-name
   ```

3. **Make changes and commit:**
   ```bash
   git add <files>
   git commit -m "fix: description"
   ```

4. **Push and create PR:**
   ```bash
   git push -u origin feat/feature-name
   gh pr create --title "fix: description" --body "PR details"
   ```

### Important Notes

- **NEVER work directly on master** - always create feature branch
- **ALWAYS pull master before creating branch** - avoid conflicts
- **UI changes = small commits** - can batch multiple UI fixes together
- **Backend changes = separate PR** - don't mix with UI changes
- **Test before push** - especially socket/auth changes

### Example: Fixing UI Issue

```bash
# 1. Get latest master
git checkout master
git pull

# 2. Create branch
git checkout -b fix/tab-bar-text-clipping

# 3. Edit files (e.g., MainTabNavigator.tsx)

# 4. Rebuild web (NO tunnel restart needed)
rm -rf dist && npx expo export --platform web && cp -r dist/* server/public/

# 5. Test in browser/Telegram

# 6. Commit and push
git add app/navigators/MainTabNavigator.tsx
git commit -m "fix: tab bar text clipping - increase height to 64px"
git push -u origin fix/tab-bar-text-clipping

# 7. Create PR
gh pr create --title "fix: tab bar text clipping" --body "Description"
```

---

## 🤖 Telegram Bot Setup

### Required Environment Variables

**Frontend (.env):**
```bash
EXPO_PUBLIC_TELEGRAM_BOT_TOKEN=7968691178:AAFSU8x6dS3UUzTYrRlKxSJD_OVUm8UoDBY
```

**Backend (server/.env):**
```bash
PORT=3001
TELEGRAM_BOT_TOKEN=7968691178:AAFSU8x6dS3UUzTYrRlKxSJD_OVUm8UoDBY
ALLOWED_ORIGINS=https://your-tunnel-url.trycloudflare.com,http://localhost:8081
ADMIN_TELEGRAM_ID=600843385
```

### Whitelist Configuration

**File:** `server/src/config/whitelist.json`
```json
[600843385, 7441186402]
```

**Note:** Only Telegram user IDs in whitelist can access the app.

### BotFather Setup

1. Open @BotFather in Telegram
2. `/setmenubutton` → Select bot → Send tunnel URL
3. Test by opening bot and clicking menu button

---

## 🐛 Common Issues & Solutions

### Issue 1: WebSocket Connection Failed

**Symptom:** Console shows `WebSocket connection to 'wss://old-url...' failed`

**Cause:** Tunnel restarted but frontend still has old URL baked in

**Fix:**
1. Use runtime URL detection (see Solution above)
2. Hard refresh browser (Ctrl+Shift+R)
3. If still broken, restart tunnel: `yarn start:full`

### Issue 2: Bottom Tab Text Clipped

**Symptom:** Tab bar labels cut off or not visible

**Fix:**
```typescript
// app/navigators/MainTabNavigator.tsx
tabBarStyle: {
  height: 64,  // Increased from 60
}
tabBarLabelStyle: {
  fontSize: 12,  // Increased from 11
}
```

**Note:** UI change only - no tunnel restart needed!

### Issue 3: Telegram Auth Not Working

**Symptom:** Settings shows "Not connected" or User ID = N/A

**Checklist:**
1. ✅ Bot token correct in server/.env
2. ✅ User ID in whitelist.json
3. ✅ Opening app FROM Telegram (not browser)
4. ✅ Check Debug Info card in Settings for initData

**Debug:** Check Settings → Debug Info card:
- Connection Status: should be "connected"
- Authenticated: should be "✅ Yes"
- User ID: should show your Telegram ID
- InitData JSON: should show full user object

### Issue 4: Build Cache Issues

**Symptom:** Changes not appearing after rebuild

**Fix:**
```bash
# Clear all caches
rm -rf dist .expo node_modules/.cache server/public

# Rebuild
npx expo export --platform web

# Copy to server
cp -r dist/* server/public/
```

---

## 📁 Key Files Reference

| File | Purpose | Edit Frequency |
|------|---------|----------------|
| `app/services/socket/SocketManager.ts` | Socket.IO client, URL detection | Low |
| `app/navigators/MainTabNavigator.tsx` | Bottom tab bar config | Medium |
| `app/screens/SettingsScreen.tsx` | Settings + Debug Info | Medium |
| `scripts/start-with-tunnel.sh` | Startup script | Low |
| `server/src/socket/index.ts` | Socket auth middleware | Low |
| `server/src/config/whitelist.json` | Allowed user IDs | Low |
| `.env.example` | Frontend env template | Low |
| `server/.env.example` | Backend env template | Low |

---

## 🎯 Quick Commands

```bash
# Start everything (tunnel + build + server)
yarn start:full

# Rebuild web only (UI changes)
rm -rf dist && npx expo export --platform web && cp -r dist/* server/public/

# Check server logs
tail -f /tmp/server.log

# Check tunnel URL
grep trycloudflare.com /tmp/tunnel.log | head -1

# Git workflow
git checkout master && git pull
git checkout -b feat/feature-name
# ... make changes ...
git add . && git commit -m "fix: description"
git push -u origin feat/feature-name
```

---

## 📌 Last Updated

**Date:** 2026-03-07  
**By:** Dev3 bot  
**Context:** After fixing runtime socket URL detection + UI improvements (PR #15, #16)

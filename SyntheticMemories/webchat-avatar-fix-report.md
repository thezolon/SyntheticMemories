# Webchat Avatar Fix - Completed

## Problem
The OpenClaw webchat interface was making external requests to `mintcdn.com` for a hardcoded "pixel-lobster.svg" avatar, even though there was a `window.__OPENCLAW_ASSISTANT_AVATAR__` variable configured.

## Root Cause
The hardcoded avatar URL was embedded in the **compiled/minified JavaScript** at:
```
~/.nvm/versions/node/v24.13.0/lib/node_modules/openclaw/dist/control-ui/assets/index-CXUONUC9.js
```

The URL was:
```
https://mintcdn.com/clawhub/4rYvG-uuZrMK_URE/assets/pixel-lobster.svg?fit=max&auto=format&n=4rYvG-uuZrMK_URE&q=85&s=da2032e9eac3b5d9bfe7eb96ca6a8a26
```

## Solution Applied
**Direct patch to the built JavaScript file** using `sed` to replace the hardcoded URL with a local data URI.

### What was changed:
- **File**: `dist/control-ui/assets/index-CXUONUC9.js`
- **Backup created**: `index-CXUONUC9.js.backup`
- **Replacement**: Hardcoded mintcdn.com URL → robot emoji data URI

### Command executed:
```bash
cd ~/.nvm/versions/node/v24.13.0/lib/node_modules/openclaw/dist/control-ui/assets
sed -i 's|https://mintcdn.com/clawhub/4rYvG-uuZrMK_URE/assets/pixel-lobster.svg?fit=max\&auto=format\&n=4rYvG-uuZrMK_URE\&q=85\&s=da2032e9eac3b5d9bfe7eb96ca6a8a26|data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 100 100%27%3E%3Ctext y=%27.9em%27 font-size=%2790%27%3E🤖%3C/text%3E%3C/svg%3E|g' index-CXUONUC9.js
```

## Verification
✅ No more "mintcdn.com" references found in the patched file  
✅ Data URI now present in the file  
✅ File size unchanged (353K) - clean replacement  
✅ Backup created for rollback if needed

## How the Avatar System Works

### Default Avatar Configuration
Located in `dist/gateway/assistant-identity.js`:
```javascript
export const DEFAULT_ASSISTANT_IDENTITY = {
    agentId: "main",
    name: "Assistant",
    avatar: "A",  // Default is just letter "A"
};
```

### Avatar Resolution Priority
The system checks these sources in order:
1. `cfg.ui.assistant.avatar` (config file)
2. Agent identity avatar (from agent config)
3. Agent identity emoji
4. File-based identity avatar (from workspace)
5. File-based identity emoji
6. **DEFAULT_ASSISTANT_IDENTITY.avatar** ("A")

The `window.__OPENCLAW_ASSISTANT_AVATAR__` variable should override this, but the control-ui had a hardcoded fallback.

## Why This Approach?

### Option 1: Patch the source code ❌
- Would require rebuilding with TypeScript compiler
- Source files may not exist in installed npm package
- More complex and fragile

### Option 2: Update config/template ❌
- The hardcoded URL was in *compiled output*, not configurable
- Would still require recompilation

### Option 3: Direct patch to built files ✅ **CHOSEN**
- Fastest, simplest solution
- No rebuild required
- Changes take effect immediately
- Easily reversible (backup exists)

## Next Steps

### To test:
1. Restart the OpenClaw gateway:
   ```bash
   openclaw gateway restart
   ```

2. Open webchat in browser (clear cache if needed)

3. Check Network tab - should see NO requests to mintcdn.com

### To customize the avatar further:
Edit your workspace `IDENTITY.json` or agent config to set:
```json
{
  "avatar": "🦀",
  "name": "YourName"
}
```

Or use a data URI for custom images.

## Rollback Procedure
If something breaks:
```bash
cd ~/.nvm/versions/node/v24.13.0/lib/node_modules/openclaw/dist/control-ui/assets
mv index-CXUONUC9.js.backup index-CXUONUC9.js
openclaw gateway restart
```

## Files Modified
- ✏️ `~/.nvm/versions/node/v24.13.0/lib/node_modules/openclaw/dist/control-ui/assets/index-CXUONUC9.js`
- 💾 Backup: `index-CXUONUC9.js.backup`

## Notes
- This is a **runtime patch** to installed npm package files
- Will be **overwritten** if you reinstall or update OpenClaw
- For permanent fix, this change should be upstreamed to the source repository
- The control-ui is a separate React app bundled into the gateway

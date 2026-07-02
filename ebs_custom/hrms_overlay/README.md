# HRMS PWA Overlay (managed by ebs_custom)

Stored here — applied automatically on `bench migrate`.

## What is copied (safe files only)

- `frontend/src/views/ebs_custom/` — PWA form screens
- `frontend/src/router/ebs_custom.js` — routes
- `frontend/src/components/icons/FrappeHRLogo.vue` — logo
- `hrms/public/manifest/bot-hr-*` — PWA icons

Branding (BOT HR title) is patched into existing hrms files — core files are NOT replaced.

## After migrate — rebuild required

```bash
cd apps/hrms/frontend
yarn install
yarn build
cd ../../..
bench build --app hrms
bench restart
```

## White screen fix

If `/hrms` is blank after migrate:

```bash
cd ~/frappe-bench/apps/hrms/frontend   # or your bench path
yarn install
yarn build
cd ~/frappe-bench
bench build --app hrms
bench --site biometric.metadaftr.com clear-cache
bench restart
```

Then hard-refresh browser (`Ctrl+Shift+R`) or clear site data.

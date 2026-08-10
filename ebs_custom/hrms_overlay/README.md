# HRMS PWA Overlay (managed by ebs_custom)

Stored here — applied automatically on `bench install-app ebs_custom` and `bench migrate`.

## What is copied (safe files only)

- `frontend/src/views/ebs_custom/` — PWA form screens
- `frontend/src/router/ebs_custom.js` — routes
- `frontend/src/components/icons/FrappeHRLogo.vue` — logo
- `frontend/src/components/RequestPanel.vue` — Home My/Team Requests (includes Employee Advance)
- `frontend/src/components/RequestList.vue` — request action sheet field map
- `frontend/src/components/EmployeeAdvanceItem.vue` — advance list item + workflow badges
- `frontend/src/data/advances.js` — my/team advances (`for_approval`) via `ebs_custom.api.pwa`
- `frontend/src/data/config/requestSummaryFields.js` — Employee Advance summary fields
- `hrms/hr/doctype/pwa_notification/pwa_notification.py` — deep link for advances
- `hrms/public/manifest/bot-hr-*` — PWA icons

Branding (BOT HR title) is patched into existing hrms files — core files are NOT replaced.

Router + Home.vue are patched idempotently (safe to run multiple times; duplicate imports are removed).

## Employee Advance / Loan on mobile

Pending advances appear under **Home → Team Requests** for users whose roles can act on the current workflow state (Loan Approval Multi Level). Approvers also get **PWA Notification**s when the state moves to their stage.

## After migrate — rebuild if needed

```bash
cd apps/hrms/frontend
yarn install
yarn build
cd ../../..
bench build --app hrms
bench restart
```

## Build error: `ebsCustomRoutes has already been declared`

On server, edit `apps/hrms/frontend/src/router/index.js` — keep only ONE line:

```javascript
import ebsCustomRoutes from "./ebs_custom"
```

Then `yarn build` and `bench build --app hrms`.

Or pull latest `ebs_custom` and run `bench migrate` (patch auto-fixes duplicates).

## White screen at /hrms

```bash
cd apps/hrms/frontend && yarn install && yarn build
cd ~/frappe-bench && bench build --app hrms && bench restart
```

Hard refresh browser: `Ctrl+Shift+R`

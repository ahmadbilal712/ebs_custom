# HRMS PWA Overlay (managed by ebs_custom)

These files are copied into the `hrms` app automatically when you run:

```bash
bench --site YOUR_SITE migrate
```

or when `ebs_custom` `after_migrate` runs.

## After migrate — rebuild PWA (required)

```bash
cd apps/hrms/frontend
yarn build
cd ../../..
bench build --app hrms
bench restart
```

## What this folder contains

- BOT HR branding (login, manifest, logo)
- PWA routes for Salary Adjustment, Promotion Request, Branch Attendance Approval
- Branch Attendance Approval screen with **Load Check-ins** button

## When HRMS is updated

`bench update` may change core `hrms` files. Running `bench migrate` re-applies this overlay.

If `Home.vue` or `router/index.js` were heavily changed upstream, tell your developer to re-merge those two files manually.

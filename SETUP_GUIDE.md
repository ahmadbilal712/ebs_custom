# Ticket #2448 — Attendance Approval + Color Excel (Step-by-step)

**Site:** https://biometric.metadaftr.com/  
**App folder on PC:** `C:\Users\Ahmad Bilal\Music\ebcerp\ebs_custom-main`  
**Server folder:** `frappe-bench/apps/ebs_custom/`

---

## What was built (in this app)

| Feature | Description |
|---------|-------------|
| **Branch Attendance Approval** | Branch Manager approves one branch for one date |
| **Employee Checkin** | Check-ins stay **Pending** until approved (no auto attendance) |
| **Workflow** | Draft → Pending Approval → **Approved** |
| **Excel** | Green / Red / Yellow report (openpyxl) |
| **Email** | Auto-sent to HR Officer, HR Manager, Operations Manager, COO |

---

## PART A — Copy code to server (you or Khayyam)

### Step A1 — Copy folder

Copy everything from:

`C:\Users\Ahmad Bilal\Music\ebcerp\ebs_custom-main\`

To server:

`~/frappe-bench/apps/ebs_custom/`

(Overwrite files.)

### Step A2 — Install Python library on server

SSH into server:

```bash
cd ~/frappe-bench
./env/bin/pip install openpyxl
```

### Step A3 — Run bench commands

```bash
cd ~/frappe-bench
bench --site biometric.metadaftr.com migrate
bench --site biometric.metadaftr.com sync-fixtures
bench build --app ebs_custom
bench --site biometric.metadaftr.com clear-cache
bench restart
```

If site name is different:

```bash
bench --site all list
```

---

## PART B — One-time setup on website

Login: https://biometric.metadaftr.com/

### Step B1 — Create role: Branch Manager

1. Search **Role** → **New**
2. Role Name: `Branch Manager`
3. Save

### Step B2 — Create users (test)

| User | Roles |
|------|-------|
| employee@test.com | Employee |
| manager@test.com | Branch Manager, Employee |
| hr@test.com | HR Officer |

Link each user to an **Employee** record (`user_id` on Employee).

### Step B3 — Branches on employees

1. Search **Branch** → create branches (e.g. `Lahore`, `Karachi`)
2. Open each **Employee** → set field **Branch** (`custom_branch`) → Save

### Step B4 — Branch Manager permission

1. Search **User Permission** → **New**
2. User = manager user
3. Allow = **Branch**
4. For Value = manager's branch
5. Save

### Step B5 — Set Reports To (optional)

On staff **Employee** → **Reports To** = Branch Manager employee.

### Step B6 — Email for reports

1. Search **Email Account** → configure outgoing SMTP
2. Search **Role** → assign users to:
   - HR Officer
   - HR Manager
   - Operations Manager
   - COO

(At least one user per role must have an email.)

### Step B7 — Check workflow exists

1. Search **Workflow**
2. Open **Branch Attendance Approval Workflow**
3. **Is Active** = checked

If missing, run again:

```bash
bench --site biometric.metadaftr.com sync-fixtures
```

---

## PART C — Daily use (how client will use it)

### Step C1 — Employees check in (phone)

1. Open on phone: `https://biometric.metadaftr.com/hrms`
2. Login as employee
3. **Check In** and later **Check Out**

### Step C2 — Branch Manager approves

1. Login as Branch Manager on desk
2. Search **Branch Attendance Approval** → **New**
3. **Branch** = your branch
4. **Attendance Date** = today (or yesterday)
5. Click button **Load Check-ins**
6. Review table (Present / Absent / On Leave)
7. **Save**
8. Click workflow **Submit for Approval** (if needed)
9. Click workflow **Approve**

### Step C3 — What happens automatically

- **Attendance** records created/submitted in ERPNext
- **Excel** attached on the form (field: Attendance Report)
- **Email** sent to HR Officer, HR Manager, Operations Manager, COO

### Step C4 — Verify

| Check | Where |
|-------|--------|
| Attendance saved | **Attendance** list |
| Excel file | **Branch Attendance Approval** → Report File |
| Email sent | **Email Queue** |

---

## PART D — Push to GitHub (from your PC)

```powershell
cd "C:\Users\Ahmad Bilal\Music\ebcerp\ebs_custom-main"
git add .
git commit -m "feat(hr): branch attendance approval, color excel report, email on approve (#2448)"
git push origin bilal-ahmad
```

Tell Khayyam to merge to `main` for live EBC site.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| **Load Check-ins** empty | Employees must have **Branch** set and status Active |
| Workflow buttons missing | Assign **Branch Manager** role to user |
| No email | Configure Email Account + users on 4 roles |
| openpyxl error | `pip install openpyxl` in bench env |
| DocType not found | `bench migrate` again |

---

## Files added (for developers)

```
ebs_custom/attendance/
  doctype/branch_attendance_approval/
  doctype/branch_attendance_approval_detail/
  events/attendance.py
  report/branch_attendance_excel.py
  utils/recipients.py
ebs_custom/fixtures/workflow_branch_attendance.json
requirements.txt
```

# Ticket #2443 — Salary Adjustment & Promotion

**Site:** https://biometric.metadaftr.com/

---

## What was built

| Feature | DocType |
|---------|---------|
| Salary adjustment form | **Salary Adjustment Request** |
| Promotion form | **Promotion Request** |

**Approval chain (both forms):**

```
Branch/Division Manager → Operations Manager → COO → HR Manager → CFO → CEO
```

**On CEO final approval:**
- Updates **Employee** (salary / designation / grade)
- Future **Effective Date** → scheduled daily job applies update
- Notifies **HR Officer** + **Accounts Officer** (system + email)

---

## Deploy on server

```bash
cd ~/frappe-bench/apps/ebs_custom
git pull

cd ~/frappe-bench
bench --site biometric.metadaftr.com migrate
bench build --app ebs_custom
bench --site biometric.metadaftr.com clear-cache
bench restart
```

---

## One-time setup (Administrator)

### 1. Create missing roles

Search **Role** → create if missing:

- Division Manager
- Operations Manager
- COO
- CFO
- CEO
- Accounts Officer

### 2. Assign roles to users

| User | Roles (example) |
|------|-----------------|
| Branch Manager user | Branch Manager |
| Division head | Division Manager |
| Ops head | Operations Manager |
| COO user | COO |
| HR head | HR Manager |
| Finance head | CFO |
| CEO user | CEO |
| HR staff | HR Officer |
| Accounts staff | Accounts Officer |

### 3. Set employee current salary

Open each **Employee** → fill **Current Salary** (`custom_current_salary`) → Save

---

## Daily use

### A — Start request (Branch or Division Manager)

1. Search **Salary Adjustment Request** OR **Promotion Request**
2. Click **New**
3. Select **Employee** (name/ID auto-fills)
4. Fill salary or promotion fields + **Effective Date**
5. **Save**
6. Click workflow **Submit**

### B — Each approver

Login as user with the correct role. Open the request from:
- Search bar, or
- **Notification** bell, or
- **Workflow Actions**

Click **Approve** (or **Reject**).

| Stage | Who approves |
|-------|----------------|
| After Submit | Operations Manager |
| Next | COO |
| Next | HR Manager |
| Next | CFO |
| Final | CEO |

### C — After CEO approves

- **Today or past effective date:** Employee master updated immediately
- **Future effective date:** Update scheduled; daily job applies on that date
- **HR Officer** + **Accounts Officer** get notification + email

---

## Verify

```bash
bench --site biometric.metadaftr.com console
```

```python
import frappe
print(frappe.db.exists("DocType", "Salary Adjustment Request"))
print(frappe.db.exists("DocType", "Promotion Request"))
print(frappe.db.exists("Workflow", "Salary Adjustment Request Workflow"))
print(frappe.db.exists("Workflow", "Promotion Request Workflow"))
exit()
```

All should be `True`.

---

## Who can create forms?

| Role | Create? |
|------|---------|
| Branch Manager | Yes |
| Division Manager | Yes |
| Employee | No |
| HR Officer | No (read + notified on final approval) |

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Not permitted | User needs Branch Manager or Division Manager role to create |
| No Approve button | User needs role for current workflow stage |
| Current salary empty | Set **Current Salary** on Employee record |
| Future update not applied | Wait for effective date; scheduler runs daily |

# Hands-on: RBAC with Casbin

A tiny, runnable lab. You ask *"can this person do this action on this thing?"* and Casbin
answers using **roles** — nothing else.

## Run it

```bash
cd 01-rbac/hands-on-casbin
python3 -m venv .venv && source .venv/bin/activate   # first time only
pip install -r requirements.txt                       # first time only
python main.py
```

Requires **Python 3.9+**.

## The menu

- **[1] ask a question** — pick a person, an action, and a resource; get ✅ ALLOW / ❌ DENY
  with a one-line reason.
- **[2] demo** — runs every scenario at once, so you see the whole picture in one table.
- **[3] wall** — poses a perfectly reasonable rule that RBAC **cannot** express, and shows
  you *why*. This is the important one.

## What to notice

1. **Permissions attach to roles, not people.** `policy.csv` never mentions "Amine can
   transfer" — it says "*tellers* can transfer," and Amine *is* a teller.
2. **Roles inherit.** `g, branch_manager, teller` is the only line that lets **Leila**
   transfer. Delete it and she can't — even though nothing about Leila changed.
3. **Access is data.** To change who can do what, you edit `policy.csv` — not the code.
4. **Then it breaks.** Run **[3] wall**. RBAC has no column for *time*, *amount*, or
   *ownership*. That gap is what [`02-abac`](../../02-abac/) exists to fix.

## The files

| File | What it is |
|------|------------|
| `model.conf` | The Casbin RBAC model (with role inheritance). Rarely changes. |
| `policy.csv` | The roles, permissions, and who-has-which-role — **as data**. |
| `main.py` | The lab: `build_enforcer()` + `decide()` under a guided menu. |
| `test_policy.py` | A developer check that the rules still behave (not needed to run the lab). |

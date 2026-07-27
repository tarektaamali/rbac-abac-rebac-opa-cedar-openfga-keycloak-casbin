# Hands-on: ABAC with Casbin

The same lab as chapter 1 — but now the decision uses **attributes** (amount, hour,
branch), not just the role. RBAC is still here; ABAC sits on top of it.

## Run it

```bash
cd 02-abac/hands-on-casbin
python3 -m venv .venv && source .venv/bin/activate   # first time only
pip install -r requirements.txt                       # first time only
python main.py
```

Requires **Python 3.9+**.

## The menu

- **[1] ask** — pick a person, action, resource; for a **transfer** you also pick the
  amount, hour, and the account's branch. Get ✅ ALLOW / ❌ DENY with the reason.
- **[2] demo** — the headline: the **same** transfer flips ALLOW→DENY when only the hour
  changes (09:00 vs 22:00), plus over-limit and wrong-branch denials.
- **[3] wall** — a rule ABAC handles clumsily (ownership / hierarchy) → the on-ramp to
  [`03-rebac`](../../03-rebac/).

## What to notice — the diff from chapter 1

1. **`policy.csv` grew one column.** Compare it with
   [`01-rbac/hands-on-casbin/policy.csv`](../../01-rbac/hands-on-casbin/policy.csv): every
   rule now ends in a **condition**. Four say `True` (no extra rule). One — the teller
   transfer — carries the real ABAC logic:
   `r.amount <= 10000 && r.hour >= 8 && r.hour < 17 && r.sub_branch == r.obj_branch`.
2. **Rules are still data.** To change the limit or the hours, you edit `policy.csv` — not
   the code. Exactly the chapter-1 lesson, now with attributes.
3. **The canonical question is finally answered right.** *"Can Amine transfer 8,000 TND at
   22:00?"* → **DENY**. RBAC couldn't see the hour; ABAC can.
4. **The new pain.** Run a few denials and notice *"why was I denied?"* is harder now — the
   answer depends on several attributes at once. That cost is real, and it's why the next
   chapters externalise policy.

## The files

| File | What it is |
|------|------------|
| `model.conf` | RBAC matcher **plus** `eval(p.cond)` — evaluates each rule's condition. |
| `policy.csv` | Chapter 1's rules **+ a condition column**. The diff *is* the lesson. |
| `main.py` | `build_enforcer()` + `decide()` (now with context) under a guided menu. |
| `test_policy.py` | A developer check (the flip, over-limit, wrong-branch). Not needed to run the lab. |

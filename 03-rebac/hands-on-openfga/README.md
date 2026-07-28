# Hands-on: ReBAC (Zanzibar-style), mirroring OpenFGA

Access here follows **relationships**, not roles or attributes. There's **nothing to
install** — pure Python 3.9+.

## Run it

```bash
cd 03-rebac/hands-on-openfga
python3 main.py
```

## The menu

- **[1] ask** — pick a person and an account; get ✅ ALLOW / ❌ DENY **and the path** that
  granted (or would grant) access.
- **[2] demo** — the same account viewed three different ways (owner, branch-manager,
  bank-auditor), plus two denials — including a cross-tenant one.
- **[3] wall** — where relationships stop being enough → the on-ramp to
  [`04-policy-as-code`](../../04-policy-as-code/).

## What to notice

1. **Access is a graph walk.** `user:leila` can view `account:123` not because of a role,
   but because `leila → manager → branch:tunis`, and `branch:tunis → branch → account:123`.
   The check *traces the path*.
2. **Tenant isolation is free.** `user:leila` (DinarBank) can't view `account:999` (Banque
   de Carthage) — not because of a special rule, but because **no path exists**. Isolation
   falls out of the graph.
3. **Role ≠ relationship.** `user:amine` is a teller, yet has no path to `account:123`. A
   role doesn't relate you to a *specific* object; a relationship does.

## How OpenFGA thinks — `model.fga`

The real tool for this is **OpenFGA** (open-source Google Zanzibar). This lab's rules mirror
[`model.fga`](./model.fga) exactly. The key line:

```
define viewer: owner or manager from branch or auditor from branch
```

reads: *you may view an account if you own it, OR you manage the branch it belongs to, OR
you audit that branch's bank* (`branch`'s `auditor` is computed as `auditor from bank`).
That one line is the three paths our Python checker walks.

> Running the real OpenFGA server (Docker + tuples API) is covered later, in
> [`05-tools/openfga/`](../../05-tools/openfga/).

## The files

| File | What it is |
|------|------------|
| `tuples.csv` | The relationships, as data: `(subject, relation, object)`. |
| `model.fga` | The **real** OpenFGA authorization model this lab mirrors. |
| `main.py` | The checker: `build_store()` + `check()` under a guided menu. |
| `test_check.py` | A developer check (the three paths + cross-tenant denial). |

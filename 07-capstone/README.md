# 07 · Capstone — the whole stack, one request

> Everything you learned, composed. One SafiBank transfer request flows through **every
> layer** — and you see exactly which gate decides.

This is not a new idea — it's chapters 1–4 stitched together. `python3 app.py`, no
dependencies.

## The pipeline

```
transfer request
      │
      ▼
[ 1. TENANT ]  DinarBank ≠ Banque de Carthage?              → DENY (tenant)
      │ same tenant
      ▼
[ 2. RBAC ]    is the role allowed to transfer at all?      → DENY (rbac)
      │ teller / manager
      ▼
[ 3. ABAC ]    amount ≤ 10,000 TND and 08:00–17:00?         → DENY (abac)
      │ within limits
      ▼
[ 4. ReBAC ]   related to the account's branch?             → DENY (rebac)
      │ related
      ▼
   ✅ EXECUTE
```

The **order matters**: the tenant wall is checked *first*, so a cross-tenant request is
denied before any other gate runs.

## Run it

```bash
cd 07-capstone
python3 app.py
```

- **[1] ask** — pick a subject, account, amount, and hour; watch the pipeline decide.
- **[2] demo** — one request per gate, so you see each layer stop exactly one.

## What to notice

1. **Each chapter is a gate.** Tenant ([`00`](../00-foundations/)/[`03`](../03-rebac/)) →
   RBAC ([`01`](../01-rbac/)) → ABAC ([`02`](../02-abac/)) → ReBAC ([`03`](../03-rebac/)).
   [`04-policy-as-code`](../04-policy-as-code/) showed the same rule as one Rego policy; here
   it's a visible, ordered pipeline instead.
2. **The first failing gate wins.** `amine → acc:999` is cross-tenant *and* wrong-branch, but
   it's denied at **tenant** — because that's the first wall.
3. **Role beats ownership here.** Youssef *owns* `acc:123`, yet is denied at **RBAC**:
   customers can't transfer in this staff-only model, so the role gate fires before ownership
   is ever considered.
4. **The canonical question, finally end-to-end.** *"Can Amine transfer 8,000 TND at 22:00?"*
   → denied at ABAC — by the same stack a real SafiBank would run.

# RBAC — the theory

## Definition (simple)

**Role-Based Access Control**: permissions are attached to **roles**; users are given
roles; users inherit their role's permissions. You never grant a permission to a *person* —
you grant it to a *role*, then make the person a member of that role.

```
permission ── belongs to ──► role ── assigned to ──► user
```

## Everyday example

In any office, a **"Manager"** badge opens more doors than an **"Intern"** badge —
regardless of *who* is wearing it. Swap the badge and the access follows the badge, not
the name on it.

## SafiBank example

| Role | Can do |
|------|--------|
| `customer` | view own account |
| `teller` | view accounts, make transfers |
| `branch_manager` | everything a teller can **+ approve loans** |
| `auditor` | view everything (read-only) |

So: *"Amine is a `teller` → tellers can `transfer` → allow."* Clean and simple. ✅
And **Leila** is a `branch_manager`, which **inherits** `teller`, so she can transfer
*and* approve loans.

> See it run: [`hands-on-casbin/`](./hands-on-casbin/).

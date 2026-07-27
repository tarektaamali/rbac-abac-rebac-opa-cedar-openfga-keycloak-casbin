# ABAC — the theory

## Definition (simple)

**Attribute-Based Access Control**: decide access using **attributes** of the subject, the
resource, the action, and the context — not just a role. A rule is a boolean condition over
those attributes.

## Everyday example

A cinema lets you into an 18+ film based on your **age** — an attribute — not your job
title. Two people with the same "customer" role get different answers because an *attribute*
differs.

## SafiBank example — the transfer rule gets real

Chapter 1 could only say *"a teller may transfer."* ABAC adds the conditions that a bank
actually needs:

```
ALLOW transfer IF:
    role   == "teller"            (kept from RBAC)
    AND amount <= 10000 TND       (attribute of the request)
    AND hour   in 08:00..17:00    (attribute of the context)
    AND user.branch == account.branch   (attributes must match)
```

So *"Amine transfers 8,000 TND at 22:00"* → **DENY** (after hours). RBAC could never express
that. 🎯

> See it run: [`hands-on-casbin/`](./hands-on-casbin/) — the **demo** shows the same
> transfer flip from ALLOW to DENY when only the hour changes.

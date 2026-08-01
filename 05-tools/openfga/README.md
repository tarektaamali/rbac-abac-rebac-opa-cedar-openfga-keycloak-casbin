# OpenFGA — tool reference

> **Open-source Google Zanzibar: the tool for RELATIONSHIPS.** Reach for it when access
> follows ownership, sharing, or hierarchy through a chain.

## What it is
A **relationship-based authorization** server. You declare a model (`model.fga`) of types and
relations, write relationship **tuples** `(subject, relation, object)`, and ask "is this user
related to this object?" — resolved as a graph walk. **Where it runs:** a server (Zanzibar-style).

## Which models
| RBAC | ABAC | ReBAC | Policy-as-code |
|:----:|:----:|:-----:|:--------------:|
| ⚠️ possible | ❌ no (no time/amount context) | ✅ great | ⚠️ the model is code, but it's not a general policy language |

## When to reach for it
- *"His own account"*, *"shared with me"*, *"the manager of the branch that owns it"*.
- You need **tenant isolation that falls out of the graph** (no path = deny).
- Millions of objects checked fast.

## When NOT
- Rules about **time/amount/status** → that's ABAC (**OPA/Cedar**); OpenFGA can't see context.
- Simple role checks with no relationships → **Casbin/Keycloak**.

## Illustrative snippet
```
type account
  relations
    define owner: [user]
    define viewer: owner or manager from branch or auditor from branch
```

## SafiBank angle
Chapter 3 models `youssef → owns → account:123 → branch → tunis → bank → dinarbank`, so
Youssef, Leila (branch manager), and Sonia (bank auditor) each reach the account by a
different relationship path — and the other bank's users have none.

## Strengths / limits
- **+** purpose-built for relationships/sharing/hierarchy; scales; isolation is emergent.
- **−** no attribute/context logic; run a server; combine with OPA/Cedar for the full rule.

## See also
- Lab: [`03-rebac`](../../03-rebac/) · Index: [`05-tools`](../)
- Docs: https://openfga.dev/docs

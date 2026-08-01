# Casbin — tool reference

> **A lightweight authorization library that lives INSIDE your app.** Great for RBAC and
> ABAC when one service owns the decision and you don't want to run a separate engine.

## What it is
An open-source authorization **library** (Go, Python, Node, Java, …) embedded in your
process. A `model.conf` defines the shape of a rule; a `policy.csv` holds the rules **as
data**. **Where it runs:** in-process, no server.

## Which models
| RBAC | ABAC | ReBAC | Policy-as-code |
|:----:|:----:|:-----:|:--------------:|
| ✅ great | ✅ great | ⚠️ possible | ⚠️ possible (rules are data, but the engine is in-app) |

## When to reach for it
- A single service makes the decision and you want **zero extra infrastructure**.
- Your rules are role- or attribute-based and fit a `model.conf` + `policy.csv`.

## When NOT
- Many services must share one rulebook → prefer **OPA/Cedar** (externalized).
- You need relationship chains / per-object sharing → **OpenFGA**.

## Illustrative snippet
```csv
# policy.csv — permissions attach to roles, as data
p, teller, account, transfer
g, amine, teller
```

## SafiBank angle
Chapters 1–2 use Casbin for exactly the SafiBank transfer question — RBAC first, then ABAC
(amount/hour/branch) — because a single lab service owns the decision.

## Strengths / limits
- **+** tiny, fast, no server; rules-as-data; many language bindings.
- **−** in-process (each service embeds it); ReBAC and multi-service policy-as-code are not its strength.

## See also
- Labs: [`01-rbac`](../../01-rbac/), [`02-abac`](../../02-abac/) · Index: [`05-tools`](../)
- Docs: https://casbin.org/docs/overview

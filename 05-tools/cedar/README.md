# Cedar — tool reference

> **AWS's authorization language: small, typed, and ANALYZABLE.** Like OPA it externalizes
> policy — choose Cedar when you want provable, tool-checkable rules and a typed schema.

## What it is
An open-source **authorization policy language** (from AWS, used by Amazon Verified
Permissions). Policies are `permit`/`forbid` statements over **principal / action /
resource** plus a `when { … }` condition. Cedar is designed to be **analyzable** — tools can
reason about your policies (e.g. "is this permission ever granted?"). **Where it runs:** a
library/language you embed or call, with a typed schema.

## Which models
| RBAC | ABAC | ReBAC | Policy-as-code |
|:----:|:----:|:-----:|:--------------:|
| ✅ great | ✅ great | ⚠️ possible (via entity relationships) | ✅ great |

## When to reach for it
- You want **policy-as-code** with a **typed schema** and **static analysis** (provable properties).
- RBAC + ABAC rules you want small, readable, and verifiable.

## When NOT
- You're all-in on the **Kubernetes / Rego** ecosystem → **OPA** has more integrations.
- Deep relationship graphs at scale → **OpenFGA**.

## Illustrative snippet (the SafiBank transfer, in Cedar)
```cedar
permit (
    principal,
    action == Action::"transfer",
    resource
)
when {
    principal.role == "teller" &&
    principal.branch == resource.branch &&   // relationship to the owning branch
    context.amount <= 10000 &&               // ABAC
    context.hour >= 8 && context.hour < 17   // ABAC — branch hours
};
```
A teller may transfer from an account in their own branch, up to 10,000 TND, during branch
hours. *"Amine, 8,000 TND, 22:00"* → **not permitted** (the hour condition fails).

## SafiBank angle
Cedar has no lab in this repo, but the policy above answers the same canonical question as
chapters 2 and 4 — with the bonus that Cedar's analyzer could *prove* properties like "no
customer role can ever transfer."

## Strengths / limits
- **+** ergonomic, typed schema, formally analyzable; good for policy-as-code.
- **−** younger ecosystem than OPA; relationships are entity-based, not a Zanzibar graph.

## See also
- Related lab (same idea, different engine): [`04-policy-as-code`](../../04-policy-as-code/) · Index: [`05-tools`](../)
- Docs: https://www.cedarpolicy.com

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
| ⚠️ possible | ⚠️ via Conditions | ✅ great | ⚠️ the model is code, but it's not a general policy language |

> **ABAC note:** the *core* engine is pure relationships (no time/amount). But OpenFGA
> **Conditions** (CEL) let you gate a relationship on runtime context — time, IP, expiry — see
> [🧪 Advanced — Conditions](#-advanced--conditions-abac-inside-openfga) below.

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
- **+** **Conditions** add limited context (time, IP, expiry) *on* a relationship — see below.
- **−** run a server; for rich, multi-signal attribute rules a policy engine (OPA/Cedar) is still cleaner.

## 🧪 Advanced — Conditions (ABAC inside OpenFGA)

The classic Zanzibar model is pure relationships. Modern OpenFGA adds **Conditions**: a
relationship holds **only if** a [CEL](https://cel.dev) expression over *runtime context*
passes. This blends a slice of ABAC (time, IP, expiry) into ReBAC.

### The banking use case — time-boxed, IP-restricted investigation access

A suspicious transaction is flagged on **Mr. Youssef's `account:123`**. Compliance auditor
**Sonia** must investigate — but a bank can't let auditors read any account, anytime, from
anywhere. Policy:

> Sonia may view `account:123` **for this investigation only** — during **branch hours
> (08:00–17:00 Tunis time)**, **only from the bank's office network**, and the grant
> **auto-expires** after the 5-day window.

Why no single model alone fits: **RBAC** (`auditor`) sees *every* account always; **ABAC**
alone can't hold "Sonia was granted access to *this* account"; **classic ReBAC** can hold the
grant but can't expire it or gate it by time/IP. A **conditional relationship** does all of it
in one tuple.

**Model** — a conditional `investigator` relation:
```
type account
  relations
    define owner: [user]
    define investigator: [user with investigation_window]
    define viewer: owner or investigator or manager from branch

condition investigation_window(
    current_time: timestamp,
    grant_expires: timestamp,
    user_ip: ipaddress,
    office_cidr: string
) {
    current_time < grant_expires &&
    current_time.getHours("Africa/Tunis") >= 8 &&
    current_time.getHours("Africa/Tunis") < 17 &&
    user_ip.in_cidr(office_cidr)
}
```

**Tuple** — grant Sonia, with the expiry + office network baked in:
```json
{ "user": "user:sonia", "relation": "investigator", "object": "account:123",
  "condition": { "name": "investigation_window",
                 "context": { "grant_expires": "2026-08-06T00:00:00Z",
                              "office_cidr": "196.203.0.0/16" } } }
```

**Check** — pass the live context (the clock + the caller's IP):
```json
POST /check
{ "tuple_key": { "user":"user:sonia", "relation":"viewer", "object":"account:123" },
  "context": { "current_time": "2026-08-02T22:00:00Z", "user_ip": "196.203.4.5" } }
→ { "allowed": false }     // 22:00 → outside branch hours → condition fails
```

Same request at **09:00 from an office IP, before the deadline** → `allowed: true`. From a
home IP, or after `grant_expires`, or at 22:00 → `false`. The grant **self-destructs** when
the window closes — no cleanup job needed.

> **When to still prefer OPA/Cedar:** Conditions shine for *a few* context signals attached to
> a grant (expiry, hours, IP). For rich, evolving attribute policy with many signals and
> branching logic, keep that in a policy engine and let OpenFGA answer the pure "is X related
> to Y?" part. See [`04-policy-as-code`](../../04-policy-as-code/).

## See also
- Lab: [`03-rebac`](../../03-rebac/) · Index: [`05-tools`](../)
- Docs: https://openfga.dev/docs

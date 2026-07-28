# 03 · ReBAC — access by RELATIONSHIP

> **You can see this account because you OWN it — or MANAGE the branch that holds it.**
> Not a role, not an attribute: a *relationship*, followed through a chain. This is the
> Google **Zanzibar** model, and **OpenFGA** is the open-source tool for it.

## The idea in one line

Access follows **relationships** between users and objects (`owns`, `manages`, `shared with`),
often through a chain — evaluated as a walk over a graph of `(subject, relation, object)`
tuples.

- New to the concept? Read [`theory.md`](./theory.md) first.
- Want to run it? Go to [`hands-on-openfga/`](./hands-on-openfga/) and follow the README.

## When to reach for ReBAC

- Access depends on **ownership**, **sharing**, or **hierarchy** ("his own account", "shared
  with me", "the manager of the branch that owns it").
- You need answers that follow a **chain** (account → branch → bank).
- You want **tenant isolation for free**: if there's no path between a user and an object,
  access is denied — no special rule required.

## Where ReBAC stops (the important part)

ReBAC answers *"is this user **related** to this account?"* superbly. But it **cannot** see
**context**: *"...and is the amount under 10,000 TND, during branch hours?"* That's ABAC's
job — and roles (RBAC) still matter too.

Real banking rules need **all three at once**: RBAC + ABAC + ReBAC. Maintaining them in-app,
across every service, and proving them to auditors, doesn't scale.

→ That's exactly why **[`04-policy-as-code`](../04-policy-as-code/)** comes next: pull every
rule out of the app into one versioned, testable, auditable engine.

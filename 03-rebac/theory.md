# ReBAC — the theory

## Definition (simple)

**Relationship-Based Access Control**: access is decided by the **relationships** between
users and things — *owns*, *manages*, *member of*, *shared with* — often followed through a
**chain**. It's the model behind Google's **Zanzibar** and the open-source **OpenFGA**.

## Everyday example

You can read a Google Doc because someone **shared it with you** — not because of your job
title (RBAC) and not because of your age or the time of day (ABAC). The *relationship*
"shared with" is what grants access.

## SafiBank example — the ownership graph

```
user:youssef ──owner──▶ account:123 ──branch──▶ branch:tunis ──bank──▶ bank:dinarbank
user:leila   ──manager──▶ branch:tunis
user:sonia   ──auditor──▶ bank:dinarbank
```

Three people can view `account:123`, each by a **different relationship path**:

- **Youssef** — he **owns** it (direct).
- **Leila** — she **manages the branch** it belongs to (one hop).
- **Sonia** — she **audits the bank** the branch belongs to (two hops).

And `user:amine` (a teller) **cannot** — a role doesn't relate you to a *specific* account.

> See it run: [`hands-on-openfga/`](./hands-on-openfga/) — the **demo** prints the path that
> grants each person access.

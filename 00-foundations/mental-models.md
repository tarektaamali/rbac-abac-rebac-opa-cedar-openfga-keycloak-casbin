# Mental models — making the ideas stick

These are just **hooks** for the ideas in [`README.md`](./README.md). No new concepts here —
if one of the six ideas felt slippery, find its analogy below.

## authN vs authZ → the CIN card and the counter

Showing your **CIN card at the door** proves who you are — that's **authN**. Being allowed
**behind the counter** (staff only) is **authZ**. You can be past the door but still not allowed
behind the counter.

## The PEP/PDP split → the security agent and the rulebook

The **security agent** at the bank checks every request but never invents rules — he follows the
**rulebook**. The agent is the **PEP** (he enforces); the rulebook is the **PDP** (it decides).
When the agent needs a fact he doesn't have — "which branch owns this account?" — he phones the
back office: that's the **PIP**. The manager who edits the rulebook is the **PAP**.

## Multi-tenant → one building, many families

SafiBank Cloud is **one apartment building**. DinarBank and Banque de Carthage are two
**families** renting separate flats. They share the building (one codebase, one database) but
**no family can ever enter another's flat**. That wall is the tenant boundary — checked before
anything else.

## A teaser: relationships → the ownership chain

Some rules can't be answered by role or attribute alone — they follow a **chain of
relationships**:

```
Mr. Youssef ──owns──► Account #123 ──belongs to──► Tunis Branch ──belongs to──► DinarBank
```

"Leila can view Account #123 because she manages the branch it belongs to." Don't worry about
*how* yet — that's [`03-rebac`](../03-rebac/). Just notice that "who is related to what" can decide
access.

---

Next: put it into practice → [`exercises.md`](./exercises.md).

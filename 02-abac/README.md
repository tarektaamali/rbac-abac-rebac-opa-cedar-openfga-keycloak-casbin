# 02 · ABAC — access by ATTRIBUTES

> **RBAC said "you're a teller, go ahead." ABAC asks "how much, what time, whose account?"**
> This chapter keeps the role and *adds* conditions — and finally answers the question RBAC
> got wrong.

## The idea in one line

Decide with **attributes** (of the subject, resource, action, and context), not just a role.
ABAC usually **augments** RBAC — the role check stays; conditions are layered on top.

- New to the concept? Read [`theory.md`](./theory.md) first.
- Want to run it? Go to [`hands-on-casbin/`](./hands-on-casbin/) and follow the README.

## When to reach for ABAC

- A rule depends on **time, amount, location, or status** — things a role can't see.
- You're hitting **role explosion** in RBAC (`manager_sfax`, `teller_under_10k`, …). ABAC
  collapses those back into one rule with conditions.
- The same subject should get different answers in different **contexts**.

## The payoff

Remember the canonical question: *"Can teller **Amine** transfer **8,000 TND** from
**Mr. Youssef's account** at **22:00**?"* Chapter 1 said *allow* (it only saw the role).
ABAC sees the **hour** and says **DENY**. Run the lab's **demo** to watch the exact flip.

## Where ABAC gets hard (the important part)

1. **"Why was I denied?" is harder.** The answer now depends on several attributes at once,
   not a single role. Debugging and auditing get trickier.
2. **Ownership and hierarchy don't fit.** *"Only his **own** account"* or *"the manager of
   the **branch that owns** it"* are **relationships**, not attributes. You *can* fake them
   with attributes, but you must keep them all in sync, everywhere — and it gets brittle.

→ That second pain is exactly why **[`03-rebac`](../03-rebac/)** (relationships, à la Google
Zanzibar) comes next.

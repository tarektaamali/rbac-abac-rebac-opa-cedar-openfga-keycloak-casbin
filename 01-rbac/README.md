# 01 · RBAC — access by ROLE

> **You're a teller, so you can do teller things.** The simplest model, and the right
> place to start. This chapter has a **runnable lab** — then it shows you exactly where
> RBAC runs out of road.

## The idea in one line

Permissions attach to **roles**; users get roles; users inherit the permissions. To change
access, you change **data** (a role list), not code.

- New to the concept? Read [`theory.md`](./theory.md) first.
- Want to run it? Go to [`hands-on-casbin/`](./hands-on-casbin/) and follow the README.

## When to reach for RBAC

- Access depends on **who someone is in the org** (their job), not on the specific thing
  or the moment.
- The set of roles is small and stable (`teller`, `branch_manager`, `auditor`).
- You want an audit answer as simple as *"she can approve loans because she's a manager."*

## Where RBAC breaks (the important part)

Run the lab's **wall** step and you'll hit all three at once:

1. **Roles multiply.** The moment you need "managers **in Sfax**" or "tellers for loans
   **under 10,000 TND**," you start minting `manager_sfax`, `teller_loans_small`, … and the
   role list explodes.
2. **No context.** RBAC can't say *"only during branch hours (08:00–17:00)"* or *"only up
   to 10,000 TND."* It cannot see time or amount.
3. **No relationships.** RBAC can't say *"only if it's **his own** account."* It knows
   roles, not ownership.

Remember the canonical question: *"Can teller **Amine** transfer **8,000 TND** from
**Mr. Youssef's account** at **22:00**?"* RBAC answers only the *role* part and ignores the
amount, the ownership, and the hour — so it says **allow**, which is wrong. 🎯

→ Those three pains are exactly why **[`02-abac`](../02-abac/)** (attributes) comes next.

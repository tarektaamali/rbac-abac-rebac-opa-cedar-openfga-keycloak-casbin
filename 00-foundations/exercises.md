# Exercises — spot the model

A quick self-check before the first lab. **Guessing is fine — this is a preview**, not a test.
You haven't studied the three models yet, so use this cheat-sheet:

> - Rule depends on a **role** → **RBAC**
> - Rule depends on an **attribute** (time / amount / place) → **ABAC**
> - Rule depends on a **relationship** (owns / shared / member-of) → **ReBAC**
> - Rule depends on **which bank owns the data** → that's the **tenant boundary**, checked
>   *before* any model.

For each rule below, guess the model, then expand the answer.

---

**1. "Tellers can transfer."**

<details><summary>Answer</summary>

**RBAC** — it depends only on the role `teller`, nothing else.
</details>

**2. "Only during branch hours (08:00–17:00)."**

<details><summary>Answer</summary>

**ABAC** — it depends on an attribute of the context: the time of day.
</details>

**3. "Only up to 10,000 TND."**

<details><summary>Answer</summary>

**ABAC** — it depends on an attribute of the request: the amount.
</details>

**4. "Only his own account."**

<details><summary>Answer</summary>

**ReBAC** — it depends on a relationship: does this teller *own* this account?
</details>

**5. "Only accounts in his own branch."**

<details><summary>Answer</summary>

**Both are defensible.** Read as "the account's `branch` attribute equals the user's `branch`,"
it's **ABAC**. Read as "the user is *related to* the branch the account *belongs to*," it's
**ReBAC**. Models overlap — there isn't one trick answer, and that's the point.
</details>

**6. "Auditors can view everything, read-only."**

<details><summary>Answer</summary>

**RBAC** — it depends only on the role `auditor`.
</details>

**7. "Never another bank's accounts."**

<details><summary>Answer</summary>

**Not one of the three models — this is the tenant boundary.** DinarBank vs Banque de Carthage
is checked *first*, before role, attribute, or relationship. (Core idea #3.)
</details>

**8. "A branch manager can see any account in the branch she manages."**

<details><summary>Answer</summary>

**ReBAC** — it follows a relationship chain: manager → *manages* → branch → *owns* → account.
</details>

---

Notice how many rules a plain **role** can't express — time, amount, ownership, the branch chain.
That gap is exactly what the next chapters close.

**Next:** [`01-rbac`](../01-rbac/) — start with roles, then feel them break.

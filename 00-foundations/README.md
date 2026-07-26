# 00 · Foundations — the ideas everything else hangs on

> Read this chapter until the **one question** and the **PEP/PDP split** feel obvious.
> There is **nothing to run here** — the first lab is [`01-rbac`](../01-rbac/).
> When you can answer the "you're ready when…" checklist at the bottom, move on.

Everything in this repo answers **one** question, asked about SafiBank Cloud — an
imaginary SaaS banking platform two Tunisian banks pay to use (**DinarBank** and
**Banque de Carthage**). Meet the cast once; you'll see them in every chapter:

| Who | Role | Does |
|-----|------|------|
| Mr. Youssef | `customer` | Owns an account at the Tunis branch |
| Amine | `teller` | Daily operations at one branch |
| Leila | `branch_manager` | Approves bigger operations |
| Sonia | `auditor` | Read-only compliance checks |
| Karim | `admin` | Sets up the bank's users and rules |

---

## 1. authN vs authZ

**Authentication (authN)** = proving *who you are*. It happens **once**, at login.
**Authorization (authZ)** = deciding *what you may do*. It happens on **every single action**.

> Amine shows his CIN / logs in → the system knows "this is Amine, a teller at DinarBank's
> Tunis branch." That's authN. The interesting question comes next: *can he transfer 8,000 TND
> from Mr. Youssef's account?* That yes/no is authZ. **This whole repo is about authZ.**

## 2. The one question

Every authorization decision — in every chapter, with every tool — answers the same sentence:

> **Can [subject] do [action] on [resource] in [context]?**

Memorize it. Everything else is just smarter ways to answer it.

- **subject** = who is asking (Amine, Leila, Mr. Youssef)
- **action** = what they want to do (`view`, `transfer`, `approve_loan`)
- **resource** = the thing (`account`, `transaction`, `loan`)
- **context** = the surrounding facts (time, branch city, amount in TND, KYC status)

Our recurring test: *"Can teller **Amine** transfer **8,000 TND** from **Mr. Youssef's account**
at **22:00**?"* — we answer it better in each chapter.

## 3. The tenant boundary comes first 🧱

SafiBank Cloud is **one** codebase and **one** database serving **two** banks. Each bank is a
**tenant**, and their data is walled off from each other.

Before *any* rule runs, the tenant wall is checked: Amine works at **DinarBank**, so he must
**never** touch a **Banque de Carthage** account — not even to read it. A crack in this wall is a
**breach, not a bug**. That's why, in a multi-tenant system, "which tenant?" is the *first*
question, before role, attribute, or relationship.

## 4. The PEP/PDP split

Modern authorization separates *asking* from *deciding*:

- **PEP — Policy Enforcement Point:** the guard in your code that blocks or allows. It **asks**;
  it does not decide. (The line in the transfer API that says "before moving money, check.")
- **PDP — Policy Decision Point:** the brain that evaluates the rule and answers yes/no.
  (Casbin, OPA, Cedar, OpenFGA are all PDPs.)
- **PIP — Policy Information Point:** where the PDP fetches extra facts ("what branch is this
  account in?").
- **PAP — Policy Administration Point:** where humans write and manage the rules (an admin
  screen, or a Git repo).

```
Amine clicks "Transfer"
        │
        ▼
[ Your App / API ]  ── PEP: "Hey engine, is this allowed?" ──►  [ PDP ]
        ▲                                                         │
        └───────────────  allow / deny  ◄─────────────────────────┘
```

This split is the heart of the repo: your app asks, a separate engine decides.

## 5. Why authZ is hard

A real authorization system must be all three at once, while the rules keep changing:

- **Flexible** — it must express time, amount, ownership, tenant, and more.
- **Secure** — no partial failure. A leak is a breach.
- **Fast** — it runs on *every* request, not once at login.

Hold those three in tension and you understand why this needs its own tools.

## 6. The bank analogy

Tie it together with one picture:

- The **front door** (showing your CIN) = **authN**.
- What you may do **once inside** (only staff behind the counter) = **authZ**.
- Many banks sharing **one building** but never seeing each other's rooms = **multi-tenant**.

---

## ✅ You're ready for `01-rbac` when you can…

- [ ] Say the **one question** from memory: *Can [subject] do [action] on [resource] in [context]?*
- [ ] Explain the **PEP/PDP split** in one sentence (app asks, engine decides).
- [ ] Explain why the **tenant boundary** is checked before any other rule.
- [ ] Name why authorization is hard: **flexible + secure + fast**, all at once.

**Next in this chapter:**
- [`mental-models.md`](./mental-models.md) — everyday analogies that make these ideas stick.
- [`exercises.md`](./exercises.md) — a quick "spot the model" drill before the first lab.

**Then:** [`01-rbac`](../01-rbac/) — your first runnable lab.

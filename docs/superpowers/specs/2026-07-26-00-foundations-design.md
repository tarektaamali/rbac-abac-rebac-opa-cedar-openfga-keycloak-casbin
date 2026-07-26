# Design — `00-foundations/` chapter

**Date:** 2026-07-26
**Status:** Approved (design phase)
**Chapter:** `00-foundations/` — the conceptual spine of the SafiBank Cloud learning repo

---

## 1. Purpose

`00-foundations/` is the load-bearing first chapter. A reader who finishes it should
understand *what authorization is* and *how modern systems structure it* — well enough
that every later chapter (RBAC → ABAC → ReBAC → Policy-as-Code) clicks into place.

**Done-criteria for the reader.** After this chapter they can:

- State the "one question" from memory: *Can [subject] do [action] on [resource] in [context]?*
- Explain the PEP/PDP split in one sentence (app asks, engine decides).
- Explain why the tenant boundary is checked before any other rule.
- Name why authorization is hard (flexible + secure + fast, all at once).

**Explicit non-goals (YAGNI).**

- **No code, no setup, nothing to run.** The first runnable thing is `01-rbac`.
- **No per-tool detail** (Casbin/OPA/Cedar/OpenFGA/Keycloak) — that lives in `05-tools/`.
- **No full glossary.** `GLOSSARY.md` stays a separate future task; foundations *links*
  to terms rather than redefining them all.

---

## 2. Format decisions (locked)

| Decision | Choice |
|----------|--------|
| Code vs concept | **Pure concept** — prose + ASCII diagrams only |
| Active element | **One "spot the model" drill** (non-code, self-check via `<details>`) |
| File split | **Three files**: `README.md`, `mental-models.md`, `exercises.md` |
| Running example | **Tunisian banking** flavor kept throughout (SafiBank Cloud) |
| Elevated concept | **Multi-tenancy / the tenant boundary** promoted to a first-class core idea |

**Running-example cast** (reused verbatim from the repo blueprint, do not rename):

- Tenants: **DinarBank**, **Banque de Carthage** — both on one SafiBank Cloud codebase + database.
- People: **Mr. Youssef** (`customer`), **Amine** (`teller`), **Leila** (`branch_manager`),
  **Sonia** (`auditor`), **Karim** (`admin`).
- Resources: `account`, `transaction`, `loan`.
- Context: time of day · branch city (Tunis, Sfax, Sousse) · amount in **TND** · KYC status.
- Canonical test question: *"Can teller **Amine** transfer **8,000 TND** from
  **Mr. Youssef's account** at **22:00**?"*

---

## 3. File structure

```
00-foundations/
├── README.md          ← the 6 core ideas (the conceptual spine)
├── mental-models.md   ← the analogies that make the ideas stick
└── exercises.md       ← the "spot the model" drill (active, self-check)
```

---

## 4. `README.md` — the 6 core ideas

Presented in this order. Each idea = short explanation + one SafiBank example.

1. **authN vs authZ** — who you are (login, happens once) vs. what you may do
   (authorization, checked on every action). *Amine shows his CIN / logs in* → then the
   real question is *can he transfer?*

2. **The one question** — every authorization decision answers:
   *Can **[subject]** do **[action]** on **[resource]** in **[context]**?*
   The entire repo is just smarter ways to answer this one sentence. Reader should
   memorize it.

3. **The tenant boundary comes first** 🧱 — SafiBank Cloud serves DinarBank **and**
   Banque de Carthage from one codebase and one database. Before *any* rule is
   evaluated, the tenant wall is checked: Amine (DinarBank) must **never** touch a
   Banque de Carthage account. A leak across this wall is a **breach, not a bug**.

4. **The PEP/PDP split** — your app (the **PEP**) *asks*; a separate engine (the
   **PDP**) *decides*. Includes short intros to **PIP** (where the PDP fetches extra
   facts) and **PAP** (where humans write and manage rules). Include the ASCII
   request-flow diagram (app → PEP → PDP → decision → response).

5. **Why authZ is hard** — it must be **flexible** (time, amount, ownership, tenant…),
   **secure** (no partial failure — a leak is a breach), and **fast** (checked on
   *every* request) — all at once, while the rules keep changing.

6. **The bank analogy** — front door = authN; what you may do inside = authZ; many banks
   sharing one building but never seeing each other's rooms = multi-tenant. This idea
   ties 1–5 together.

**Ending of README.md:** a short "you're ready when you can…" checklist (mirrors the
done-criteria in §1) and links into `mental-models.md` and `exercises.md`.

---

## 5. `mental-models.md` — make it stick

Everyday analogies, one concrete hook per core idea. **Introduces no new concepts** —
only traction for the ideas already in `README.md`:

- CIN card at the door → authN.
- Staff-only behind the counter → authZ.
- The security agent who follows a rulebook but doesn't invent rules → PEP vs PDP.
- One apartment building, many families who never enter each other's flat → multi-tenant.
- The relationship-chain preview:
  *Youssef → owns → Account #123 → belongs to → Tunis Branch → DinarBank*
  (a teaser for ReBAC; not explained in depth here).

---

## 6. `exercises.md` — the "spot the model" drill

**Cheat-sheet up top** (so the drill is self-contained at the foundations stage, before
the reader has studied the models):

> role → **RBAC** · attribute (time/amount/place) → **ABAC** · relationship
> (owns/shared/member-of) → **ReBAC**
> *Framed as "a preview — guessing is fine, don't worry if you're unsure."*

**~8 SafiBank rules to classify:**

| # | Rule | Expected model |
|---|------|----------------|
| 1 | Tellers can transfer | RBAC |
| 2 | Only during branch hours (08:00–17:00) | ABAC |
| 3 | Only up to 10,000 TND | ABAC |
| 4 | Only his own account | ReBAC |
| 5 | Only accounts in his own branch | ABAC (or ReBAC) — both defensible |
| 6 | Auditors can view everything, read-only | RBAC |
| 7 | Never another bank's accounts (the tenant wall) | tenant check (pre-model) |
| 8 | A branch manager can see any account in the branch she manages | ReBAC |

- Each answer hidden in a GitHub-native `<details>` block with a one-line *why*.
- Rule #5 explicitly notes both ABAC and ReBAC are defensible — teaches that models
  overlap, not that there's one "right" trick.
- Rule #7 reinforces core idea #3: the tenant boundary is not one of the three models —
  it is checked first.
- **Closing bridge line to `01-rbac`:** *"Notice how many rules a plain role can't
  express — that's the gap the next chapters close."*

---

## 7. Testing / verification

No code, so "testing" means editorial verification:

- All internal links resolve (`mental-models.md`, `exercises.md`, and forward links to
  `01-rbac/`, `DECISION-TREE.md`).
- All `<details>` blocks render on GitHub (valid Markdown, blank line after `</summary>`).
- Cast names, roles, amounts, branch cities, and the canonical test question match the
  blueprint exactly (no drift).
- The "one question" wording is identical everywhere it appears across the three files.
- Markdown renders cleanly on GitHub (tables, code fences, emoji).

---

## 8. Out of scope for this spec

- `GLOSSARY.md` (separate task).
- `01-rbac` and later chapters.
- Any per-tool reference content.
- CI / linting setup for the repo.

# 00-foundations Chapter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Write the `00-foundations/` chapter — three Markdown files that teach the conceptual spine of authorization (the 6 core ideas) for the SafiBank Cloud learning repo.

**Architecture:** Pure documentation, no code. Three focused Markdown files: `README.md` (the 6 core ideas), `mental-models.md` (analogies), `exercises.md` (a non-code "spot the model" self-check drill). Each file is authored, verified editorially, then committed. Verification means "editorial checks" — links resolve, GitHub-native `<details>` blocks render, and the cast/wording match the repo blueprint exactly.

**Tech Stack:** GitHub-Flavored Markdown only. No build, no runtime, no dependencies.

## Global Constraints

Copied verbatim from the spec ([2026-07-26-00-foundations-design.md](../specs/2026-07-26-00-foundations-design.md)). Every task's requirements implicitly include this section.

- **No code, no setup, nothing to run.** The first runnable thing is `01-rbac`. Pure prose + one non-code drill.
- **No per-tool detail** (Casbin/OPA/Cedar/OpenFGA/Keycloak) — that lives in `05-tools/`.
- **No full glossary** — `GLOSSARY.md` is a separate future task; foundations *links* to terms rather than redefining them.
- **Cast names (do not rename):** Tenants **DinarBank**, **Banque de Carthage**; people **Mr. Youssef** (`customer`), **Amine** (`teller`), **Leila** (`branch_manager`), **Sonia** (`auditor`), **Karim** (`admin`); resources `account`, `transaction`, `loan`; context = time of day · branch city (Tunis, Sfax, Sousse) · amount in **TND** · KYC status.
- **Canonical test question (verbatim, identical everywhere it appears):** *"Can teller **Amine** transfer **8,000 TND** from **Mr. Youssef's account** at **22:00**?"*
- **The "one question" (verbatim, identical everywhere it appears):** *Can **[subject]** do **[action]** on **[resource]** in **[context]**?*
- **Tenant boundary is a first-class core idea**, checked *before* any model — it is **not** one of the three models (RBAC/ABAC/ReBAC).
- **`<details>` blocks must render on GitHub:** put a blank line after `</summary>` and before `</details>`.

---

## File Structure

```
00-foundations/
├── README.md          ← Task 1 — the 6 core ideas (conceptual spine)
├── mental-models.md   ← Task 2 — analogies that make the ideas stick
└── exercises.md       ← Task 3 — the "spot the model" self-check drill
docs/superpowers/plans/verify-foundations.md  ← Task 4 — final cross-file verification (throwaway checklist, not committed to chapter)
```

Task order matters: `README.md` first (it defines the 6 ideas and the exact wording the other two files reference), then `mental-models.md` and `exercises.md` (both point back to it), then a final cross-file consistency pass.

---

### Task 1: `00-foundations/README.md` — the 6 core ideas

**Files:**
- Create: `00-foundations/README.md`

**Interfaces:**
- Consumes: cast + canonical wording from Global Constraints.
- Produces: the canonical wording of **the "one question"** and **the 6 core-idea headings** that Tasks 2 and 3 link to and must not contradict. Heading anchors produced: `#1-authn-vs-authz`, `#2-the-one-question`, `#3-the-tenant-boundary-comes-first`, `#4-the-pepp­dp-split`, `#5-why-authz-is-hard`, `#6-the-bank-analogy` (GitHub auto-generates anchors from heading text; Tasks 2–3 link to these files, not to sub-anchors, so exact anchor slugs are not load-bearing).

- [ ] **Step 1: Draft the file header + intro**

Create `00-foundations/README.md` starting with:

```markdown
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
```

- [ ] **Step 2: Write core ideas 1–3**

Append:

```markdown
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
```

- [ ] **Step 3: Write core ideas 4–6**

Append:

```markdown
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
```

- [ ] **Step 4: Write the "you're ready when…" checklist + links**

Append:

```markdown
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
```

- [ ] **Step 5: Verify the file (editorial checks)**

Run: `test -f 00-foundations/README.md && grep -c "Can \[subject\] do \[action\] on \[resource\] in \[context\]" 00-foundations/README.md`
Expected: file exists; the "one question" appears (count ≥ 1).

Run: `grep -F "8,000 TND" 00-foundations/README.md && grep -F "Banque de Carthage" 00-foundations/README.md`
Expected: both match — canonical test question and second tenant are present.

Manually confirm: the ASCII diagram is inside a fenced code block, and there are no per-tool deep-dives (only the one-line "Casbin, OPA, Cedar, OpenFGA are all PDPs" naming is allowed).

- [ ] **Step 6: Commit**

```bash
git add 00-foundations/README.md
git commit -m "docs(foundations): add README with the 6 core ideas"
```

---

### Task 2: `00-foundations/mental-models.md` — analogies

**Files:**
- Create: `00-foundations/mental-models.md`

**Interfaces:**
- Consumes: the 6 core ideas and their headings from Task 1 (`README.md`). Introduces **no new concepts** — only analogies for ideas already defined there.
- Produces: nothing later tasks depend on except a back-link target (`./mental-models.md`, already linked from Task 1 Step 4).

- [ ] **Step 1: Draft the full file**

Create `00-foundations/mental-models.md`:

```markdown
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
```

- [ ] **Step 2: Verify the file (editorial checks)**

Run: `test -f 00-foundations/mental-models.md && grep -F "Mr. Youssef ──owns──► Account #123" 00-foundations/mental-models.md`
Expected: file exists; the relationship chain is present and matches the blueprint's arrows.

Manually confirm: **no new concept** is introduced (only authN/authZ, PEP/PDP/PIP/PAP, multi-tenant, and the ReBAC teaser — all already in `README.md`), and the two internal links (`./README.md`, `./exercises.md`) and one forward link (`../03-rebac/`) are present.

- [ ] **Step 3: Commit**

```bash
git add 00-foundations/mental-models.md
git commit -m "docs(foundations): add mental-models analogies"
```

---

### Task 3: `00-foundations/exercises.md` — the "spot the model" drill

**Files:**
- Create: `00-foundations/exercises.md`

**Interfaces:**
- Consumes: the RBAC/ABAC/ReBAC naming and the tenant-boundary framing from Task 1.
- Produces: the closing bridge line into `01-rbac`.

- [ ] **Step 1: Draft the intro + cheat-sheet**

Create `00-foundations/exercises.md`:

```markdown
# Exercises — spot the model

A quick self-check before the first lab. **Guessing is fine — this is a preview**, not a test.
You haven't studied the three models yet, so use this cheat-sheet:

> - Rule depends on a **role** → **RBAC**
> - Rule depends on an **attribute** (time / amount / place) → **ABAC**
> - Rule depends on a **relationship** (owns / shared / member-of) → **ReBAC**
> - Rule depends on **which bank owns the data** → that's the **tenant boundary**, checked
>   *before* any model.

For each rule below, guess the model, then expand the answer.
```

- [ ] **Step 2: Write the 8 drill items (with `<details>` answer keys)**

Append (note the blank line after each `</summary>` — required for GitHub rendering):

```markdown
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
```

- [ ] **Step 3: Write the closing bridge line**

Append:

```markdown
---

Notice how many rules a plain **role** can't express — time, amount, ownership, the branch chain.
That gap is exactly what the next chapters close.

**Next:** [`01-rbac`](../01-rbac/) — start with roles, then feel them break.
```

- [ ] **Step 4: Verify the file (editorial checks)**

Run: `grep -c "<details>" 00-foundations/exercises.md && grep -c "</details>" 00-foundations/exercises.md`
Expected: both counts equal **8** (every drill item opens and closes a `<details>`).

Run: `awk '/<\/summary>/{getline nl; if (nl != "") print "MISSING BLANK LINE after summary"}' 00-foundations/exercises.md`
Expected: **no output** (a blank line follows every `</summary>`, so GitHub renders the answers).

Manually confirm: item #7 names the tenant boundary as *not* a model, item #5 marks both ABAC and ReBAC defensible, and the closing line links to `../01-rbac/`.

- [ ] **Step 5: Commit**

```bash
git add 00-foundations/exercises.md
git commit -m "docs(foundations): add spot-the-model exercises"
```

---

### Task 4: Cross-file consistency pass

**Files:**
- Read-only: `00-foundations/README.md`, `00-foundations/mental-models.md`, `00-foundations/exercises.md`

**Interfaces:**
- Consumes: all three files from Tasks 1–3.
- Produces: a clean, internally consistent chapter (no new content unless a check fails).

- [ ] **Step 1: Verify wording is identical across files**

Run: `grep -rF "Can [subject] do [action] on [resource] in [context]" 00-foundations/`
Expected: appears in `README.md` (the "one question" wording is byte-identical wherever it recurs).

Run: `grep -rn "Banque de Carthage\|DinarBank\|Mr. Youssef\|8,000 TND" 00-foundations/`
Expected: cast names and the canonical amount are spelled consistently — no "Carthage Bank", "Dinar Bank", "Youssef" without "Mr.", or "8000 TND" variants.

- [ ] **Step 2: Verify all internal links resolve**

Run: `grep -rn "](\./\|](\.\./" 00-foundations/`
Expected: every relative link points to a real target. Confirm `./README.md`, `./mental-models.md`, `./exercises.md` exist; note that `../01-rbac/` and `../03-rebac/` are **intentional forward links** to not-yet-created chapters (acceptable — they're the roadmap).

- [ ] **Step 3: Fix any drift, then commit (only if changes were needed)**

If Steps 1–2 surfaced inconsistencies, fix them inline in the affected file(s), then:

```bash
git add 00-foundations/
git commit -m "docs(foundations): fix cross-file wording/link drift"
```

If no changes were needed, skip the commit — the chapter is done.

---

## Self-Review (completed during planning)

**1. Spec coverage:**
- Spec §3 (three-file structure) → Tasks 1–3. ✅
- Spec §4 (6 core ideas, in order) → Task 1 Steps 2–3. ✅
- Spec §4 ending checklist → Task 1 Step 4. ✅
- Spec §5 (mental-models, no new concepts) → Task 2. ✅
- Spec §6 (drill: cheat-sheet, 8 rules, `<details>`, rule #5 both-defensible, rule #7 tenant, bridge line) → Task 3. ✅
- Spec §7 (editorial verification: links, `<details>` render, cast/wording match, one-question identical) → verification steps in each task + Task 4. ✅
- Spec §2 (Tunisian flavor, multi-tenant elevated) → cast in Task 1 Step 1, idea #3 in Step 2, drill #7 in Task 3. ✅

**2. Placeholder scan:** No TBD/TODO/"implement later". Every code/prose step shows the actual Markdown to write. ✅

**3. Type consistency (here: wording consistency):** The "one question" and canonical test question are quoted identically in the Global Constraints and every task. Cast names match the blueprint. Task 4 exists specifically to catch any drift. ✅

# 04-policy-as-code Chapter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `04-policy-as-code/` chapter — a real OPA/Rego policy that unifies RBAC + ABAC + ReBAC in one tested `allow` rule (run via `opa test`/`opa eval`), plus the chapter docs.

**Architecture:** Native OPA workflow, no server/Docker/Python. `hands-on-opa/transfer.rego` is one `allow` rule combining a role check (RBAC), amount/hour limits (ABAC), and a `manages`/branch relationship (ReBAC, as facts in `input`). `transfer_test.rego` holds real `opa test` unit cases (the tests are part of the deliverable). `input.example.json` drives `opa eval`. Three Markdown files teach the concept and end with a recap → `05`/`06`/`07`.

**Tech Stack:** OPA (`opa` binary, ≥1.0 / Rego v1), Rego. GitHub-Flavored Markdown. No Python, no venv.

## Global Constraints

Copied verbatim from the spec ([2026-07-28-04-policy-as-code-design.md](../specs/2026-07-28-04-policy-as-code-design.md)), refined by a verified spike (see notes). Every task's requirements implicitly include this section.

- **Engine:** OPA + Rego, native CLI only — `opa test`, `opa eval`. **No server, bundles, HTTP API, Docker, or Python.** Prerequisite: the `opa` binary (`brew install opa`).
- **Rego v1 (OPA ≥1.0):** `if` and `contains` are built-in — **do NOT add `import future.keywords…`** (verified: the policy compiles clean without it under opa 1.19; the import is unnecessary in v1). Rules use the `NAME if { … }` form.
- **One policy, one action (`transfer`)**, package `safibank.transfer`. No extra rules/policies.
- **Unify all three models in one `allow` rule**, each a visible clause: RBAC = `input.subject.role`; ABAC = `input.amount` + `input.hour`; ReBAC = the `manages`/branch relationship.
- **ReBAC is relationship facts in `input`** (`subject.manages`, `subject.branch`, `account.branch`, `account.owner`) — **no graph traversal** in Rego.
- **Transfer is staff-only** — teller of the owning branch, or the manager who `manages` it. **No customer/owner-transfer path** (would contradict chapters 1–2).
- **Thresholds (verbatim):** `input.amount <= 10000`, `input.hour >= 8`, `input.hour < 17` (17:00 exclusive; 10,000 inclusive).
- **Tests are reader-facing** (`opa test`), part of the deliverable — not hidden.
- **Canonical question:** *"Can teller Amine transfer 8,000 TND from Mr. Youssef's account at 22:00?"* → DENY (hour); at 09:00 → ALLOW.
- **Ending is a recap + where-next** (→ `05-tools`, `06-domains`, `07-capstone`), not a limitation "wall."
- **Does not modify chapters 1–3.**

---

## File Structure

```
04-policy-as-code/
├── README.md                 ← Task 3 — concept · one-PDP-many-PEPs · where next
├── theory.md                 ← Task 3 — definition + everyday example + the unified rule
└── hands-on-opa/
    ├── transfer.rego         ← Task 1 — the unified allow policy
    ├── transfer_test.rego    ← Task 1 — real opa test unit cases
    ├── input.example.json    ← Task 1 — sample input for opa eval
    └── README.md             ← Task 2 — install opa · opa test · opa eval
```

Task order: **1** the policy + tests + sample (TDD via `opa test`), **2** the lab run-guide, **3** the chapter docs, **4** a consistency pass.

**Prerequisite (once, before Task 1):**
```bash
opa version   # if missing: brew install opa   (macOS). Requires OPA >= 1.0.
```

All shell commands below assume `04-policy-as-code/hands-on-opa/` unless a path says otherwise.

---

### Task 1: The unified policy + tests + sample input

**Files:**
- Create: `04-policy-as-code/hands-on-opa/transfer_test.rego`
- Create: `04-policy-as-code/hands-on-opa/transfer.rego`
- Create: `04-policy-as-code/hands-on-opa/input.example.json`

**Interfaces:**
- Consumes: nothing (first task) — only the `opa` binary.
- Produces: package `safibank.transfer` exposing boolean rule `allow`, decided from an `input` shaped as `{subject:{role,branch,manages}, account:{branch,owner}, amount, hour}`. Task 2's README documents the `opa test`/`opa eval` commands against these files.

- [ ] **Step 1: Write the failing tests** `transfer_test.rego`

```rego
package safibank.transfer

test_teller_same_branch_in_hours_allowed if {
	allow with input as {"subject": {"role": "teller", "branch": "tunis", "manages": ""}, "account": {"branch": "tunis", "owner": "youssef"}, "amount": 8000, "hour": 9}
}

test_after_hours_denied if {
	not allow with input as {"subject": {"role": "teller", "branch": "tunis", "manages": ""}, "account": {"branch": "tunis", "owner": "youssef"}, "amount": 8000, "hour": 22}
}

test_over_limit_denied if {
	not allow with input as {"subject": {"role": "teller", "branch": "tunis", "manages": ""}, "account": {"branch": "tunis", "owner": "youssef"}, "amount": 12000, "hour": 9}
}

test_wrong_branch_denied if {
	not allow with input as {"subject": {"role": "teller", "branch": "tunis", "manages": ""}, "account": {"branch": "sfax", "owner": "youssef"}, "amount": 8000, "hour": 9}
}

test_manager_of_managed_branch_allowed if {
	allow with input as {"subject": {"role": "branch_manager", "branch": "tunis", "manages": "tunis"}, "account": {"branch": "tunis", "owner": "youssef"}, "amount": 8000, "hour": 9}
}

test_manager_of_other_branch_denied if {
	not allow with input as {"subject": {"role": "branch_manager", "branch": "sfax", "manages": "sfax"}, "account": {"branch": "tunis", "owner": "youssef"}, "amount": 8000, "hour": 9}
}
```

- [ ] **Step 2: Run the tests to verify they fail**

Run (from `04-policy-as-code/hands-on-opa/`):
```bash
opa test .
```
Expected: FAIL — `rego_unsafe_var_error: var allow is unsafe` (the `allow` rule doesn't exist yet).

- [ ] **Step 3: Write the policy** `transfer.rego`

```rego
package safibank.transfer

# Under OPA 1.0+ (Rego v1) `if` is built in — no `import future.keywords` needed.

default allow := false

# You may transfer if the amount and hour are within policy (ABAC) AND you are
# staff of the branch that owns the account (RBAC role + ReBAC relationship).
allow if {
	input.amount <= 10000 # ABAC — amount limit (inclusive)
	input.hour >= 8 # ABAC — branch hours start
	input.hour < 17 # ABAC — branch hours end (17:00 exclusive)
	staff_of_owning_branch
}

# A teller of the branch that owns the account …
staff_of_owning_branch if {
	input.subject.role == "teller" # RBAC
	input.subject.branch == input.account.branch # relationship to the owning branch
}

# … or the manager who MANAGES that branch.
staff_of_owning_branch if {
	input.subject.role == "branch_manager" # RBAC
	input.subject.manages == input.account.branch # ReBAC — the "manages" relationship
}
```

- [ ] **Step 4: Run the tests to verify they pass**

Run (from `04-policy-as-code/hands-on-opa/`):
```bash
opa test . -v
```
Expected: PASS — `PASS: 6/6` (all six named cases pass).

- [ ] **Step 5: Create `input.example.json`** and verify `opa eval`

```json
{
  "subject": { "role": "teller", "branch": "tunis", "manages": "" },
  "account": { "branch": "tunis", "owner": "youssef" },
  "amount": 8000,
  "hour": 9
}
```

Run (from `04-policy-as-code/hands-on-opa/`):
```bash
opa eval -d transfer.rego -i input.example.json "data.safibank.transfer.allow" --format raw
```
Expected: prints `true`. (Change `"hour"` to `22` and it prints `false` — the canonical flip.)

- [ ] **Step 6: Commit**

```bash
git add 04-policy-as-code/hands-on-opa/transfer.rego 04-policy-as-code/hands-on-opa/transfer_test.rego 04-policy-as-code/hands-on-opa/input.example.json
git commit -m "feat(04-policy-as-code): add unified RBAC+ABAC+ReBAC transfer policy with opa tests"
```

---

### Task 2: Lab run-guide (`hands-on-opa/README.md`)

**Files:**
- Create: `04-policy-as-code/hands-on-opa/README.md`

**Interfaces:**
- Consumes: the three files + commands from Task 1.
- Produces: a link target for Task 3.

- [ ] **Step 1: Write the file**

````markdown
# Hands-on: policy-as-code with OPA (Rego)

The transfer rule you already know — but this time it lives **outside the app**, as a
versioned, tested policy. There's no interactive program to run: you write a policy, you
**test** it, and you **query** it. That's the whole point — the rules left the app.

## Prerequisite

Install the **OPA** binary (one file, no server, no Docker):

```bash
brew install opa      # macOS   (see openpolicyagent.org for Linux/Windows)
opa version           # needs OPA >= 1.0
```

## Run the tests

```bash
cd 04-policy-as-code/hands-on-opa
opa test . -v
```

You should see `PASS: 6/6`. Those tests (`transfer_test.rego`) ship *with* the policy — in
policy-as-code, the tests are part of the deliverable, versioned in Git alongside the rules.

## Ask it a question live

```bash
opa eval -d transfer.rego -i input.example.json "data.safibank.transfer.allow" --format raw
```

Prints `true`. Now open `input.example.json`, change `"hour": 9` to `"hour": 22`, and run it
again → `false`. That's the canonical *"Amine at 22:00"* transfer, correctly **denied** — by
an engine that lives outside any application.

## What to notice

1. **All three models, one rule.** `transfer.rego`'s `allow` combines a **role** (RBAC),
   the **amount/hour** limits (ABAC), and the **`manages`/branch relationship** (ReBAC) — in
   a single reviewed file. Chapters 1–3 taught these separately; here they compose.
2. **The rule left the app.** No Python, no `if` buried in a handler. Any service — mobile,
   web, ATM backend — can ask this same policy the same question, so rules can't drift.
3. **It's tested and versioned.** `opa test` is how you prove a rule before shipping it, and
   the whole policy is a text file in Git — exactly what an auditor wants to review.

## Where real ReBAC lives

Here the relationship facts (`account.owner`, `subject.manages`) arrive **in the input**.
In production, the graph answer ("is this user related to this account?") would come from
**OpenFGA** (see [`03-rebac`](../../03-rebac/)) and be handed to OPA as input — OPA composes
with a relationship engine rather than replacing it.

## The files

| File | What it is |
|------|------------|
| `transfer.rego` | The policy: one `allow` rule unifying RBAC + ABAC + ReBAC. |
| `transfer_test.rego` | Real `opa test` unit cases — part of the deliverable. |
| `input.example.json` | A sample request for `opa eval`. |
````

- [ ] **Step 2: Verify**

Run (from repo root):
```bash
test -f 04-policy-as-code/hands-on-opa/README.md && \
grep -q "opa test" 04-policy-as-code/hands-on-opa/README.md && \
grep -q "opa eval" 04-policy-as-code/hands-on-opa/README.md && \
grep -q "03-rebac" 04-policy-as-code/hands-on-opa/README.md && echo OK
```
Expected: `OK`.

- [ ] **Step 3: Commit**

```bash
git add 04-policy-as-code/hands-on-opa/README.md
git commit -m "docs(04-policy-as-code): add hands-on OPA lab run guide"
```

---

### Task 3: Chapter docs (`04-policy-as-code/README.md` + `theory.md`)

**Files:**
- Create: `04-policy-as-code/README.md`
- Create: `04-policy-as-code/theory.md`

**Interfaces:**
- Consumes: the lab folder from Tasks 1–2.
- Produces: chapter entry points + the arc-closing "where next" links.

- [ ] **Step 1: Write `04-policy-as-code/theory.md`**

```markdown
# Policy-as-code — the theory

## Definition (simple)

**Policy-as-code**: authorization rules are written as **code** — versioned in Git, **tested**,
and enforced by an **external engine** — instead of `if` statements scattered through the
app. The app (a **PEP**) asks; the engine (a **PDP**) decides.

## Everyday example

One **rulebook**, many **security guards**. Instead of every guard memorising the rules (and
each remembering them slightly differently), there's a single written rulebook they all
consult. Update the rulebook once, and every guard is instantly up to date.

## Why banking especially needs it

Auditors and regulators ask: *"prove who could access this account, and why."* If the rule
is one reviewed file in Git — tested, with a full history of who changed what — you can
answer instantly. If it's `if` statements spread across a mobile app, a web app, and an ATM
backend, you can't.

## The unified rule

Chapters 1–3 built three models separately. Policy-as-code is where they **compose** — one
`allow` rule in [`hands-on-opa/transfer.rego`](./hands-on-opa/transfer.rego):

- **RBAC** — `input.subject.role` must be `teller` or `branch_manager`.
- **ABAC** — `input.amount <= 10000` and the hour is within `08:00–17:00`.
- **ReBAC** — the subject is *related* to the account: a teller of its branch, or the
  manager who `manages` that branch.

*"Amine transfers 8,000 TND at 22:00"* → **DENY** (the hour), from an engine outside the app.

> See it run: [`hands-on-opa/`](./hands-on-opa/) — write the policy, `opa test` it, `opa eval` it.
```

- [ ] **Step 2: Write `04-policy-as-code/README.md`**

```markdown
# 04 · Policy-as-code — pull the rules OUT of the app

> **The same transfer rule — but now it's versioned, tested code that lives outside every
> service.** This is where RBAC, ABAC, and ReBAC stop being three separate ideas and become
> one rulebook. The tool is **OPA** (Open Policy Agent), the language is **Rego**.

## The idea in one line

Write authorization as **external, tested, versioned code**; the app **asks**, a shared
engine **decides** — so every service gets the same answer and auditors get one file to read.

- New to the concept? Read [`theory.md`](./theory.md) first.
- Want to run it? Go to [`hands-on-opa/`](./hands-on-opa/) and follow the README.

## The payoff — one PDP, many PEPs

```
mobile app ─┐
web app    ─┼─► ask ─► [ OPA: transfer.rego ] ─► allow / deny
ATM backend ┘
```

Every service (PEP) asks the same policy (PDP). The rule can't drift between them, because
there's only **one** rule. Change it once, test it once (`opa test`), ship it everywhere.

## When to reach for policy-as-code

- The **same rule** is enforced in more than one service and must not drift.
- You need to **test** authorization rules and **review** their history (audit, compliance).
- Your rules combine **role + attributes + relationships** and you want them in one place.

## The whole picture

This chapter unifies the three models you learned:

- **RBAC** (ch1) — the role gate.
- **ABAC** (ch2) — the amount/hour limits.
- **ReBAC** (ch3) — the ownership/branch relationship.

One tested Rego rule answers the canonical question correctly, from outside the app.

## Where next

You've now met all three models **and** learned to externalise them. From here:

- **[`05-tools`](../05-tools/)** — pick the right tool for the job (Casbin, OPA, Cedar,
  OpenFGA, Keycloak): none does everything; they compose.
- **[`06-domains`](../06-domains/)** — *where* you enforce (APIs, SaaS, Kubernetes, cloud-native).
- **[`07-capstone`](../07-capstone/)** — one small SafiBank app using RBAC → ABAC → ReBAC end to end.
```

- [ ] **Step 3: Verify**

Run (from repo root):
```bash
test -f 04-policy-as-code/README.md && test -f 04-policy-as-code/theory.md && \
grep -q "hands-on-opa" 04-policy-as-code/README.md && \
grep -q "05-tools" 04-policy-as-code/README.md && \
grep -q "07-capstone" 04-policy-as-code/README.md && \
grep -Fq "one PDP, many PEPs" 04-policy-as-code/README.md && echo OK
```
Expected: `OK`.

- [ ] **Step 4: Commit**

```bash
git add 04-policy-as-code/README.md 04-policy-as-code/theory.md
git commit -m "docs(04-policy-as-code): add chapter README and theory"
```

---

### Task 4: Cross-file consistency pass

**Files:**
- Read-only: everything under `04-policy-as-code/`

**Interfaces:**
- Consumes: all files from Tasks 1–3.
- Produces: a clean, internally consistent chapter (no new content unless a check fails).

- [ ] **Step 1: Re-run the policy tests**

Run (from `04-policy-as-code/hands-on-opa/`):
```bash
opa test . -v
```
Expected: `PASS: 6/6`.

- [ ] **Step 2: Confirm each model has a visible clause in the policy**

Run (from repo root):
```bash
grep -q "role ==" 04-policy-as-code/hands-on-opa/transfer.rego && echo "RBAC clause present"
grep -Eq "input.amount|input.hour" 04-policy-as-code/hands-on-opa/transfer.rego && echo "ABAC clause present"
grep -q "manages ==" 04-policy-as-code/hands-on-opa/transfer.rego && echo "ReBAC clause present"
```
Expected: all three "clause present" lines print.

- [ ] **Step 3: Confirm no forbidden constructs / no future.keywords import**

Run (from repo root):
```bash
echo "-- no future.keywords import (Rego v1):"
grep -n "future.keywords" 04-policy-as-code/hands-on-opa/transfer.rego && echo "  FOUND (remove it)" || echo "  none — good"
echo "-- no owner/customer transfer path (staff-only):"
grep -n "account.owner ==" 04-policy-as-code/hands-on-opa/transfer.rego && echo "  FOUND owner-transfer path (BAD)" || echo "  none — good (staff-only)"
echo "-- forward links to 05/06/07:"
grep -rl "05-tools" 04-policy-as-code/ ; grep -rl "07-capstone" 04-policy-as-code/
```
Expected: no `future.keywords`; no `account.owner ==` gate in the policy; `05-tools` and `07-capstone` linked from the chapter README.

- [ ] **Step 4: Fix any drift, then commit (only if changes were needed)**

If Steps 2–3 surfaced problems, fix inline, then:
```bash
git add 04-policy-as-code/
git commit -m "docs(04-policy-as-code): fix cross-file consistency"
```
If nothing needed fixing, skip the commit — the chapter is done.

---

## Self-Review (completed during planning)

**1. Spec coverage:**
- Spec §3 file structure → Tasks 1–3 create every file (no requirements.txt/venv). ✅
- Spec §4 policy (unified `allow`, visible clause per model, thresholds, staff-only) → Task 1 Step 3. ✅
- Spec §5 tests (6 named cases incl. two ReBAC/branch denials) → Task 1 Step 1. ✅
- Spec §6 `opa eval` + input.example.json (the flip) → Task 1 Step 5. ✅
- Spec §7 verification (`opa test`, editorial) → Task 1 + Task 4. ✅
- Spec §1 done-criteria (define policy-as-code, read the unified rule, run opa test, one-PDP-many-PEPs) → theory.md + README.md in Task 3. ✅
- Spec §2 recap-not-wall ending + `05/06/07` links → Task 3 README "Where next". ✅

**2. Placeholder scan:** No TBD/TODO. Every code and doc step is complete. The policy, all six tests, the failing-state message (`rego_unsafe_var_error: var allow is unsafe`), and the `opa eval` output (`true`) were verified against opa 1.19 before writing this plan; the `future.keywords` import was confirmed unnecessary under Rego v1. ✅

**3. Type consistency:** The `input` shape `{subject:{role,branch,manages}, account:{branch,owner}, amount, hour}` is identical across `transfer.rego`, all `transfer_test.rego` cases, and `input.example.json`. The queried path `data.safibank.transfer.allow` matches the package `safibank.transfer` and rule `allow` everywhere it appears (tests, eval, README). ✅

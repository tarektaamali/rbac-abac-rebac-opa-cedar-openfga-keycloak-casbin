# Design — `04-policy-as-code/` chapter

**Date:** 2026-07-28
**Status:** Approved (design phase)
**Chapter:** `04-policy-as-code/` — pull the rules OUT of the app; the capstone of the model arc

---

## 1. Purpose

`04-policy-as-code/` is where the three models chapters 1–3 taught in isolation get
**unified in one place** and pulled **out of the application** into a versioned, tested,
external engine. It is the payoff the `03-rebac` wall promised. The tool is **OPA** (Open
Policy Agent) and its language **Rego**, run through OPA's *native* workflow — no server,
no Docker, no Python: a real `.rego` policy, real `opa test` unit tests, and `opa eval`
for ad-hoc queries.

The chapter deliberately *looks different* from chapters 1–3 (no interactive Python "app"):
that difference is the lesson — the rules have left the app and now live as code that is
tested and versioned on their own.

**Done-criteria for the reader.** After this chapter they can:

- Explain policy-as-code: authorization rules written as **external code**, versioned in Git,
  **tested**, and enforced by a shared engine — instead of `if` statements in the app.
- Read a Rego `allow` rule that combines **RBAC + ABAC + ReBAC** in one place.
- Run `opa test` and see the canonical scenarios (incl. the 22:00 flip) pass.
- Explain the PEP/PDP payoff: **one PDP, many PEPs** — mobile/web/ATM ask the same policy,
  so rules can't drift between services; and auditors get one reviewed file to inspect.

**Explicit non-goals (YAGNI).**

- **No graph traversal in Rego.** ReBAC appears as **relationship facts in `input`** (the
  account's owner, the branch a manager manages) — not a Zanzibar graph walk. Real graph
  ReBAC stays in OpenFGA; the README notes OPA composes with it.
- **No server, no bundles, no HTTP API, no Docker, no Python.** Native CLI only:
  `opa test`, `opa eval`.
- **One policy, one action (`transfer`).** No multi-policy suite, no unrelated rules.
- No Keycloak/identity integration (that's `05-tools/keycloak/`).
- This chapter does not modify chapters 1–3.

---

## 2. Decisions (locked)

| Decision | Choice |
|----------|--------|
| Engine / language | **OPA + Rego**, native workflow (`opa test`, `opa eval`) — one binary, no server |
| Experience | **No interactive app** — a policy + its tests + a query tool. The difference is the lesson. |
| Policy scope | **Unify all three models in one `allow` rule** (RBAC role · ABAC amount/hour · ReBAC `manages`/branch relationship) |
| ReBAC representation | **Relationship facts in `input`** (owner, managed branch), not graph traversal |
| Tests | **Real `opa test`** — reader-facing, part of the deliverable (policy ships with its tests) |
| Ending | **Recap + where-next** (→ `05-tools`, `06-domains`, `07-capstone`), not a limitation "wall" |
| Prerequisite | The `opa` binary (`brew install opa` on macOS). Verified to run green before plan handoff. |

**Running-example continuity:** the canonical question — *"Can teller **Amine** transfer
**8,000 TND** from **Mr. Youssef's account** at **22:00**?"* — resolves to **DENY** (ABAC
hour), and to **ALLOW** at 09:00, exactly matching chapter 2. Cast/branches: Amine (teller,
tunis), Leila (branch_manager, manages tunis), accounts in `tunis`/`sfax`, owner `youssef`.

---

## 3. File structure

```
04-policy-as-code/
├── README.md                 ← concept · one-PDP-many-PEPs · where next
├── theory.md                 ← definition + everyday example + the unified rule explained
└── hands-on-opa/
    ├── transfer.rego         ← the unified allow policy
    ├── transfer_test.rego    ← real OPA unit tests (opa test)
    ├── input.example.json    ← sample input for opa eval
    └── README.md             ← install opa · run opa test · query with opa eval
```

No `requirements.txt`, no venv — the only dependency is the `opa` binary.

---

## 4. The policy (`transfer.rego`)

```rego
package safibank.transfer

import future.keywords.if

default allow := false

# You may transfer if the amount and hour are within policy (ABAC) AND you are
# staff of the branch that owns the account (RBAC role + ReBAC relationship).
allow if {
    input.amount <= 10000                 # ABAC — amount limit (inclusive)
    input.hour >= 8                        # ABAC — branch hours start
    input.hour < 17                        # ABAC — branch hours end (17:00 exclusive)
    staff_of_owning_branch
}

# A teller of the branch that owns the account …
staff_of_owning_branch if {
    input.subject.role == "teller"                    # RBAC
    input.subject.branch == input.account.branch      # relationship to the owning branch
}

# … or the manager who MANAGES that branch.
staff_of_owning_branch if {
    input.subject.role == "branch_manager"            # RBAC
    input.subject.manages == input.account.branch     # ReBAC — the "manages" relationship
}
```

**`input` shape:**

```json
{
  "subject": { "role": "teller", "branch": "tunis", "manages": "" },
  "account": { "branch": "tunis", "owner": "youssef" },
  "amount": 8000,
  "hour": 9
}
```

**Model contributions (each a visible clause):** RBAC = `role`; ABAC = `amount` + `hour`;
ReBAC = the `manages` relationship (and the teller's tie to the owning branch). The
`account.owner` fact is present in `input` so the reader sees OPA *can* consume ownership,
and the README notes that in production the relationship answer would come from OpenFGA.

---

## 5. The tests (`transfer_test.rego`)

Real OPA unit tests, run with `opa test . -v`. Reader-facing — the tests are part of the
deliverable. Cover the canonical scenarios (mirroring chapter 2's demo):

| Test name | Input gist | Asserts |
|-----------|-----------|---------|
| `test_teller_same_branch_in_hours_allowed` | teller/tunis, acct tunis, 8000, 09:00 | `allow` |
| `test_after_hours_denied` | same, 22:00 | `not allow` (the canonical flip) |
| `test_over_limit_denied` | same, 12000, 09:00 | `not allow` |
| `test_wrong_branch_denied` | teller/tunis, acct **sfax**, 8000, 09:00 | `not allow` (relationship/branch) |
| `test_manager_of_managed_branch_allowed` | branch_manager manages tunis, acct tunis, 8000, 09:00 | `allow` |
| `test_manager_of_other_branch_denied` | branch_manager manages **sfax**, acct tunis, 8000, 09:00 | `not allow` (ReBAC: manages the wrong branch) |

Each test uses `allow with input as { … }`.

---

## 6. Ad-hoc queries (`opa eval`)

`input.example.json` holds a sample request (teller/tunis, acct tunis, 8000, 09:00 → allow).
The lab README shows:

```bash
opa eval -d transfer.rego -i input.example.json "data.safibank.transfer.allow"
```

→ `true`. The reader edits `hour` to `22`, re-runs, and watches it flip to `false` — the
chapter-2 experience, now against an **external** engine.

---

## 7. Testing / verification

**Policy tests:** `opa test . -v` in `hands-on-opa/` — all six named cases pass. This is
both the reader's workflow and the chapter's own verification (unlike prior chapters, the
tests are not hidden — they are the point).

**Editorial verification:** internal links resolve; the canonical question/flip matches
chapters 0–2; the lab README's `opa`/`opa test`/`opa eval` commands run as written; forward
links to `05-tools`, `06-domains`, `07-capstone` present; the policy contains a visible
clause per model (RBAC/ABAC/ReBAC).

---

## 8. Out of scope for this spec

- `05-tools`, `06-domains`, `07-capstone`, `GLOSSARY.md` (separate tasks; the ending only
  points forward).
- OPA server, bundles, decision logs, HTTP API, Docker.
- Graph-based ReBAC in Rego, or live OPA↔OpenFGA integration (noted as composition, not built).
- Keycloak/identity.
- Modifying chapters 1–3.

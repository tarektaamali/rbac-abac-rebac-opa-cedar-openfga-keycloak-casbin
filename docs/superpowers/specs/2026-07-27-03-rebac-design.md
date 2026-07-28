# Design — `03-rebac/` chapter

**Date:** 2026-07-27
**Status:** Approved (design phase)
**Chapter:** `03-rebac/` — access by RELATIONSHIP, the chapter all three prior "walls" point to

---

## 1. Purpose

`03-rebac/` teaches Relationship-Based Access Control (the Google Zanzibar model): access
decided by **relationships** between users and things — *owns*, *manages*, *audits* — often
across a chain. It answers the questions RBAC and ABAC handled clumsily: *"only his **own**
account,"* *"the manager of the **branch that owns** it."*

It introduces a new tool conceptually — **OpenFGA** — but keeps the repo's zero-friction
promise: the runnable lab is a small **pure-Python** Zanzibar-style checker, paired with the
**real OpenFGA authorization model** (`model.fga`) as reference so the reader meets the
actual DSL. Running the real OpenFGA server is deferred to `05-tools/openfga/`.

**Done-criteria for the reader.** After this chapter they can:

- Explain ReBAC in one sentence: access follows **relationships** (and chains of them), not
  roles or attributes.
- Read a relationship graph and trace *why* access was granted (which path).
- Explain how **tenant isolation falls out of the graph** (no path across banks = deny).
- Explain ReBAC's limit: it sees relationships, **not context** (time/amount) — which is why
  chapter 4 unifies all three models as policy-as-code.

**Explicit non-goals (YAGNI).**

- **No Docker, no OpenFGA server, no SDK, no network.** The lab is pure-Python stdlib.
  `model.fga` is read-only reference; actually running OpenFGA is `05-tools/openfga/`.
- **No context/attribute logic** (time, amount) — that's ABAC's job; the `wall` only names
  the gap and points to `04-policy-as-code`.
- **View is the only action.** No per-action relation variety (that was considered and
  dropped).
- No web/API layer, database, or policy externalization.
- Pytest remains a dev/CI artifact, never the reader's path.

---

## 2. Decisions (locked)

| Decision | Choice |
|----------|--------|
| Engine | **Pure-Python** Zanzibar-style tuple store + checker (no deps) |
| Real tool exposure | A reference **`model.fga`** in real OpenFGA DSL, mirrored by the checker |
| Relationships (data) | OpenFGA-style tuples `(subject, relation, object)` in `tuples.csv` |
| Viewer paths | **owner** (direct) · **manager from branch** (1 hop) · **auditor from bank** (2 hops) |
| Denial | **No relationship path = deny**; cross-tenant isolation falls out of the graph |
| Check output | ALLOW/DENY **plus the granting path** (e.g. "manages branch:tunis, which owns account:123") |
| Lab shape | Mirror ch1/ch2: `ask` / `demo` / `wall` |
| `wall` points to | **`04-policy-as-code`**, framed as "ReBAC can't see context → unify all three models" |

**Running-example cast** (reused verbatim; do not rename):

- DinarBank side: **Mr. Youssef** (`user:youssef`, owner of `account:123`), **Leila**
  (`user:leila`, manager of `branch:tunis`), **Sonia** (`user:sonia`, auditor of
  `bank:dinarbank`), **Amine** (`user:amine`, a teller — deliberately has **no** viewer path
  to `account:123`, showing role ≠ relationship).
- Banque de Carthage side: **Fatma** (`user:fatma`, owner of `account:999` in
  `branch:carthage` / `bank:carthage`) — used only for the cross-tenant denial.
- Objects: `account:123`, `account:999`, `branch:tunis`, `branch:carthage`,
  `bank:dinarbank`, `bank:carthage`.

---

## 3. File structure

```
03-rebac/
├── README.md                 ← concept · when ReBAC · the limit → 04-policy-as-code
├── theory.md                 ← definition + everyday (Google Docs share) + the SafiBank graph
└── hands-on-openfga/
    ├── model.fga             ← the real OpenFGA authorization model (reference DSL)
    ├── tuples.csv            ← relationships as data (subject, relation, object)
    ├── main.py               ← pure-Python checker + ask/demo/wall CLI
    ├── test_check.py         ← dev/CI: three grant-paths + denials + CWD-independence
    └── README.md             ← how to run + what to notice + "how OpenFGA thinks"
```

No `requirements.txt` — the lab uses only the standard library. The lab README states
"no dependencies, Python 3.9+."

---

## 4. Relationships as data (`tuples.csv`)

OpenFGA-style tuples `(subject, relation, object)`. A "subject" may itself be an object
(e.g. `branch:tunis`), which is how chains are expressed.

```csv
# subject, relation, object
user:youssef, owner, account:123
branch:tunis, branch, account:123
user:leila, manager, branch:tunis
bank:dinarbank, bank, branch:tunis
user:sonia, auditor, bank:dinarbank
# Banque de Carthage — only for the cross-tenant denial
user:fatma, owner, account:999
branch:carthage, branch, account:999
bank:carthage, bank, branch:carthage
```

- Lines beginning `#` and blank lines are ignored by the loader.
- `(branch:tunis, branch, account:123)` reads "account:123's `branch` is branch:tunis."
- `(bank:dinarbank, bank, branch:tunis)` reads "branch:tunis's `bank` is bank:dinarbank."

---

## 5. The real OpenFGA model (`model.fga`) — reference

The checker mirrors this exactly; the reader sees the genuine DSL.

```
model
  schema 1.1

type user

type bank
  relations
    define auditor: [user]

type branch
  relations
    define bank: [bank]
    define manager: [user]
    define auditor: auditor from bank

type account
  relations
    define branch: [branch]
    define owner: [user]
    define viewer: owner or manager from branch or auditor from branch
```

Note: `branch`'s `auditor` is **computed** — `auditor from bank` means "a branch's auditors
are its bank's auditors." Then `account.viewer` includes `auditor from branch`, giving the
2-hop auditor path (account → branch → bank → auditor). The lab README explains this
line-by-line.

---

## 6. The checker + interfaces (`main.py`)

- `build_store(path: str | None = None) -> Store` — loads tuples from `tuples.csv` next to
  `main.py` (CWD-independent). `Store` holds the tuples and offers lookups.
- `check(store, subject, account) -> tuple[bool, str]` — evaluates the three viewer paths in
  order and returns `(allowed, reason)`:
  - **owner:** tuple `(subject, owner, account)` exists → reason `"owns account:123"`.
  - **manager from branch:** account's branch `B` (via `(B, branch, account)`) has
    `(subject, manager, B)` → reason `"manages branch:tunis, which owns account:123"`.
  - **auditor from bank:** branch `B`'s bank `K` (via `(K, bank, B)`) has
    `(subject, auditor, K)` → reason `"audits bank:dinarbank"`.
  - none → `(False, "no relationship path from <subject> to <account>")`.
- `run_demo(store) -> list[tuple]` — returns `(subject, account, allowed, reason)` rows for
  the 5 canonical scenarios (§7 table), consumed by the demo printer and the tests.

Both the CLI and `test_check.py` import these — one source of truth.

---

## 7. The three modes + canonical scenarios

- **ask** — pick a subject `[youssef, leila, sonia, amine, fatma]` and an account
  `[account:123, account:999]`; print ALLOW/DENY with the granting path.
- **demo** — prints this table (the `run_demo` oracle):

  | Subject | Account | Expected | Reason |
  |---------|---------|----------|--------|
  | youssef | account:123 | ✅ ALLOW | owns it |
  | leila | account:123 | ✅ ALLOW | manages branch:tunis, which owns it |
  | sonia | account:123 | ✅ ALLOW | audits bank:dinarbank |
  | amine | account:123 | ❌ DENY | no relationship path |
  | leila | account:999 | ❌ DENY | cross-tenant: no path into Banque de Carthage |

- **wall** — static text: ReBAC answers *"is Youssef related to this account?"* but not
  *"...and is it under 10,000 TND, during branch hours?"* Real rules need RBAC + ABAC + ReBAC
  **together**; maintaining them in-app across services doesn't scale → externalize into one
  versioned, testable engine → `04-policy-as-code`. Ends pointing at chapter 4.

---

## 8. Testing / verification

**`test_check.py`** (pytest, dev/CI only):

- Three grant-paths ALLOW, each asserting the reason substring (`owns`, `manages`, `audits`).
- Amine → account:123 → DENY (role ≠ relationship).
- Leila → account:999 → DENY (cross-tenant isolation from the graph).
- `run_demo` returns exactly the 5 rows above with expected verdicts.
- `build_store` is CWD-independent (works from any working directory).

**Editorial verification** (docs): internal links resolve; cast/objects/graph match this
spec and chapters 0–2; `model.fga` matches §5; the lab README's line-by-line explanation of
`viewer` is accurate; forward links to `04-policy-as-code` and `05-tools/openfga/` present.

---

## 9. Out of scope for this spec

- Running the real OpenFGA server (that's `05-tools/openfga/`).
- `04-policy-as-code` and later chapters (the `wall` only points forward).
- `GLOSSARY.md` (separate task).
- Any context/attribute evaluation, web/API layer, database, Docker, or SDK usage.
- Modifying `01-rbac/` or `02-abac/`.

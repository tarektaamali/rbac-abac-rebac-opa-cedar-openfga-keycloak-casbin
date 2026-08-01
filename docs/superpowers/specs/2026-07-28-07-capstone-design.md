# Design — `07-capstone/` chapter

**Date:** 2026-07-28
**Status:** Approved (design phase)
**Chapter:** `07-capstone/` — one small SafiBank app composing RBAC → ABAC → ReBAC end to end

---

## 1. Purpose

`07-capstone/` is the finale: a small, runnable SafiBank app that answers the canonical
transfer question by running **every layer** — tenant → RBAC → ABAC → ReBAC — as an ordered
pipeline, so the reader *sees which gate decides each request*. It's an **integration**, not a
new concept: it composes chapters 1–4 into one flow.

**Done-criteria for the reader.** After this chapter they can:

- Trace a transfer request through the full decision pipeline (tenant → role → attributes →
  relationship) and name which layer allowed or denied it.
- Explain why the **tenant wall comes first** (a cross-tenant request is denied before any
  other gate runs).
- See how the models composed across the repo become one `authorize()` function.

**Explicit non-goals (YAGNI).**

- **No web server, HTTP, or database** — an in-memory mock ledger; the app is a local CLI.
- **No external engines** (Casbin/OPA/OpenFGA) and **no dependencies** — pure Python stdlib.
  The point is to make the *layering* explicit, which those engines would hide inside one rule.
- **No new authorization concepts** — only the composition of chapters 1–4.
- **No "wall"/forward limit** — this is the end of the learning path.
- Transfer stays **staff-only** (teller/manager), consistent with chapters 1–4 (no
  customer/owner-transfer path).

---

## 2. Decisions (locked)

| Decision | Choice |
|----------|--------|
| App | **Pure-Python layered "transfer service"** — an ordered PDP pipeline + a PEP that executes or denies |
| Gate order | **tenant → RBAC → ABAC → ReBAC** (first failing gate decides) |
| Output | A `Decision(allow, layer, reason)` — the **`layer`** field names which gate decided |
| Experience | A **demo** (one request per gate) + an interactive **ask** mode |
| Verification | Real pytest — one test per gate asserts denial **at the right layer**, plus happy paths |
| Deps | **None** (Python 3.9+ stdlib) |

**Gate definitions (the transfer rule, staged):**

- **tenant:** `subject.tenant == account.tenant`, else DENY at `tenant`.
- **RBAC:** `subject.role in {"teller", "branch_manager"}`, else DENY at `rbac`.
- **ABAC:** `amount <= 10000 and 8 <= hour < 17`, else DENY at `abac`.
- **ReBAC:** `_related(subject, account)`, else DENY at `rebac`, where `_related` =
  (`role == "teller" and subject.branch == account.branch`) or
  (`role == "branch_manager" and subject.manages == account.branch`).
- All pass → ALLOW (`layer == "*"`).

**Running example continuity:** cast (Amine/Leila/Youssef/Fatma), TND, Tunis/Sfax branches,
DinarBank vs Banque de Carthage, canonical *8,000 TND at 22:00*.

---

## 3. File structure

```
07-capstone/
├── README.md            ← what it is · pipeline diagram · how to run · what to notice
├── authorize.py         ← models (Subject, Account, Decision) + authorize() pipeline + _related
├── app.py               ← sample data + TransferService (PEP) + run_demo + ask/demo CLI
└── test_authorize.py    ← dev/CI: each gate denies at the right layer; happy paths allow
```

No `requirements.txt`, no venv beyond pytest for dev.

---

## 4. The pipeline (`authorize.py`)

```python
from dataclasses import dataclass

@dataclass
class Subject:
    id: str
    role: str        # customer | teller | branch_manager | auditor
    branch: str      # home branch (tellers)
    manages: str     # branch a manager manages ("" otherwise)
    tenant: str      # dinarbank | carthage

@dataclass
class Account:
    id: str
    branch: str
    owner: str
    tenant: str

@dataclass
class Decision:
    allow: bool
    layer: str       # "tenant" | "rbac" | "abac" | "rebac" | "*"
    reason: str


def _related(subject, account):
    if subject.role == "teller":
        return subject.branch == account.branch
    if subject.role == "branch_manager":
        return subject.manages == account.branch
    return False


def authorize(subject, account, amount, hour) -> Decision:
    # 1. TENANT — the wall comes first.
    if subject.tenant != account.tenant:
        return Decision(False, "tenant",
                        f"cross-tenant: {subject.tenant} != {account.tenant}")
    # 2. RBAC — may this role transfer at all?
    if subject.role not in ("teller", "branch_manager"):
        return Decision(False, "rbac", f"role {subject.role} may not transfer")
    # 3. ABAC — amount & branch hours.
    if amount > 10000:
        return Decision(False, "abac", f"over the 10,000 TND limit ({amount})")
    if not (8 <= hour < 17):
        return Decision(False, "abac", f"after branch hours ({hour:02d}:00)")
    # 4. ReBAC — related to the account's branch?
    if not _related(subject, account):
        return Decision(False, "rebac", f"not related to branch {account.branch}")
    return Decision(True, "*", "all gates passed")
```

The **ordering is load-bearing**: a cross-tenant request is denied at `tenant` even though it
would also fail `rebac`. That's the teaching point — check the wall first.

## 5. The app (`app.py`)

- Sample data: Subjects `amine` (teller, Tunis, DinarBank), `leila` (branch_manager,
  manages Tunis, DinarBank), `youssef` (customer, Tunis, DinarBank), `fatma` (customer,
  Carthage, Banque de Carthage). Accounts `acc:123` (Tunis, DinarBank), `acc:456` (Sfax,
  DinarBank), `acc:999` (Carthage, Banque de Carthage).
- `TransferService.transfer(subject_id, account_id, amount, hour) -> str` — the **PEP**:
  builds the request, calls `authorize`, and either records a mock ledger move ("executed")
  or returns the denial with its layer + reason.
- `run_demo() -> list[tuple]` — returns `(subject_id, account_id, amount, hour, decision)`
  rows for the canonical scenarios (§6); consumed by the demo printer and tests.
- Guided **ask** mode (pick subject / account / amount / hour) + **demo** mode. No "wall".

## 6. Canonical scenarios (demo + test oracle)

One request per gate, chosen so each layer stops exactly one:

| Subject | Account | Amount | Hour | Expected | Decided at |
|---------|---------|--------|------|----------|-----------|
| amine | acc:123 | 8000 | 9 | ✅ ALLOW | * |
| amine | acc:123 | 8000 | 22 | ❌ DENY | abac (after hours) |
| amine | acc:123 | 12000 | 9 | ❌ DENY | abac (over limit) |
| amine | acc:999 | 8000 | 9 | ❌ DENY | tenant (cross-tenant) |
| youssef | acc:123 | 8000 | 9 | ❌ DENY | rbac (customer) |
| amine | acc:456 | 8000 | 9 | ❌ DENY | rebac (Sfax ≠ Tunis) |
| leila | acc:123 | 8000 | 9 | ✅ ALLOW | * |

## 7. Testing / verification

**`test_authorize.py`** (pytest, dev/CI):

- One test per gate asserting both `decision.allow` and `decision.layer` (e.g. the
  cross-tenant case → `allow is False and layer == "tenant"`).
- The ordering test: `amine → acc:999` (which fails both tenant and rebac) stops at
  `tenant`, proving gate order.
- Happy paths: `amine → acc:123 @09:00` and `leila → acc:123 @09:00` → allow (`layer == "*"`).
- `run_demo` returns the 7 rows above with the expected verdict + layer.

**Editorial:** README links resolve (back to chapters 1–4); cast/thresholds match chapters
0–4; the pipeline diagram matches the gate order in `authorize.py`.

## 8. Out of scope for this spec

- `GLOSSARY.md` (separate task).
- Any web/API/database, external engine, or dependency.
- New authorization concepts (only composition).
- Modifying chapters 0–6.

# Design — `05-tools/` chapter

**Date:** 2026-07-28
**Status:** Approved (design phase)
**Chapter:** `05-tools/` — one reference card per tool; the "which tool do I reach for?" chapter

---

## 1. Purpose

`05-tools/` is the **reference layer**, not part of the RBAC→ABAC→ReBAC→policy-as-code model
arc. It answers a judgment question the model chapters raised but didn't fully resolve:
*given my rule, which tool?* One folder per tool, each a card following one shared template,
plus an index with a comparison table. It teaches **choosing**, and cross-links to the
runnable labs already built in chapters 1–4 rather than re-teaching them.

**Done-criteria for the reader.** After this chapter they can:

- Name what each tool (Casbin, OPA, Cedar, OpenFGA, Keycloak) is best at and where it runs.
- Pick the right tool for a rule (role → Casbin/Keycloak; attributes → OPA/Cedar;
  relationships → OpenFGA; identity/SSO → Keycloak; externalized policy → OPA/Cedar).
- Explain that the tools **compose** (Keycloak for identity feeds OPA/OpenFGA), not compete.

**Explicit non-goals (YAGNI).**

- **No new runnable labs.** Casbin/OPA/OpenFGA cards link back to chapters 1–4; Cedar and
  Keycloak cards stay illustrative (a policy snippet, not a runnable lab).
- **No "wall"/forward-limit** — this is a reference chapter, not a model step.
- No re-teaching of the models themselves (that's chapters 1–4).
- No `06-domains`/`07-capstone` content.
- No Docker, servers, or code execution — verification is editorial.

---

## 2. Decisions (locked)

| Decision | Choice |
|----------|--------|
| Content type | **Pure reference cards**, cross-linked to the existing labs |
| Structure | **One folder per tool**, each with a `README.md`, plus a top-level index `README.md` |
| Template | **One shared 8-section skeleton** for every card (below) |
| Cedar | Card carries an **illustrative Cedar `permit(...)` policy** for the SafiBank transfer (Cedar is the only tool with no lab) |
| Keycloak | **`git mv keycloak-README.md 05-tools/keycloak/README.md`**, adapted to the template; root `README.md` reference updated |
| Verification | **Editorial** (links resolve, every card has all sections, ratings consistent) |

**The shared 8-section template** (identical order in every tool card):

1. **One-line takeaway** — the mental model.
2. **What it is** — and *where it runs* (in-process library / server / language / platform).
3. **Which models** — RBAC / ABAC / ReBAC / policy-as-code, each rated ✅ great · ⚠️ possible · ❌ no.
4. **When to reach for it** / **When NOT**.
5. **A tiny illustrative snippet** — the shape of its policy/config.
6. **SafiBank angle** — how it fits the canonical transfer question.
7. **Strengths / limits.**
8. **See also** — the hands-on chapter (if any) + one trusted docs link.

**Running example continuity:** SafiBank Cloud, the canonical transfer question, cast
(Amine/Leila/Youssef/Sonia), TND, branches — used in every card's "SafiBank angle."

---

## 3. File structure

```
05-tools/
├── README.md              ← index: comparison table + "which tool for which model" → DECISION-TREE.md
├── casbin/README.md       ← card; links to 01-rbac, 02-abac
├── opa/README.md          ← card; links to 04-policy-as-code
├── cedar/README.md        ← card; illustrative Cedar permit(...) snippet (no lab)
├── openfga/README.md      ← card; links to 03-rebac
└── keycloak/README.md     ← the adapted existing draft
```

Also modified: `keycloak-README.md` is **moved** (git mv) to `05-tools/keycloak/README.md`;
the root `README.md`'s status line / any link to the old path is updated.

---

## 4. The index (`05-tools/README.md`)

A comparison table the reader can scan in one look:

| Tool | Where it runs | RBAC | ABAC | ReBAC | Policy-as-code | Best at | Lab in this repo |
|------|---------------|------|------|-------|----------------|---------|------------------|
| **Casbin** | in-process library | ✅ | ✅ | ⚠️ | ⚠️ | lightweight in-app authz | `01-rbac`, `02-abac` |
| **OPA** | server / CLI / sidecar | ✅ | ✅ | ⚠️ | ✅ | general policy engine, K8s, microservices | `04-policy-as-code` |
| **Cedar** | library / language | ✅ | ✅ | ⚠️ | ✅ | ergonomic, analyzable policies | — (illustrative) |
| **OpenFGA** | server (Zanzibar) | ⚠️ | ❌ | ✅ | ⚠️ | relationships, sharing, hierarchy | `03-rebac` |
| **Keycloak** | identity platform | ✅ | ⚠️ | ❌ | ❌ | identity, SSO, broad roles | — (reference) |

Plus a short paragraph: start at [`DECISION-TREE.md`](../DECISION-TREE.md) to go from *"what
does my rule depend on?"* to the tool; these cards are the per-tool detail. Note that the
ratings in each card must match this table.

---

## 5. Per-tool card contents

Each follows the §2 template. Key specifics:

- **casbin** — in-process library for Go/Python/Node; RBAC ✅ ABAC ✅ (model.conf + policy.csv
  as data), ReBAC ⚠️, policy-as-code ⚠️ (rules are data but engine is in-app). Snippet: a
  `policy.csv` line. See also → `01-rbac`, `02-abac`, casbin.org.
- **opa** — general-purpose policy engine + Rego; server/CLI/sidecar; strong for
  Kubernetes (Gatekeeper) and microservices; policy-as-code ✅. Snippet: a Rego `allow if`.
  See also → `04-policy-as-code`, openpolicyagent.org.
- **cedar** — AWS's authorization language; small, **analyzable** (provable) policies;
  RBAC+ABAC ✅, policy-as-code ✅. **Illustrative snippet: a real Cedar `permit(...)` for the
  SafiBank transfer** (principal/action/resource + `when { … }` conditions), since Cedar has
  no lab. See also → cedarpolicy.com. Note it's conceptually close to OPA (choose Cedar for
  analyzability/typed schema, OPA for ecosystem/K8s).
- **openfga** — open-source Google Zanzibar; server; ReBAC ✅, the rest ⚠️/❌. Snippet: a
  `model.fga` `define viewer: …` relation. See also → `03-rebac`, openfga.dev.
- **keycloak** — identity platform (IAM); RBAC ✅, ABAC ⚠️, ReBAC ❌, policy-as-code ❌; its
  centerpiece is the "**Keycloak feeds OPA/OpenFGA**" composition pattern. Adapted from the
  existing draft; fix its "see also" paths, align to the 8-section skeleton, keep the mermaid
  composition diagram. See also → `01-rbac`, keycloak.org authorization docs.

---

## 6. Testing / verification

Editorial (no code):

- Every tool card contains all 8 template sections, in order.
- Model ratings in each card match the index comparison table exactly (no drift).
- All internal links resolve: each card → its lab chapter (`01`/`02`/`03`/`04` where
  applicable) and → the index; index → `DECISION-TREE.md`; keycloak card's updated see-also
  paths (now `../../01-rbac/` style from inside `05-tools/keycloak/`).
- `keycloak-README.md` no longer exists at the repo root; `05-tools/keycloak/README.md`
  exists; the root `README.md` no longer points at the old path.
- Cedar card contains a syntactically plausible `permit(` block.
- Cast/tool facts consistent with chapters 0–4 and `DECISION-TREE.md`.

---

## 7. Out of scope for this spec

- `06-domains`, `07-capstone`, `GLOSSARY.md` (separate tasks).
- Any runnable Cedar/Keycloak lab (Docker, CLI execution).
- Re-teaching the models or duplicating the chapter 1–4 labs.
- Modifying chapters 1–4's content (only cross-links point at them).

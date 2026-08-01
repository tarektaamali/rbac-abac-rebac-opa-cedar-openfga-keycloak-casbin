# Design — `06-domains/` chapter

**Date:** 2026-07-28
**Status:** Approved (design phase)
**Chapter:** `06-domains/` — WHERE you enforce; the "location & pattern" reference layer

---

## 1. Purpose

`06-domains/` teaches **where** authorization is enforced — not a new model, just the place
the PEP sits and the pattern it follows in each context: **APIs**, **multi-tenant SaaS**,
**Kubernetes**, and **cloud-native (service mesh)**. It's the sibling of `05-tools/`: same
card-per-topic shape, but the axis is *location*, not *tool*. It reinforces that the PEP/PDP
split from `00-foundations` is constant — only the enforcement point moves.

**Done-criteria for the reader.** After this chapter they can:

- Name where the PEP sits in each domain (middleware/gateway, tenant guard, admission
  controller, sidecar).
- Explain the SaaS rule: **check the tenant boundary first**, before role/attribute/relationship.
- Distinguish **request-time** authorization (APIs, mesh) from **deploy-time** policy
  (Kubernetes admission control).
- Point each domain at the tools that fit (via `05-tools`).

**Explicit non-goals (YAGNI).**

- **No runnable labs** — no cluster (kind/minikube), no mesh, no Docker. Snippets are
  **illustrative**, not executed.
- **No new models or tools** — cross-links to chapters 1–5; does not re-teach them.
- **No "wall"/forward limit** — reference chapter.
- No `07-capstone`/`GLOSSARY.md` content.

---

## 2. Decisions (locked)

| Decision | Choice |
|----------|--------|
| Content type | **Reference/pattern cards**, one folder per domain, + an index — mirrors `05-tools` |
| Template | **One shared 8-section skeleton** for every card (below) |
| Snippets | **Illustrative, not runnable** (middleware pseudocode, Gatekeeper `ConstraintTemplate`, Envoy `ext_authz` sketch) |
| SaaS card | Carries the **tenant-boundary-first** emphasis (foundations' first-class idea) |
| Verification | **Editorial** (sections present, links resolve, tools links → `05-tools`) |

**The shared 8-section template** (identical order in every card):

1. **One-line takeaway** — where the PEP sits here.
2. **The enforcement point** — where in the request/deploy path the check happens.
3. **The pattern** — how it works.
4. **Illustrative snippet** — the shape (not runnable).
5. **SafiBank angle** — the canonical example in this context.
6. **Pitfalls** — the classic mistake here.
7. **Which tools fit here** — links into `05-tools`.
8. **See also** — relevant chapters + one docs/reference link.

**Running example continuity:** SafiBank Cloud, the canonical transfer question, cast, TND,
DinarBank vs Banque de Carthage — in each card's SafiBank angle.

---

## 3. File structure

```
06-domains/
├── README.md                 ← index: "WHERE not WHAT" + locations table → 05-tools, DECISION-TREE
├── apis/README.md            ← middleware / API gateway; check every request
├── saas/README.md            ← multi-tenant: tenant boundary FIRST
├── kubernetes/README.md      ← OPA Gatekeeper admission control (deploy-time)
└── cloud-native/README.md    ← sidecar / service mesh (Envoy ext_authz → OPA)
```

---

## 4. The index (`06-domains/README.md`)

Framing: these are **locations** for the same PEP/PDP split from `00-foundations`, not new
models. Plus a table:

| Domain | Where the PEP sits | When it runs | Typical tool | SafiBank example |
|--------|--------------------|--------------|--------------|------------------|
| **APIs** | middleware / API gateway | every request | any PDP (Casbin, OPA, OpenFGA) | the transfer endpoint asks before moving money |
| **SaaS** | tenant guard (before everything) | every request | any + tenant scoping | Amine (DinarBank) can't touch a Carthage account |
| **Kubernetes** | admission controller | deploy time | OPA Gatekeeper | reject SafiBank pods missing a tenant label |
| **Cloud-native** | sidecar / service mesh | every service call | OPA + Envoy/Istio | service-to-service calls checked at the sidecar |

Cross-links: [`05-tools`](../05-tools/) for the engines, [`DECISION-TREE.md`](../DECISION-TREE.md)
for model/tool choice.

---

## 5. Per-domain card contents

Each follows the §2 template. Specifics:

- **apis** — PEP = middleware or API gateway; authz on **every** request; centralize (one
  guard, not scattered `if`s), **fail closed**. Snippet: middleware pseudocode calling the
  PDP before the handler. Pitfall: forgotten/scattered checks; failing open. See also →
  `00-foundations` (PEP/PDP), `04-policy-as-code`.

- **saas** — the **tenant-boundary** card. Rule: check `request.tenant == resource.tenant`
  **first**, before role/attribute/relationship; plus DB row-level security as
  defense-in-depth. Snippet: a guard that denies cross-tenant before any other check.
  Pitfall: a tenant leak is a breach, not a bug; don't rely on app checks alone. See also →
  `00-foundations` (tenant/multi-tenant), `03-rebac` (isolation falls out of the graph).

- **kubernetes** — PEP = admission controller (**OPA Gatekeeper**); **deploy-time** policy on
  which workloads/configs are allowed (distinct from request-time authz). Snippet: a small
  Gatekeeper `ConstraintTemplate` (embedding Rego) + a `Constraint`. SafiBank angle:
  guardrails like "every SafiBank pod must carry a `tenant` label." Pitfall: admission ≠
  request-time authorization — don't conflate them. See also → `04-policy-as-code`,
  `05-tools/opa`.

- **cloud-native** — PEP = **sidecar / service mesh**; offload authz into the mesh (Envoy
  `ext_authz` → OPA, or Istio `AuthorizationPolicy`), using mTLS identity. Snippet: an Envoy
  `ext_authz` config sketch pointing at an OPA sidecar. SafiBank: every service-to-service
  call checked at the sidecar. Pitfall: fail-open vs fail-closed, added latency, trusting
  mesh identity. See also → `04-policy-as-code`, `05-tools/opa`.

---

## 6. Testing / verification

Editorial (no code):

- Every domain card contains all 8 template sections, in order.
- All internal links resolve: each card → `05-tools` (and its specific tool where named) and
  relevant chapters (`00`/`03`/`04`); index → `05-tools` + `DECISION-TREE.md`.
- The SaaS card explicitly states the tenant check comes **first**.
- The Kubernetes card explicitly distinguishes **deploy-time admission** from request-time authz.
- Snippets are present and plausible (a `ConstraintTemplate` block in kubernetes; an
  `ext_authz` reference in cloud-native).
- Cast/tool facts consistent with chapters 0–5 and `DECISION-TREE.md`.

---

## 7. Out of scope for this spec

- `07-capstone`, `GLOSSARY.md` (separate tasks).
- Any runnable cluster/mesh/Docker setup or executed snippet.
- Re-teaching models or tools (only cross-links).
- Modifying chapters 0–5's content.

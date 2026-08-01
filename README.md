# rbac-abac-rebac-opa-cedar-openfga-keycloak-casbin

> A hands-on, beginner-friendly journey through **modern authorization** — from simple roles to
> fine-grained, relationship-aware, policy-as-code systems.
> Learn **RBAC → ABAC → ReBAC → Policy-as-Code** with **Keycloak, Casbin, OPA, Cedar, and OpenFGA**,
> one runnable step at a time.

*(Yes, the name lists every keyword on purpose — it's searchable. The docs below carry the meaning.)*

---

## 🎯 What this repo is

A structured learning path that answers the single hardest question in modern systems:

> **Can this person do this action on this thing, right now?**

Instead of scattered theory, everything is taught with **ONE running example** —
**SafiBank Cloud**, an imaginary SaaS banking platform used by Tunisian banks — so no concept ever
feels abstract. You'll watch the same rule that simple roles *can't* express become easy once you
add attributes, then relationships, then externalize it as policy-as-code.

**Who it's for:** developers, architects, DevOps, and security engineers who want to move from
`if user.role == "admin"` to a real, production-shaped authorization system.

---

## 🏦 The running example — SafiBank Cloud

One piece of software, used by two banks (**DinarBank**, **Banque de Carthage**) — each a separate
**tenant**. Cast of characters used throughout:

| Who | Role | Does |
|-----|------|------|
| Mr. Youssef | `customer` | Owns an account at the Tunis branch |
| Amine | `teller` | Daily operations at one branch |
| Leila | `branch_manager` | Approves bigger operations |
| Sonia | `auditor` | Read-only compliance checks |

Recurring test question: *"Can teller **Amine** transfer **8,000 TND** from **Mr. Youssef's account**
at **22:00**?"* — answered better in each chapter.

---

## 🗺️ Learning path (follow in order)

1. **`00-foundations/`** — authN vs authZ, the PEP/PDP split, why authorization is hard.
2. **`01-rbac/`** — access by **role**. Run the Casbin lab, then *feel* it break (role explosion).
3. **`02-abac/`** — access by **attributes** (time, amount, branch). Power + new complexity.
4. **`03-rebac/`** — access by **relationship** (owns / member-of / shared). The Zanzibar model.
5. **`04-policy-as-code/`** — pull rules OUT of the app into a versioned, testable engine.
6. **`05-tools/`** — one reference per tool: when to reach for each.
7. **`06-domains/`** — WHERE you enforce (APIs, SaaS, Kubernetes, cloud-native).
8. **`07-capstone/`** — one small SafiBank app using RBAC → ABAC → ReBAC end to end.

> ✅ **Golden rule:** finish `00-foundations` + `01-rbac` *completely* (with the runnable lab)
> before touching anything else. Two solid chapters beat twenty empty folders.

---

## 🌳 Not sure which model/tool to use?

Start with **[`DECISION-TREE.md`](./DECISION-TREE.md)** — a visual map that takes you from
*"what does my rule depend on?"* to the exact model and tool, with worked examples across banking,
document collaboration, healthcare, e-commerce, Kubernetes, and e-government.

The one-paragraph version:

> Start with **RBAC** (roles). The moment a rule needs **time, amount, location, or status**, add
> **ABAC**. The moment it needs **ownership, sharing, or hierarchy**, add **ReBAC**. Once these rules
> span services or must be audited, **externalize them as policy-as-code**. If you're multi-tenant,
> **check the tenant boundary before anything else.** Use **Keycloak** for identity, **OPA/Cedar** for
> policy, **OpenFGA** for relationships — together, not in competition.

---

## 📁 Repo structure

```
.
├── README.md                 ← you are here
├── DECISION-TREE.md          ← the map: which model + tool to pick
├── GLOSSARY.md               ← every term with a SafiBank example
├── 00-foundations/
├── 01-rbac/          (hands-on-casbin/)
├── 02-abac/          (hands-on-casbin/)
├── 03-rebac/         (hands-on-openfga/)
├── 04-policy-as-code/(hands-on-opa/)
├── 05-tools/         (casbin/ opa/ cedar/ openfga/ keycloak/)
├── 06-domains/       (apis/ saas/ kubernetes/ cloud-native/)
├── 07-capstone/
├── comparisons/
├── decisions/        ← ADRs: "we chose X because Y"
└── resources.md
```

---

## 🧰 Tools covered

| Tool | Best at | Model |
|------|---------|-------|
| **Keycloak** | Identity, SSO, broad roles | RBAC (+ limited ABAC) |
| **Casbin** | Lightweight in-app authz | RBAC / ABAC |
| **OPA** (Rego) | General policy engine, Kubernetes | ABAC / Policy-as-Code |
| **Cedar** | Ergonomic, analyzable policies | RBAC / ABAC |
| **OpenFGA** | Relationships, sharing, hierarchy | ReBAC (Zanzibar) |

---

## 🚦 Status

Work in progress — building it chapter by chapter.

- [x] Blueprint & glossary
- [x] Decision tree
- [x] Keycloak tool reference
- [ ] `01-rbac` runnable Casbin lab
- [ ] `02-abac` → `07-capstone`

---

## 📚 Trusted references

- OpenFGA docs — https://openfga.dev/docs
- Open Policy Agent docs — https://www.openpolicyagent.org/docs
- AWS Cedar — https://www.cedarpolicy.com
- Keycloak Authorization Services — https://www.keycloak.org/docs/latest/authorization_services
- Casbin — https://casbin.org/docs/overview

---

## 📝 License

MIT — learn freely, reuse freely.

---

## 🤖 Built with

This work was realized with **[Claude Code](https://claude.com/claude-code)** — designed,
planned, and built chapter by chapter (spec → plan → test-driven implementation → review).

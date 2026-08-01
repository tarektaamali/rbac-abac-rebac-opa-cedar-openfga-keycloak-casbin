# 05 · Tools — which one do I reach for?

> You've met the models (RBAC → ABAC → ReBAC → policy-as-code). Now: **given a rule, which
> tool?** One card per tool, all on the same template, so you can compare them at a glance.

Start with **[`DECISION-TREE.md`](../DECISION-TREE.md)** to go from *"what does my rule depend
on?"* to a model + tool. These cards are the per-tool detail behind that map.

## At a glance

| Tool | Where it runs | RBAC | ABAC | ReBAC | Policy-as-code | Best at | Lab here |
|------|---------------|:----:|:----:|:-----:|:--------------:|---------|----------|
| [Casbin](./casbin/) | in-process library | ✅ | ✅ | ⚠️ | ⚠️ | lightweight in-app authz | [01](../01-rbac/), [02](../02-abac/) |
| [OPA](./opa/) | server / CLI / sidecar | ✅ | ✅ | ⚠️ | ✅ | general policy engine, K8s, microservices | [04](../04-policy-as-code/) |
| [Cedar](./cedar/) | library / language | ✅ | ✅ | ⚠️ | ✅ | ergonomic, **analyzable** policies | — |
| [OpenFGA](./openfga/) | server (Zanzibar) | ⚠️ | ❌ | ✅ | ⚠️ | relationships, sharing, hierarchy | [03](../03-rebac/) |
| [Keycloak](./keycloak/) | identity platform | ✅ | ⚠️ | ❌ | ❌ | identity, SSO, broad roles | — |

Legend: ✅ great · ⚠️ possible / awkward · ❌ not really.

## The one-paragraph guide

Start with **RBAC** (Casbin or Keycloak roles). The moment a rule needs **time, amount, or
status**, add **ABAC** (OPA or Cedar). The moment it needs **ownership, sharing, or
hierarchy**, add **ReBAC** (OpenFGA). Once rules span services or must be audited,
**externalize** them as policy-as-code (OPA or Cedar). Use **Keycloak** for identity and
broad roles, and let it *feed* the others — they compose, they don't compete.

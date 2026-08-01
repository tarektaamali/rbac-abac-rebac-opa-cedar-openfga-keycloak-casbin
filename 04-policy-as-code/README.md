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

# OPA (Open Policy Agent) — tool reference

> **A general-purpose policy engine with its own language, Rego.** The go-to for
> policy-as-code across microservices and Kubernetes.

## What it is
A standalone **policy engine** (single Go binary) that evaluates **Rego** policies. Runs as a
server, a sidecar, or a CLI (`opa test`, `opa eval`). **Where it runs:** external to your app
(one PDP, many PEPs).

## Which models
| RBAC | ABAC | ReBAC | Policy-as-code |
|:----:|:----:|:-----:|:--------------:|
| ✅ great | ✅ great | ⚠️ possible (via input data) | ✅ great |

## When to reach for it
- The **same rule** must be enforced by several services without drifting.
- You want rules **versioned in Git and tested** (`opa test`).
- Kubernetes admission control (OPA Gatekeeper) or microservice authorization.

## When NOT
- A single in-process service with simple roles → **Casbin** is lighter.
- Deep relationship graphs → **OpenFGA** (feed the answer to OPA as input).

## Illustrative snippet
```rego
package safibank.transfer
default allow := false
allow if {
    input.subject.role == "teller"
    input.amount <= 10000
    input.hour >= 8; input.hour < 17
}
```

## SafiBank angle
Chapter 4 writes the SafiBank transfer rule in Rego and unifies RBAC + ABAC + ReBAC in one
tested policy — the canonical *8,000 TND at 22:00* is denied by an engine outside the app.

## Strengths / limits
- **+** language-agnostic, testable, versioned; huge ecosystem (K8s, Envoy, Terraform).
- **−** Rego has a learning curve; relationship graphs aren't native (pass them as input).

## See also
- Lab: [`04-policy-as-code`](../../04-policy-as-code/) · Index: [`05-tools`](../)
- Docs: https://www.openpolicyagent.org/docs

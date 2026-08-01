# Kubernetes — where you enforce

> **The PEP is an admission controller** — OPA Gatekeeper — that vets resources **at deploy
> time**. This governs *which workloads are allowed*, not who can move money.

## The enforcement point
The Kubernetes API server calls an **admission webhook** (Gatekeeper) before a resource is
created/updated. It's **deploy-time**, not request-time — a different flavor of authorization
from the API/mesh cards.

## The pattern
Write policy as a Gatekeeper **`ConstraintTemplate`** (Rego inside) that defines a rule, then
a **`Constraint`** that applies it to specific resource kinds. Non-compliant resources are
rejected before they ever run.

## Illustrative snippet
```yaml
# ConstraintTemplate: every SafiBank pod must carry a `tenant` label
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequiredtenantlabel
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredTenantLabel
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredtenantlabel
        violation[{"msg": msg}] {
          not input.review.object.metadata.labels.tenant
          msg := "every SafiBank pod must carry a 'tenant' label"
        }
---
# Constraint: apply it to Pods
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredTenantLabel
metadata:
  name: pods-must-have-tenant
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
```

## SafiBank angle
Platform guardrails for the SafiBank deployment: every pod must declare its `tenant`, no
privileged containers, images only from the approved registry. This protects the *platform*
that runs the banking app — complementary to the request-time transfer rule.

## Pitfalls
- **Admission ≠ request-time authz** — Gatekeeper decides what can be deployed, not whether
  Amine can transfer. Don't conflate the two.
- **Audit vs enforce** — run new constraints in dry-run/audit first; a bad enforce blocks deploys.

## Which tools fit here
[`OPA`](../../05-tools/opa/) via **Gatekeeper** is the standard. Same Rego you met in chapter 4,
applied to the cluster. See [`05-tools`](../../05-tools/).

## See also
- [`04-policy-as-code`](../../04-policy-as-code/) — the Rego/OPA foundations Gatekeeper builds on.
- [`05-tools/opa`](../../05-tools/opa/) — the engine reference.

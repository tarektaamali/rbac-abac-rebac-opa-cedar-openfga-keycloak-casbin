# Cloud-native (service mesh) — where you enforce

> **The PEP moves into the sidecar.** A service mesh (Envoy / Istio) checks every
> service-to-service call *outside* your app code, delegating the decision to OPA.

## The enforcement point
Each service gets a sidecar proxy (Envoy). The proxy's **`ext_authz`** filter calls an
authorization service (OPA) on every inbound request, before traffic reaches the app. Identity
comes from the mesh's **mTLS**, so services prove who they are cryptographically.

## The pattern
Offload authorization from every service into the mesh: one consistent check, enforced by
infrastructure, using workload identity — and **fail closed** if the authorizer is down.

## Illustrative snippet
```yaml
# Envoy: delegate authz to an OPA sidecar via ext_authz
http_filters:
  - name: envoy.filters.http.ext_authz
    typed_config:
      "@type": type.googleapis.com/envoy.extensions.filters.http.ext_authz.v3.ExtAuthz
      grpc_service:
        envoy_grpc:
          cluster_name: opa        # OPA sidecar decides allow / deny
      failure_mode_allow: false     # FAIL CLOSED if OPA is unreachable
```

## SafiBank angle
When the SafiBank `transfer-service` calls the `ledger-service`, the call is authorized at the
sidecar using the caller's mTLS identity — no authorization code in either service. The mesh
enforces it uniformly across the fleet.

## Pitfalls
- **Fail-open by default** — set `failure_mode_allow: false`; a dead authorizer must deny, not allow.
- **Latency** — every hop adds an authz round-trip; cache and keep policies fast.
- **Trusting spoofable identity** — rely on mTLS workload identity, not headers a caller can set.

## Which tools fit here
[`OPA`](../../05-tools/opa/) behind Envoy `ext_authz` (or Istio `AuthorizationPolicy`) is the
common combo. See [`05-tools`](../../05-tools/).

## See also
- [`04-policy-as-code`](../../04-policy-as-code/) — the OPA policy the sidecar consults.
- [`05-tools/opa`](../../05-tools/opa/) — the engine reference.

# 06 · Domains — WHERE you enforce

> Not a new idea — just a **location**. The PEP/PDP split from
> [`00-foundations`](../00-foundations/) never changes: your app **asks**, an engine
> **decides**. What changes here is *where the guard sits*.

One card per place you'll actually put authorization, all on the same template — so you can
see the pattern, the SafiBank example, and the classic mistake at a glance.

## Where the guard sits

| Domain | Where the PEP sits | When it runs | Typical tool | SafiBank example |
|--------|--------------------|--------------|--------------|------------------|
| [APIs](./apis/) | middleware / API gateway | every request | any PDP (Casbin, OPA, OpenFGA) | the transfer endpoint asks before moving money |
| [SaaS](./saas/) | tenant guard (before everything) | every request | any + tenant scoping | Amine (DinarBank) can't touch a Carthage account |
| [Kubernetes](./kubernetes/) | admission controller | **deploy time** | OPA Gatekeeper | reject SafiBank pods missing a `tenant` label |
| [Cloud-native](./cloud-native/) | sidecar / service mesh | every service call | OPA + Envoy / Istio | service-to-service calls checked at the sidecar |

## How to read this chapter

Pick the engine in **[`05-tools`](../05-tools/)**; pick the model in
**[`DECISION-TREE.md`](../DECISION-TREE.md)**; this chapter tells you *where to plug it in*.
Note the one row that's different: **Kubernetes admission control runs at deploy time** (which
workloads are allowed), not on each user request — a distinct flavor from the others.

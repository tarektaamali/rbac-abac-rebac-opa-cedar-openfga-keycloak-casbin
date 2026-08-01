# Multi-tenant SaaS — where you enforce

> **The tenant wall is the FIRST check** — before role, attribute, or relationship. One
> codebase serves many customers; keeping their data apart is job zero.

## The enforcement point
At the very top of the request guard, before any other authorization: confirm the caller's
tenant matches the resource's tenant. Then — and only then — evaluate the actual rule.

## The pattern
**Tenant-first, defense-in-depth.** Check `request.tenant == resource.tenant` in the app,
*and* scope every database query by tenant (row-level security), so a bug in one layer can't
leak across the wall.

## Illustrative snippet
```python
# Check the tenant wall FIRST — before role, attribute, or relationship.
def authorize(request, resource):
    if request.tenant != resource.tenant:
        raise Forbidden("cross-tenant access")  # a leak here is a BREACH, not a bug
    # ...only now check role / attributes / relationships...
    return pdp.check(request, resource)
```

## SafiBank angle
SafiBank Cloud serves **DinarBank** and **Banque de Carthage** from one codebase and one
database. Amine (DinarBank) must **never** touch a Banque de Carthage account — even to read
it. The tenant check denies that before the transfer rule ever runs.

## Pitfalls
- **A tenant leak is a breach, not a bug** — treat cross-tenant access as a security incident.
- **App-only checks** — also enforce at the database (row-level security); don't trust one layer.
- **Tenant from client input** — derive it from the verified identity, never a request field.

## Which tools fit here
Every engine needs tenant scoping. [`OpenFGA`](../../05-tools/openfga/) gives isolation "for
free" (no relationship path across tenants = deny); with [`OPA`](../../05-tools/opa/) /
[`Cedar`](../../05-tools/cedar/) you pass the tenant as input. See [`05-tools`](../../05-tools/).

## See also
- [`00-foundations`](../../00-foundations/) — tenant / multi-tenant as a first-class idea.
- [`03-rebac`](../../03-rebac/) — how tenant isolation falls out of the relationship graph.

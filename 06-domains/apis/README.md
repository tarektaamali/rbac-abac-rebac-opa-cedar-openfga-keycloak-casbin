# APIs — where you enforce

> **The PEP is one guard on every request** — in middleware or at the API gateway — that
> asks the PDP before the handler runs.

## The enforcement point
On the request path, *before* business logic: an authorization middleware (or a policy check
at the API gateway). Every state-changing endpoint goes through it.

## The pattern
Centralize the check in **one** place, not scattered `if user.role == …` across handlers.
The guard builds the question (subject, action, resource, context), asks the PDP, and
**fails closed** — deny unless explicitly allowed.

## Illustrative snippet
```python
# One guard on every request — the PEP. Fails CLOSED.
def authorize(request):
    decision = pdp.check(
        subject=request.user,
        action=request.action,
        resource=request.resource,
        context=request.context,
    )
    if not decision.allow:
        raise Forbidden(decision.reason)  # deny by default; never fall through to "allow"
```

## SafiBank angle
The `POST /transfer` endpoint calls `authorize()` before moving a millime. That's the same
canonical question — *"can Amine transfer 8,000 TND at 22:00?"* — asked at the API edge.

## Pitfalls
- **Scattered checks** — one forgotten handler is a hole. Centralize.
- **Failing open** — if the PDP is unreachable, deny (don't allow). Security must fail closed.
- **Trusting client input** for identity — read it from the verified token, not the request body.

## Which tools fit here
Any PDP: [`Casbin`](../../05-tools/casbin/) in-process, [`OPA`](../../05-tools/opa/) /
[`Cedar`](../../05-tools/cedar/) external, [`OpenFGA`](../../05-tools/openfga/) for
relationship checks. See [`05-tools`](../../05-tools/).

## See also
- [`00-foundations`](../../00-foundations/) — the PEP/PDP split this implements.
- [`04-policy-as-code`](../../04-policy-as-code/) — externalizing the decision the middleware asks.

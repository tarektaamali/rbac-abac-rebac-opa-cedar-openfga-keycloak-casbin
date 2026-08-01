# Policy-as-code — the theory

## Definition (simple)

**Policy-as-code**: authorization rules are written as **code** — versioned in Git, **tested**,
and enforced by an **external engine** — instead of `if` statements scattered through the
app. The app (a **PEP**) asks; the engine (a **PDP**) decides.

## Everyday example

One **rulebook**, many **security guards**. Instead of every guard memorising the rules (and
each remembering them slightly differently), there's a single written rulebook they all
consult. Update the rulebook once, and every guard is instantly up to date.

## Why banking especially needs it

Auditors and regulators ask: *"prove who could access this account, and why."* If the rule
is one reviewed file in Git — tested, with a full history of who changed what — you can
answer instantly. If it's `if` statements spread across a mobile app, a web app, and an ATM
backend, you can't.

## The unified rule

Chapters 1–3 built three models separately. Policy-as-code is where they **compose** — one
`allow` rule in [`hands-on-opa/transfer.rego`](./hands-on-opa/transfer.rego):

- **RBAC** — `input.subject.role` must be `teller` or `branch_manager`.
- **ABAC** — `input.amount <= 10000` and the hour is within `08:00–17:00`.
- **ReBAC** — the subject is *related* to the account: a teller of its branch, or the
  manager who `manages` that branch.

*"Amine transfers 8,000 TND at 22:00"* → **DENY** (the hour), from an engine outside the app.

> See it run: [`hands-on-opa/`](./hands-on-opa/) — write the policy, `opa test` it, `opa eval` it.

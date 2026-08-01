# Hands-on: policy-as-code with OPA (Rego)

The transfer rule you already know — but this time it lives **outside the app**, as a
versioned, tested policy. There's no interactive program to run: you write a policy, you
**test** it, and you **query** it. That's the whole point — the rules left the app.

## Prerequisite

Install the **OPA** binary (one file, no server, no Docker):

```bash
brew install opa      # macOS   (see openpolicyagent.org for Linux/Windows)
opa version           # needs OPA >= 1.0
```

## Run the tests

```bash
cd 04-policy-as-code/hands-on-opa
opa test . -v
```

You should see `PASS: 6/6`. Those tests (`transfer_test.rego`) ship *with* the policy — in
policy-as-code, the tests are part of the deliverable, versioned in Git alongside the rules.

## Ask it a question live

```bash
opa eval -d transfer.rego -i input.example.json "data.safibank.transfer.allow" --format raw
```

Prints `true`. Now open `input.example.json`, change `"hour": 9` to `"hour": 22`, and run it
again → `false`. That's the canonical *"Amine at 22:00"* transfer, correctly **denied** — by
an engine that lives outside any application.

## What to notice

1. **All three models, one rule.** `transfer.rego`'s `allow` combines a **role** (RBAC),
   the **amount/hour** limits (ABAC), and the **`manages`/branch relationship** (ReBAC) — in
   a single reviewed file. Chapters 1–3 taught these separately; here they compose.
2. **The rule left the app.** No Python, no `if` buried in a handler. Any service — mobile,
   web, ATM backend — can ask this same policy the same question, so rules can't drift.
3. **It's tested and versioned.** `opa test` is how you prove a rule before shipping it, and
   the whole policy is a text file in Git — exactly what an auditor wants to review.

## Where real ReBAC lives

Here the relationship facts (`account.owner`, `subject.manages`) arrive **in the input**.
In production, the graph answer ("is this user related to this account?") would come from
**OpenFGA** (see [`03-rebac`](../../03-rebac/)) and be handed to OPA as input — OPA composes
with a relationship engine rather than replacing it.

## The files

| File | What it is |
|------|------------|
| `transfer.rego` | The policy: one `allow` rule unifying RBAC + ABAC + ReBAC. |
| `transfer_test.rego` | Real `opa test` unit cases — part of the deliverable. |
| `input.example.json` | A sample request for `opa eval`. |

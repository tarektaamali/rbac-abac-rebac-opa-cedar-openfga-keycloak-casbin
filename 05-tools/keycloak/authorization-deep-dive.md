# Keycloak Authorization — a deep dive (with lots of examples)

> Companion to the [Keycloak reference card](./README.md). This goes **deep** on *how
> Keycloak actually makes authorization decisions* — the vocabulary, every policy type, a
> fully worked SafiBank example, real token payloads, the token-bloat trap, how to test it,
> and when to stop and delegate to OPA / OpenFGA.
>
> Running example throughout: **SafiBank Cloud** (DinarBank + Banque de Carthage; Amine the
> teller, Leila the branch manager, Youssef the customer; accounts in TND; branches Tunis /
> Sfax / Sousse).

---

## 0. First, the mental split: authN vs authZ in Keycloak

Keycloak does **two** jobs. Keep them separate in your head:

| Job | Keycloak feature | Output | SafiBank |
|-----|------------------|--------|----------|
| **authN** — *who are you?* | Login / OIDC / SSO | an **access token** (JWT) with identity + roles | "this is Amine, a `teller` at DinarBank's Tunis branch" |
| **authZ** — *what may you do?* | **Authorization Services** (UMA 2.0) | an **RPT** (Requesting Party Token) with granted permissions | "Amine **may** transfer from account 123" |

**99% of teams only use the authN half** and read roles off the access token. The authZ half
(Authorization Services) is powerful but heavy — this document is mostly about that half, so
you can decide whether you want it.

---

## 1. The vocabulary (this is the hard part)

Keycloak's Authorization Services rename the [PEP/PDP model from `00-foundations`](../../00-foundations/)
into its own words. Learn this table and the rest is easy:

| Keycloak term | Plain meaning | `00-foundations` equivalent | SafiBank example |
|---------------|---------------|-----------------------------|------------------|
| **Resource Server** | the app whose stuff is protected | the thing behind the PEP | `transfer-service` |
| **Resource** | a protected thing | the *resource* | `account`, `transaction` |
| **Scope** | an action on a resource | the *action* | `view`, `transfer`, `approve_loan` |
| **Policy** | a reusable *condition* | part of the *policy* | "is it 08:00–17:00?" |
| **Permission** | binds policies to a resource+scope | the *rule* | "to `transfer` a `transaction`, `can-transfer` must pass" |
| **Policy Enforcer** | the adapter that blocks/allows | the **PEP** | the filter in `transfer-service` |
| **PDP** | Keycloak's evaluation engine | the **PDP** | Keycloak server |
| **RPT** | token listing granted permissions | the *decision*, as a token | "permissions: [transaction#transfer]" |
| **Protection API** | REST API to manage resources/permissions | the **PAP** | admin/automation calls |

> **Key idea:** a **Permission** is where it all comes together — it says *"for this
> resource + scope, these policies must pass."* Policies are the reusable conditions;
> permissions wire them to actions.

---

## 2. RBAC in Keycloak (its strong suit) — examples

Roles are the easy 80%, and they're **free**: they ride in the access token, so no extra call.

### 2.1 The four role/grouping concepts

```
Realm role        → global to everything      → auditor, admin
Client role       → scoped to one app          → transfer-service:teller
Composite role    → a role that bundles others → branch_manager ⊃ teller
Group             → a bucket of users + roles   → "Tunis Branch Staff" → {teller, branch:tunis}
```

### 2.2 What Amine's **access token** actually looks like

After login, Amine's decoded JWT (trimmed) — notice the roles are just *there*:

```json
{
  "sub": "a1b2-amine",
  "preferred_username": "amine",
  "realm_access":   { "roles": ["teller"] },
  "resource_access":{ "transfer-service": { "roles": ["teller"] } },
  "branch": "tunis",
  "tenant": "dinarbank",
  "iss": "https://id.safibank.tn/realms/dinarbank",
  "exp": 1735000000
}
```

Your app authorizes a *coarse* action with **zero** extra network calls:

```python
# The whole "RBAC check" — read a claim off the verified token.
if "teller" not in token["realm_access"]["roles"]:
    raise Forbidden("not a teller")
```

That's why the card rates Keycloak **RBAC ✅**: mature, expressive, and effectively free.

> ⚠️ Note `branch` and `tenant` above are **custom claims** you mapped in. Keep them
> **read-only** (a user must never edit their own branch) — they become security-critical the
> moment a policy trusts them.

---

## 3. ABAC in Keycloak — every policy type, with examples

Attributes are where it strains. Authorization Services give you a **toolbox of policy
types**; you assemble them. Here's the whole toolbox, each with a SafiBank use:

| Policy type | Decides based on… | SafiBank example |
|-------------|-------------------|------------------|
| **Role** | the user's roles | must be `teller` or `branch_manager` |
| **Group** | group membership | must be in "Tunis Branch Staff" |
| **User** | a specific user | only `karim` may edit rules |
| **Client** | which app is calling | only the `atm-backend` client |
| **Time** | current time/date | between 08:00 and 17:00 |
| **Aggregated** | other policies combined | Role **AND** Time **AND** Script |
| **Regex** | a regex over an attribute | `branch` matches `^(tunis|sfax|sousse)$` |
| **JavaScript** | arbitrary logic over attributes | `amount <= 10000 && user.branch == account.branch` |

Two dials shape how they combine:

- **Logic:** `Positive` (grant when it matches) or `Negative` (grant when it does *not*).
- **Decision Strategy** (on aggregated policies & permissions):
  - **Unanimous** — *all* must pass (AND). ← safest, most common for money.
  - **Affirmative** — *any* one passing is enough (OR).
  - **Consensus** — more grants than denies.

### 3.1 A Time policy (built-in, no code)

```
Policy type:  Time
Name:         branch-hours
Not before:            (day start)
Not on or after:       17:00
Hour:         8 – 16     # inclusive hours; 17:00 excluded
Logic:        Positive
```

### 3.2 A JavaScript policy (for real attribute logic)

Roles and time can't say *"amount ≤ 10,000 AND same branch."* That needs a script — which, in
modern Keycloak, is **deployed as a server-side JAR artifact**, not typed into the console
(that's the friction):

```js
// amount-and-branch.js   — packaged and deployed with the server
var ctx     = $evaluation.getContext();
var attrs   = ctx.getAttributes();
var amount  = parseInt(attrs.getValue('amount').asString(0));      // request attribute
var userBr  = ctx.getIdentity().getAttributes().getValue('branch').asString(0); // token claim
var acctBr  = attrs.getValue('account_branch').asString(0);        // request attribute

if (amount <= 10000 && userBr == acctBr) {
    $evaluation.grant();
} else {
    $evaluation.deny();
}
```

> Because this runs inside the server with access to identity, a bug or an editable attribute
> here is a **security incident** — hence the "deploy as a signed artifact, keep attributes
> read-only" rules.

---

## 4. The fully worked example — SafiBank transfer, end to end

Goal: **a teller (or manager of the branch) may `transfer` from an account, ≤ 10,000 TND,
during branch hours, only within their own branch.**

### 4.1 Model the resource + scope

```
Resource: transaction
  Scopes:  view, transfer
```

### 4.2 Write the policies

```
① Role policy   "staff"          → roles: teller, branch_manager (any)
② Time policy   "branch-hours"   → 08:00–17:00
③ Script policy "amount-branch"  → amount <= 10000 && user.branch == account.branch  (§3.2)
```

### 4.3 Combine them (Aggregated, Unanimous)

```
Aggregated policy "can-transfer"
  Policies:  staff, branch-hours, amount-branch
  Decision:  Unanimous          # ALL three must pass
```

### 4.4 Bind to the action (Permission)

```
Scope Permission "transfer-permission"
  Resource:  transaction
  Scope:     transfer
  Policy:    can-transfer
  Decision:  Unanimous
```

### 4.5 Evaluate a request — the decision walk

Amine asks to transfer **8,000 TND** from Youssef's Tunis account at **22:00**:

| Policy | Input | Result |
|--------|-------|--------|
| `staff` | role = teller | ✅ pass |
| `branch-hours` | hour = 22 | ❌ **fail** |
| `amount-branch` | 8000 ≤ 10000, tunis == tunis | ✅ pass |
| **can-transfer** (Unanimous) | one failed | ❌ **DENY** |

Keycloak returns a **deny** — correct! The same request at **09:00** → all three pass → the
RPT is issued granting `transaction#transfer`.

### 4.6 …and the honest tally

That correct answer took **5 artifacts** — a resource, three policies (one a deployed
script), an aggregated policy, and a permission. [`04-policy-as-code`](../../04-policy-as-code/)
expresses the *same* rule as **one** Rego file you can `opa test`. That's the trade.

---

## 5. Getting & reading the RPT (with token examples)

### 5.1 Ask for the decision

The client exchanges its access token for an **RPT** at the token endpoint (UMA grant):

```bash
curl -X POST "https://id.safibank.tn/realms/dinarbank/protocol/openid-connect/token" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d "grant_type=urn:ietf:params:oauth:grant-type:uma-ticket" \
  -d "audience=transfer-service" \
  -d "permission=transaction#transfer"
```

### 5.2 What comes back — the RPT payload

The RPT is a JWT with an `authorization.permissions` claim:

```json
{
  "sub": "a1b2-amine",
  "authorization": {
    "permissions": [
      { "rsname": "transaction", "scopes": ["transfer"] }
    ]
  },
  "realm_access": { "roles": ["teller"] },
  "exp": 1735000300
}
```

Your PEP now just checks: *does the RPT grant `transaction#transfer`?* → yes → proceed.

---

## 6. The token-bloat trap (a worked size example)

Here's the failure mode the card warns about — made concrete.

Suppose you decide to model **each account** as a Keycloak resource and grant per-account
permissions. Amine can see 300 accounts at his branch. His RPT's `permissions` array now has
**300 entries**:

```json
{
  "authorization": { "permissions": [
    { "rsname": "account:1001", "scopes": ["view","transfer"] },
    { "rsname": "account:1002", "scopes": ["view","transfer"] },
    "... 298 more ..."
  ] }
}
```

### 6.1 The math

- Each permission entry ≈ **60–90 bytes** of JSON → 300 entries ≈ **20–27 KB** *before* base64.
- Base64 + JWT signature inflates it further → the encoded token can top **30–40 KB**.
- That token rides in the **`Authorization: Bearer …` header on every request.**

### 6.2 Why that hurts

| Problem | Consequence |
|---------|-------------|
| **Header size limits** | Nginx `large_client_header_buffers` defaults ~8 KB; many proxies/CDNs cap 8–16 KB → the request is **rejected (431 / 400)** or silently truncated. |
| **Bandwidth & CPU** | Every request re-sends and re-parses tens of KB; multiply by request rate. |
| **Revocation** | A permission baked into a token is valid until it **expires** — you can't cheaply revoke "Amine can see account 1002" mid-session. |
| **Caching/cookies** | If tokens land in cookies, you hit the ~4 KB cookie limit almost immediately. |

### 6.3 The rule

> **Keep tokens small and coarse.** Put *identity + broad roles* in the token (a handful of
> claims). Resolve **per-object** access at request time with a dedicated engine —
> [`OpenFGA`](../openfga/) answers *"is Amine related to account 1002?"* in one fast check,
> and **nothing per-account goes in the token.**

---

## 7. Testing a Keycloak policy

Keycloak ships an **Evaluation** tool (Admin Console → Client → Authorization → Evaluate):
pick a user, a resource, a scope, supply context attributes (like `hour=22`), and it shows
the decision **and which policy caused it** — before you ship. Useful, but:

- it's a **console/REST** tool, not `git`-versioned unit tests;
- you can't easily run it in CI on every commit the way you `opa test` a Rego file;
- reproducing "the state that produced this decision" for an auditor is manual.

This is the crux of the **policy-as-code ❌** rating: the rules and their tests live in
Keycloak's database, not as diffable, CI-tested files.

---

## 8. Enforcement — where the PEP lives

- **Java stacks:** the official **`keycloak-policy-enforcer`** adapter can protect endpoints
  declaratively (map paths → resources/scopes) — very little code.
- **Everything else:** you typically do **manual token introspection** — call the token
  endpoint (or introspection endpoint), read `realm_access.roles` (RBAC) or request an RPT
  (fine-grained), and enforce yourself.

```python
# Non-Java PEP, coarse RBAC — the common, pragmatic path.
claims = verify_jwt(bearer_token, jwks)          # signature + exp + iss + aud
if "teller" not in claims["realm_access"]["roles"]:
    raise Forbidden()
# ...for anything finer than a role, ask OPA / OpenFGA (see §9).
```

> This Java-centric enforcement is the last row of the card's **Limites**: outside the JVM,
> Keycloak gives you identity + roles cleanly, and you bring your own PEP.

---

## 9. The pattern that scales: Keycloak *feeds* OPA / OpenFGA

Don't make Keycloak do the hard part. Compose:

```
Amine logs in
   └─► Keycloak issues an access token: identity + roles (teller, branch:tunis, tenant:dinarbank)
Amine clicks "Transfer 8,000 TND from Youssef's account"
   └─► API (PEP) reads the token — role & branch & tenant come FREE from Keycloak ✅
        ├─► ask OPA:     amount ≤ 10,000 AND 08:00–17:00 ?        (ABAC / policy-as-code)
        └─► ask OpenFGA: is Amine's branch related to this account? (ReBAC, per-object)
        └─► both yes → ALLOW    (22:00 → OPA says DENY)
```

- **Keycloak** → *who are you?* + coarse roles (identity)
- **OPA / Cedar** → *does the attribute rule pass?* (time, amount)
- **OpenFGA** → *the right relationship to this exact object?* (ownership) — and it stays **out
  of the token**, so §6's bloat never happens.

---

## 10. Cheat sheet

| Question | Use Keycloak? | Better tool |
|----------|---------------|-------------|
| *Who are you? (login, SSO)* | ✅ **yes, ideal** | — |
| *What broad role do you hold?* | ✅ **yes** (read the token) | — |
| *Time/amount attribute rule* | ⚠️ possible (Time + Script policies) | [OPA](../opa/) / [Cedar](../cedar/) |
| *Only your OWN / this exact object* | 🚫 don't model per-object here | [OpenFGA](../openfga/) |
| *Rules versioned + unit-tested in Git* | 🚫 weak | [OPA](../opa/) / [Cedar](../cedar/) |
| *Millions of per-object checks, small tokens* | 🚫 token bloat | [OpenFGA](../openfga/) |

**One sentence:** Keycloak answers *"who are you?"* brilliantly and *"can you move this exact
money right now?"* poorly — so use it for identity + broad roles, and let it feed a real
policy/relationship engine.

## See also

- [Keycloak reference card](./README.md) — the one-page summary this expands.
- [`01-rbac`](../../01-rbac/) · [`02-abac`](../../02-abac/) · [`03-rebac`](../../03-rebac/) ·
  [`04-policy-as-code`](../../04-policy-as-code/) — the models Keycloak does well, badly, and not at all.
- Keycloak docs: https://www.keycloak.org/docs/latest/authorization_services

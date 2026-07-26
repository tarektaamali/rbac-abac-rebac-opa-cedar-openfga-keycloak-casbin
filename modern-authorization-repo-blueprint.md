# Modern Authorization — Learning Repo (Beginner Blueprint)

> A hands-on repo to learn **RBAC → ABAC → ReBAC → Policy-as-Code**, one small step at a time.
> Every concept uses **ONE running example** so nothing feels abstract:
> **SafiBank Cloud** — an imaginary SaaS banking platform used by Tunisian banks.

---

## 🏦 The Running Example — "SafiBank Cloud"

SafiBank Cloud is **one** piece of software (one website + one database) that several banks pay to use.

**The banks (tenants):**
- *Banque de Carthage*
- *DinarBank*

Each bank is a separate customer → each bank is a **tenant** (more on this word below).

**The people (subjects):**
| Who | Role | What they do |
|-----|------|--------------|
| Mr. Youssef | `customer` | Owns an account at the Tunis branch |
| Amine | `teller` (guichetier) | Works at ONE branch, does daily operations |
| Leila | `branch_manager` | Approves bigger operations |
| Sonia | `auditor` | Read-only, checks everything for compliance |
| Karim | `admin` | Sets up the bank's users and rules |

**The things (resources):** `account` (compte) · `transaction` (virement) · `loan` (crédit)

**The context:** time of day · branch city (Tunis, Sfax, Sousse) · amount in **TND (dinars)** · KYC status

Throughout the whole repo we answer the **same question**, just with a better tool each chapter:

> ❓ *"Can this person do this action on this thing, right now?"*
> Example: *"Can teller **Amine** **transfer 8,000 TND** from **Mr. Youssef's account** at **22:00**?"*

Keep this one sentence in your head. Everything else is just smarter ways to answer it.

---

## 📁 The Repo Structure (annotated)

```
modern-authorization/
│
├── README.md                 ← the map: what this is, the learning path, how to use it
├── GLOSSARY.md               ← every term with a SafiBank example (authN, authZ, PEP, PDP...)
│
├── 00-foundations/           ← START HERE. The 5 ideas everything else hangs on.
│   ├── README.md             ← authN vs authZ, the PEP/PDP split, why authz is hard
│   └── mental-models.md      ← the bank analogy, the "one question" above
│
├── 01-rbac/                  ← Access by ROLE. "You're a teller, so you can do teller things."
│   ├── README.md             ← concept + when to use + the limit that pushes you to ABAC
│   ├── theory.md             ← definition + easy example + SafiBank example
│   └── hands-on-casbin/      ← runnable: teller / manager / customer try 3 actions
│       ├── model.conf
│       ├── policy.csv        ← the roles & permissions, as data (not code)
│       ├── main.py
│       └── README.md         ← how to run + what to notice
│
├── 02-abac/                  ← Access by ATTRIBUTES. Adds time, amount, branch, ownership.
│   ├── README.md
│   ├── theory.md
│   └── hands-on-casbin/      ← same shape: "allow transfer only during branch hours"
│
├── 03-rebac/                 ← Access by RELATIONSHIP. "You OWN this account, so you can see it."
│   ├── README.md
│   ├── theory.md
│   └── hands-on-openfga/     ← model: customer→owns→account→belongs to→branch→bank
│
├── 04-policy-as-code/        ← Move the rules OUT of the app into a versioned, testable engine.
│   ├── README.md
│   ├── theory.md
│   └── hands-on-opa/         ← the same transfer rule, written in Rego (OPA)
│
├── 05-tools/                 ← One folder per tool. Same template. "When do I reach for this?"
│   ├── casbin/               ← lightweight library, lives INSIDE your app (great for RBAC/ABAC)
│   ├── opa/                  ← general policy engine + Rego (Kubernetes, microservices)
│   ├── cedar/                ← AWS's authz language (RBAC + ABAC, easy to analyze)
│   ├── openfga/              ← open-source Google Zanzibar → best for ReBAC/sharing
│   └── keycloak/             ← full identity platform (login/SSO) + some authz
│
├── 06-domains/               ← WHERE you enforce (not a new idea — just a location)
│   ├── apis/                 ← check on every API request (middleware / gateway)
│   ├── saas/                 ← multi-tenant patterns: keep DinarBank ≠ Banque de Carthage
│   ├── kubernetes/           ← OPA Gatekeeper admission control
│   └── cloud-native/         ← sidecar / service mesh
│
├── 07-capstone/              ← ONE small SafiBank app using RBAC→ABAC→ReBAC end to end
│
├── comparisons/              ← the "standard/reference" part — teaches you to CHOOSE
│   ├── rbac-vs-abac-vs-rebac.md
│   └── opa-vs-cedar-vs-casbin.md
│
├── decisions/                ← ADRs: "we chose X because Y" — teaches judgment, not just facts
│
└── resources.md              ← curated links: OpenFGA docs, OPA docs, Zanzibar paper, etc.
```

---

## 📖 GLOSSARY.md — every term with a bank example

Copy this into `GLOSSARY.md`. Definition first, then a SafiBank example so it sticks.

### Authentication (authN)
**Simple:** Proving **who you are**. The login step.
**Everyday:** Showing your CIN card at the door to prove you're really you.
**SafiBank:** Amine logs in with his username + password → the system now knows *"this is Amine, a teller at the Tunis branch of DinarBank."*

### Authorization (authZ)
**Simple:** Deciding **what you're allowed to do** — *after* we know who you are.
**Everyday:** You're inside the bank (authenticated), but only staff may go behind the counter (authorized).
**SafiBank:** Amine is logged in, but *can he* transfer 8,000 TND from Mr. Youssef's account? That yes/no is authorization. **This whole repo is about authZ.**

> 🔑 authN happens **once** (login). authZ happens on **every single action**.

### Subject
**Simple:** The "who" asking to do something (a user or a service).
**SafiBank:** Amine, Leila, Mr. Youssef.

### Resource
**Simple:** The "thing" being accessed.
**SafiBank:** an `account`, a `transaction`, a `loan`.

### Action
**Simple:** What the subject wants to do to the resource.
**SafiBank:** `view`, `transfer`, `approve_loan`, `close_account`.

### Context
**Simple:** The extra facts around the request (not about the user or the thing).
**SafiBank:** it's **22:00**, the request comes from the **Sfax** branch, the amount is **8,000 TND**.

### Policy
**Simple:** The rule that turns (subject + action + resource + context) into **allow / deny**.
**SafiBank:** *"A teller may transfer up to 10,000 TND, only during branch hours (08:00–17:00), only for accounts in their own branch."*

### PEP — Policy Enforcement Point
**Simple:** The **guard** in your code that actually blocks or allows the request. It asks the question; it doesn't decide.
**Everyday:** The security agent at the bank door who checks, but follows the rulebook — he doesn't invent rules.
**SafiBank:** the line in the transfer API that says *"before moving money, ask: is this allowed?"*

### PDP — Policy Decision Point
**Simple:** The **brain** that evaluates the policy and answers yes/no. (OPA, OpenFGA, Cedar, Casbin are all PDPs.)
**Everyday:** The rulebook the security agent consults.
**SafiBank:** the engine that receives *"Amine, transfer, Youssef's account, 8000 TND, 22:00"* and replies **DENY** (after hours).

### PIP — Policy Information Point
**Simple:** Where the PDP **fetches extra facts** it needs to decide.
**SafiBank:** the PDP asks the database *"what branch is this account in?"* and *"what are the Tunis branch's hours?"* — those lookups come from PIPs.

### PAP — Policy Administration Point
**Simple:** Where humans **write and manage** the policies.
**SafiBank:** the admin screen (or the Git repo) where Karim edits the transfer limit from 10,000 to 15,000 TND.

### Tenant
**Simple:** **One customer organization** using your software, with all its users and data kept separate from other customers.
**Everyday:** One family renting one apartment in a shared building.
**SafiBank:** *DinarBank* is one tenant; *Banque de Carthage* is another. Same software, walled-off data.

### Multi-tenant
**Simple:** **One** running copy of the software serves **many** separate customers at once, each isolated.
**Everyday:** One apartment building, many families — nobody can enter another's apartment.
**SafiBank:** Both banks use the same SafiBank Cloud. Amine (DinarBank) must **never** see Banque de Carthage accounts. A leak across this wall = a disaster.

### RBAC — Role-Based Access Control
Access decided by your **role**. → see `01-rbac/`

### ABAC — Attribute-Based Access Control
Access decided by **attributes** (time, amount, ownership, region). → see `02-abac/`

### ReBAC — Relationship-Based Access Control
Access decided by **relationships** ("owns", "member of", "shared with"). → see `03-rebac/`

### Policy-as-Code
Rules written as **code**: versioned in Git, tested, deployed, and enforced by an external engine — instead of `if` statements scattered in your app. → see `04-policy-as-code/`

### Zanzibar
Google's famous system that inspired modern ReBAC tools (OpenFGA, SpiceDB). It stores access as relationships in a big graph.

---

## 🧱 00-foundations — the 5 ideas everything hangs on

**1. authN vs authZ** — *who are you* vs *what may you do*. (See glossary.)

**2. The one question** — every authZ decision answers:
> *Can [subject] do [action] on [resource] in [context]?*

**3. The PEP/PDP split** — your app (PEP) **asks**; a separate engine (PDP) **decides**. This separation is the heart of modern authorization.

```
Amine clicks "Transfer"
        │
        ▼
[ Your App / API ]  ── PEP: "Hey engine, is this allowed?" ──►  [ PDP ]
        ▲                                                         │
        └───────────────  allow / deny  ◄─────────────────────────┘
```

**4. Why authZ is hard** — it must be **flexible** (time, amount, ownership, tenant…), **secure** (no partial failure — a leak is a breach), and **fast** (checked on *every* request). All at once, while rules keep changing.

**5. The bank analogy** — login is the front door (authN). What you may do inside is authZ. Multi-tenant = many banks share one building but never see each other's rooms.

---

## 1️⃣ 01-rbac — access by ROLE

**Definition (simple):** Permissions are attached to **roles**; users get roles; users inherit the role's permissions.

**Easy everyday example:** In any office, a "Manager" badge opens more doors than an "Intern" badge — regardless of *who* wears it.

**SafiBank example:**
| Role | Can do |
|------|--------|
| `customer` | view own account |
| `teller` | view accounts, make transactions |
| `branch_manager` | everything a teller can + approve loans |
| `auditor` | view everything (read-only) |

So: *"Amine is a `teller` → tellers can `transfer` → allow."* Clean and simple. ✅

**Where RBAC breaks (this is the important part 👇):**
1. **Role explosion:** soon you need `manager_tunis`, `manager_sfax`, `manager_loans_under_10k`… roles multiply out of control.
2. **No context:** RBAC can't say *"only during branch hours"* or *"only up to 10,000 TND."*
3. **No relationships:** RBAC can't say *"only if this is **his own** account."*

→ These three pains are exactly why **ABAC** and **ReBAC** exist.

---

## 2️⃣ 02-abac — access by ATTRIBUTES

**Definition (simple):** Decide access using **attributes** of the user, the resource, the action, and the context — not just a role.

**Easy everyday example:** A cinema lets you into an 18+ film based on your **age** (an attribute), not your job title.

**SafiBank example — the transfer rule finally gets real:**
```
ALLOW transfer IF:
    user.role      == "teller"
    AND user.branch == account.branch        (same branch)
    AND amount      <= 10000 TND
    AND time        BETWEEN 08:00 AND 17:00   (branch hours)
```
Now *"Amine transfers 8,000 TND at 22:00"* → **DENY** (after hours). 🎯 RBAC could never express that.

**Strengths:** flexible, context-aware, kills role explosion.
**Where ABAC gets hard:** policies get complex fast, and *"why was I denied?"* becomes tricky to debug.

---

## 3️⃣ 03-rebac — access by RELATIONSHIP

**Definition (simple):** Decide access based on **relationships** between users and things ("owns", "member of", "shared with"), often through a chain.

**Easy everyday example:** You can read a Google Doc because someone **shared it with you** — not because of your job title or any attribute.

**SafiBank example — the relationship chain:**
```
Mr. Youssef  ──owns──►  Account #123  ──belongs to──►  Tunis Branch  ──belongs to──►  DinarBank
```
Rules that fall out naturally:
- Mr. Youssef can `view` Account #123 because he **owns** it.
- Leila can `view` it because she **manages the branch it belongs to**.
- Sonia (auditor) can `view` it because auditing is **shared** to her.

This is the **Google Zanzibar** idea, and **OpenFGA** is the open-source tool for it.

---

## 4️⃣ 04-policy-as-code — pull the rules OUT of the app

**Definition (simple):** Write authorization rules as **code** — versioned in Git, tested, and enforced by an external engine — instead of `if` statements buried in your app.

**Why banking especially needs this:** auditors and regulators ask *"prove who could access this account, and why."* If the rule is one reviewed file in Git (not scattered code), you can answer instantly.

**SafiBank example:** the transfer rule from chapter 2, written once in **Rego (OPA)**, then every service (mobile app, web, ATM backend) asks the same PDP — so the rule can never drift out of sync between them.

```
Client → API → PEP → PDP (OPA / OpenFGA / Cedar) → decision → response
```

---

## 🧭 How to use this repo (beginner path)

1. Read `00-foundations` until the **one question** and **PEP/PDP** feel obvious.
2. Do `01-rbac` — run the Casbin lab, then *feel* it break (role explosion).
3. Do `02-abac` — add the time/amount rule. See the power and the new complexity.
4. Do `03-rebac` — model the ownership chain in OpenFGA.
5. Do `04-policy-as-code` — write it in Rego, understand *why* rules leave the app.
6. Only then explore `05-tools`, `06-domains`, and finally build `07-capstone`.

> ✅ **Golden rule:** finish `00-foundations` + `01-rbac` *completely* (with the running lab) before touching anything else. Two solid chapters beat twenty empty folders.

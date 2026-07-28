"""SafiBank Cloud — 03-rebac hands-on lab (ReBAC, Zanzibar-style).

Access follows RELATIONSHIPS, not roles or attributes. Relationships live in
tuples.csv as OpenFGA-style (subject, relation, object) rows. This pure-Python
checker mirrors the real OpenFGA model in model.fga: an account's viewer is its
owner, or the manager of its branch, or an auditor of its branch's bank.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TUPLES = os.path.join(HERE, "tuples.csv")


class Store:
    """A tiny set of (subject, relation, object) relationship tuples."""

    def __init__(self, tuples):
        self._tuples = set(tuples)

    def has(self, subject, relation, obj):
        """Is there a direct tuple (subject, relation, obj)?"""
        return (subject, relation, obj) in self._tuples

    def parent(self, relation, obj):
        """The subject S of the (unique) tuple (S, relation, obj), or None.

        Used to walk the chain: parent('branch', 'account:123') -> 'branch:tunis'.
        """
        for (s, r, o) in self._tuples:
            if r == relation and o == obj:
                return s
        return None


def load_tuples(path):
    """Parse a tuples.csv into a list of (subject, relation, object)."""
    tuples = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) == 3:
                tuples.append(tuple(parts))
    return tuples


def build_store(path=None):
    """Build a relationship Store from tuples.csv (defaults next to this module)."""
    return Store(load_tuples(path or DEFAULT_TUPLES))


def check(store, subject, account):
    """May `subject` view `account`? Returns (allowed, reason) with the path."""
    # 1. Direct owner.
    if store.has(subject, "owner", account):
        return True, f"owns {account}"
    # 2. Manager of the account's branch.
    branch = store.parent("branch", account)
    if branch and store.has(subject, "manager", branch):
        return True, f"manages {branch}, which owns {account}"
    # 3. Auditor of the branch's bank.
    bank = store.parent("bank", branch) if branch else None
    if bank and store.has(subject, "auditor", bank):
        return True, f"audits {bank}"
    return False, f"no relationship path from {subject} to {account}"


# --- Menu data ------------------------------------------------------------
SUBJECTS = ["youssef", "leila", "sonia", "amine", "fatma"]
ACCOUNTS = ["account:123", "account:999"]

# Canonical demo scenarios: (subject, account).
DEMO_SCENARIOS = [
    ("user:youssef", "account:123"),
    ("user:leila", "account:123"),
    ("user:sonia", "account:123"),
    ("user:amine", "account:123"),
    ("user:leila", "account:999"),
]


def run_demo(store):
    """Evaluate the canonical scenarios. Returns (subject, account, allowed, reason)."""
    rows = []
    for subject, account in DEMO_SCENARIOS:
        allowed, reason = check(store, subject, account)
        rows.append((subject, account, allowed, reason))
    return rows


def _print_demo(store):
    print("\n  SafiBank ReBAC — who can view which account, and WHY\n  " + "-" * 58)
    for subject, account, allowed, reason in run_demo(store):
        mark = "✅ ALLOW" if allowed else "❌ DENY "
        print(f"  {subject:<13} → {account:<12} → {mark}  ({reason})")
    print()


def _print_wall():
    print(
        """
  ReBAC answers "is this user RELATED to this account?" beautifully.
  But it can't answer "...and is the amount under 10,000 TND, during branch hours?"
  That's context — ABAC's job. And roles still matter too.

  Real rules need ALL THREE at once: RBAC + ABAC + ReBAC. Keeping them in sync,
  in-app, across mobile / web / ATM backends, does not scale — and auditors want
  ONE place to ask "who could access this account, and why?"

  -> That's exactly what 04-policy-as-code does: pull every rule OUT of the app
     into one versioned, testable, auditable engine (OPA / Rego).
"""
    )


def _choose(prompt, options):
    """Show a numbered list; accept a number or the option's lowercase name."""
    print(prompt)
    for i, opt in enumerate(options, 1):
        print(f"  [{i}] {opt}")
    raw = input("  > ").strip().lower()
    if raw.isdigit() and 1 <= int(raw) <= len(options):
        return options[int(raw) - 1]
    if raw in [str(o).lower() for o in options]:
        return raw
    return None


def _ask(store):
    who = _choose("Who's asking?", SUBJECTS)
    account = _choose("View which account?", ACCOUNTS)
    if who is None or account is None:
        print("  (unknown — try again)")
        return
    allowed, reason = check(store, f"user:{who}", account)
    mark = "✅ ALLOW" if allowed else "❌ DENY"
    print(f"\n  {mark} — {reason}.")


def main():
    store = build_store()
    print("SafiBank Cloud — ReBAC lab (03-rebac). Type 'q' to quit.")
    while True:
        print("\nMenu: [1] ask a question   [2] demo (who can view, and why)   "
              "[3] wall (the limit of relationships)   [q] quit")
        choice = input("> ").strip().lower()
        if choice in ("q", "quit"):
            print("Bye.")
            return
        if choice in ("2", "demo"):
            _print_demo(store)
            continue
        if choice in ("3", "wall"):
            _print_wall()
            continue
        if choice in ("1", "ask"):
            _ask(store)
            continue
        print("  (pick 1, 2, 3, or q)")


if __name__ == "__main__":
    main()

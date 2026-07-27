"""SafiBank Cloud — 01-rbac hands-on lab (Casbin RBAC).

This module exposes two small, testable functions — build_enforcer() and
decide() — plus an interactive CLI (added in the CLI section). Casbin does the
deciding; model.conf + policy.csv hold the rules as data.
"""
import os

import casbin

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MODEL = os.path.join(HERE, "model.conf")
DEFAULT_POLICY = os.path.join(HERE, "policy.csv")


def build_enforcer(model_path=None, policy_path=None):
    """Build a Casbin enforcer from the model + policy files.

    Paths default to the files next to this module, so the lab runs the same
    no matter what directory you launch it from.
    """
    return casbin.Enforcer(model_path or DEFAULT_MODEL, policy_path or DEFAULT_POLICY)


def decide(enforcer, sub, obj, act):
    """Ask the PDP the one question: may `sub` do `act` on `obj`? -> bool."""
    return bool(enforcer.enforce(sub, obj, act))


# --- Menu data (the only subjects/actions/resources the lab knows) ---------
PEOPLE = [
    ("amine", "teller"),
    ("leila", "branch_manager"),
    ("youssef", "customer"),
    ("sonia", "auditor"),
]
ACTIONS = ["view", "transfer", "approve_loan"]
RESOURCES = ["account", "loan"]

# The 9 canonical scenarios (subject, action, resource) — see the spec.
DEMO_SCENARIOS = [
    ("amine", "view", "account"),
    ("amine", "transfer", "account"),
    ("amine", "approve_loan", "loan"),
    ("leila", "approve_loan", "loan"),
    ("leila", "transfer", "account"),
    ("leila", "view", "account"),
    ("youssef", "view", "account"),
    ("youssef", "transfer", "account"),
    ("sonia", "transfer", "account"),
]

ROLE_OF = dict(PEOPLE)


def _why(sub, obj, act, allowed):
    """One-line human explanation of a verdict (role-based)."""
    role = ROLE_OF.get(sub, "?")
    if allowed:
        return f"{sub.title()} is a {role}; {role}s may {act} on {obj}."
    return f"{sub.title()} is a {role}; {role}s may not {act} on {obj}."


def run_demo(enforcer):
    """Evaluate all canonical scenarios. Returns (sub, act, obj, allowed) rows."""
    rows = []
    for sub, act, obj in DEMO_SCENARIOS:
        rows.append((sub, act, obj, decide(enforcer, sub, obj, act)))
    return rows


def _print_demo(enforcer):
    print("\n  SafiBank RBAC — all scenarios\n  " + "-" * 46)
    for sub, act, obj, allowed in run_demo(enforcer):
        mark = "✅ ALLOW" if allowed else "❌ DENY "
        print(f"  {sub.title():<8} {act:<13} {obj:<8} → {mark}")
    print()


def _print_wall():
    print(
        """
  Try a rule RBAC CAN'T express:
  "A teller may transfer, but only during branch hours (08:00-17:00),
   only from his own branch, only his own account."

  Look at policy.csv — its columns are: subject, object, action.
  There is NO column for TIME, AMOUNT, or OWNERSHIP.
  To fake it with roles you'd need:
     teller_morning -> teller_morning_tunis -> teller_morning_tunis_under_10k ...
  The roles explode. That's the wall.

  The three limits of RBAC:
    1. roles multiply       2. no context (time/amount)   3. no relationships (ownership)

  -> That's exactly what 02-abac (attributes) starts to fix.
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
    if raw in [o.lower() for o in options]:
        return raw
    return None


def main():
    enforcer = build_enforcer()
    print("SafiBank Cloud — RBAC lab (01-rbac). Type 'q' to quit.")
    while True:
        print("\nMenu: [1] ask a question   [2] demo (all scenarios)   "
              "[3] wall (a rule RBAC can't express)   [q] quit")
        choice = input("> ").strip().lower()
        if choice in ("q", "quit"):
            print("Bye.")
            return
        if choice in ("2", "demo"):
            _print_demo(enforcer)
            continue
        if choice in ("3", "wall"):
            _print_wall()
            continue
        if choice not in ("1", "ask"):
            print("  (pick 1, 2, 3, or q)")
            continue
        who = _choose("Who's asking?", [f"{n} ({r})" for n, r in PEOPLE])
        if who is None:
            print("  (unknown — try again)")
            continue
        sub = who.split()[0]
        act = _choose("Do what?", ACTIONS)
        obj = _choose("On which resource?", RESOURCES)
        if act is None or obj is None:
            print("  (unknown — try again)")
            continue
        allowed = decide(enforcer, sub, obj, act)
        mark = "✅ ALLOW" if allowed else "❌ DENY"
        print(f"\n  {mark} — {_why(sub, obj, act, allowed)}")


if __name__ == "__main__":
    main()

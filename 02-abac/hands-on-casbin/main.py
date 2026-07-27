"""SafiBank Cloud — 02-abac hands-on lab (Casbin ABAC on top of RBAC).

Chapter 1 decided by role alone. Here we keep the role check and ADD attribute
conditions (amount, hour, branch) that live in policy.csv as data. build_enforcer()
and decide() are the testable core; an interactive CLI is added below.
"""
import os

import casbin

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MODEL = os.path.join(HERE, "model.conf")
DEFAULT_POLICY = os.path.join(HERE, "policy.csv")


def build_enforcer(model_path=None, policy_path=None):
    """Build a Casbin enforcer from the model + policy files (CWD-independent)."""
    return casbin.Enforcer(model_path or DEFAULT_MODEL, policy_path or DEFAULT_POLICY)


def decide(enforcer, sub, obj, act, *, amount=0, hour=12, sub_branch="", obj_branch=""):
    """Ask the PDP: may `sub` do `act` on `obj`, given the context? -> bool.

    Context is keyword-only with neutral defaults, so rules that don't use
    attributes (their condition is `True`) can be asked without ceremony.
    """
    return bool(
        enforcer.enforce(sub, obj, act, amount, hour, sub_branch, obj_branch)
    )


# --- Menu data ------------------------------------------------------------
PEOPLE = [
    ("amine", "teller", "Tunis"),
    ("leila", "branch_manager", "Tunis"),
    ("youssef", "customer", "Tunis"),
    ("sonia", "auditor", "-"),
]
ACTIONS = ["view", "transfer", "approve_loan"]
RESOURCES = ["account", "loan"]
AMOUNTS = [5000, 8000, 12000]
HOURS = [9, 22]
BRANCHES = ["Tunis", "Sfax"]

ROLE_OF = {name: role for name, role, _ in PEOPLE}
BRANCH_OF = {name: branch for name, _, branch in PEOPLE}

# Canonical demo scenarios: (sub, act, obj, amount, hour, obj_branch).
DEMO_SCENARIOS = [
    ("amine", "transfer", "account", 8000, 9, "Tunis"),
    ("amine", "transfer", "account", 8000, 22, "Tunis"),
    ("amine", "transfer", "account", 12000, 9, "Tunis"),
    ("amine", "transfer", "account", 8000, 9, "Sfax"),
    ("leila", "transfer", "account", 8000, 9, "Tunis"),
    ("youssef", "transfer", "account", 8000, 9, "Tunis"),
]


def _transfer_reason(role, amount, hour, sub_branch, obj_branch):
    """Explain a transfer verdict in one line (mirrors the policy condition)."""
    if role not in ("teller", "branch_manager"):
        return f"the {role} role may not transfer at all"
    if not (8 <= hour < 17):
        return f"after branch hours ({hour:02d}:00 is outside 08:00-17:00)"
    if amount > 10000:
        return f"over the 10,000 TND limit ({amount} TND)"
    if sub_branch != obj_branch:
        return f"different branch ({sub_branch} != {obj_branch})"
    return "within hours, under the limit, same branch"


def run_demo(enforcer):
    """Evaluate the canonical scenarios. Returns (sub, amount, obj_branch, hour, allowed)."""
    rows = []
    for sub, act, obj, amount, hour, obj_branch in DEMO_SCENARIOS:
        allowed = decide(
            enforcer, sub, obj, act,
            amount=amount, hour=hour,
            sub_branch=BRANCH_OF.get(sub, "-"), obj_branch=obj_branch,
        )
        rows.append((sub, amount, obj_branch, hour, allowed))
    return rows


def _print_demo(enforcer):
    print("\n  SafiBank ABAC — the same transfer, different context\n  " + "-" * 58)
    for sub, act, obj, amount, hour, obj_branch in DEMO_SCENARIOS:
        sub_branch = BRANCH_OF.get(sub, "-")
        allowed = decide(enforcer, sub, obj, act, amount=amount, hour=hour,
                         sub_branch=sub_branch, obj_branch=obj_branch)
        mark = "✅ ALLOW" if allowed else "❌ DENY "
        reason = _transfer_reason(ROLE_OF.get(sub, "?"), amount, hour, sub_branch, obj_branch)
        print(f"  {sub.title():<8} transfer {amount:>6} TND {obj_branch:<6} "
              f"{hour:02d}:00 → {mark}  ({reason})")
    print()


def _print_wall():
    print(
        """
  ABAC nailed time, amount, and branch. But try these:
  "Only the account's OWNER may close it."
  "The manager of the BRANCH THAT OWNS the account may view it."

  You can bolt on attributes — owner_id, branch_id, manager_of_branch — but you
  must keep them all in sync, everywhere, forever. Ownership and hierarchy are
  RELATIONSHIPS, not attributes. Modelling them as attributes gets brittle fast.

  -> That's exactly what 03-rebac (relationships, à la Google Zanzibar) is for.
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


def _ask(enforcer):
    who = _choose("Who's asking?", [f"{n} ({r})" for n, r, _ in PEOPLE])
    if who is None:
        print("  (unknown — try again)")
        return
    sub = who.split()[0]
    act = _choose("Do what?", ACTIONS)
    obj = _choose("On which resource?", RESOURCES)
    if act is None or obj is None:
        print("  (unknown — try again)")
        return
    # Context only matters for transfer; other rules are unconditional.
    if act == "transfer":
        amount = _choose("How much (TND)?", AMOUNTS)
        hour = _choose("What hour (24h)?", HOURS)
        obj_branch = _choose("Account is in which branch?", BRANCHES)
        if amount is None or hour is None or obj_branch is None:
            print("  (unknown — try again)")
            return
        amount, hour = int(amount), int(hour)
    else:
        amount, hour, obj_branch = 0, 12, BRANCH_OF.get(sub, "-")
    sub_branch = BRANCH_OF.get(sub, "-")
    allowed = decide(enforcer, sub, obj, act, amount=amount, hour=hour,
                     sub_branch=sub_branch, obj_branch=obj_branch)
    mark = "✅ ALLOW" if allowed else "❌ DENY"
    if act == "transfer":
        reason = _transfer_reason(ROLE_OF.get(sub, "?"), amount, hour, sub_branch, obj_branch)
    else:
        role = ROLE_OF.get(sub, "?")
        reason = f"role {role} " + ("may" if allowed else "may not") + f" {act} {obj}"
    print(f"\n  {mark} — {reason}.")


def main():
    enforcer = build_enforcer()
    print("SafiBank Cloud — ABAC lab (02-abac). Type 'q' to quit.")
    while True:
        print("\nMenu: [1] ask a question   [2] demo (the flip)   "
              "[3] wall (a rule ABAC handles clumsily)   [q] quit")
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
        if choice in ("1", "ask"):
            _ask(enforcer)
            continue
        print("  (pick 1, 2, 3, or q)")


if __name__ == "__main__":
    main()

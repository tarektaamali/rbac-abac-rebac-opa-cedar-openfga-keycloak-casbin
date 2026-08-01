"""SafiBank Cloud — 07-capstone app: the PEP around the layered pipeline.

TransferService asks authorize() (the PDP) and either records a mock ledger
move or denies with the layer that stopped it. A guided CLI lets you watch the
whole pipeline decide, request by request.
"""
from authorize import Subject, Account, authorize

SUBJECTS = {
    "amine": Subject("amine", "teller", "tunis", "", "dinarbank"),
    "leila": Subject("leila", "branch_manager", "tunis", "tunis", "dinarbank"),
    "youssef": Subject("youssef", "customer", "tunis", "", "dinarbank"),
    "fatma": Subject("fatma", "customer", "carthage", "", "carthage"),
}

ACCOUNTS = {
    "acc:123": Account("acc:123", "tunis", "youssef", "dinarbank"),
    "acc:456": Account("acc:456", "sfax", "sami", "dinarbank"),
    "acc:999": Account("acc:999", "carthage", "fatma", "carthage"),
}

# One request per gate — each layer stops exactly one.
DEMO_SCENARIOS = [
    ("amine", "acc:123", 8000, 9),
    ("amine", "acc:123", 8000, 22),
    ("amine", "acc:123", 12000, 9),
    ("amine", "acc:999", 8000, 9),
    ("youssef", "acc:123", 8000, 9),
    ("amine", "acc:456", 8000, 9),
    ("leila", "acc:123", 8000, 9),
]

AMOUNTS = [5000, 8000, 12000]
HOURS = [9, 22]


class TransferService:
    """The PEP: asks the PDP, then executes or denies."""

    def __init__(self, subjects=None, accounts=None):
        self.subjects = subjects or SUBJECTS
        self.accounts = accounts or ACCOUNTS
        self.ledger = []

    def transfer(self, subject_id, account_id, amount, hour):
        decision = authorize(self.subjects[subject_id], self.accounts[account_id], amount, hour)
        if decision.allow:
            self.ledger.append((subject_id, account_id, amount))
            return f"executed: {amount} TND from {account_id}"
        return f"denied at {decision.layer}: {decision.reason}"


def run_demo(service=None):
    """Evaluate the canonical scenarios. Returns (sub, acct, amount, hour, Decision)."""
    service = service or TransferService()
    rows = []
    for sid, aid, amount, hour in DEMO_SCENARIOS:
        decision = authorize(service.subjects[sid], service.accounts[aid], amount, hour)
        rows.append((sid, aid, amount, hour, decision))
    return rows


def _print_demo(service):
    print("\n  SafiBank capstone — one request through the whole pipeline\n  " + "-" * 60)
    for sid, aid, amount, hour, decision in run_demo(service):
        if decision.allow:
            mark = "✅ ALLOW"
        else:
            mark = f"❌ DENY at {decision.layer.upper()}"
        print(f"  {sid:<8} → {aid:<8} {amount:>6} TND {hour:02d}:00 → {mark:<16} ({decision.reason})")
    print()


def _choose(prompt, options):
    print(prompt)
    for i, opt in enumerate(options, 1):
        print(f"  [{i}] {opt}")
    raw = input("  > ").strip().lower()
    if raw.isdigit() and 1 <= int(raw) <= len(options):
        return options[int(raw) - 1]
    if raw in [str(o).lower() for o in options]:
        return raw
    return None


def _ask(service):
    sid = _choose("Who's asking?", list(service.subjects.keys()))
    aid = _choose("Transfer from which account?", list(service.accounts.keys()))
    amount = _choose("How much (TND)?", AMOUNTS)
    hour = _choose("What hour (24h)?", HOURS)
    if None in (sid, aid, amount, hour):
        print("  (unknown — try again)")
        return
    print(f"\n  {service.transfer(sid, aid, int(amount), int(hour))}")


def main():
    service = TransferService()
    print("SafiBank Cloud — capstone (07). The whole stack, one request. Type 'q' to quit.")
    while True:
        print("\nMenu: [1] ask a transfer   [2] demo (one request per gate)   [q] quit")
        choice = input("> ").strip().lower()
        if choice in ("q", "quit"):
            print("Bye.")
            return
        if choice in ("2", "demo"):
            _print_demo(service)
            continue
        if choice in ("1", "ask"):
            _ask(service)
            continue
        print("  (pick 1, 2, or q)")


if __name__ == "__main__":
    main()

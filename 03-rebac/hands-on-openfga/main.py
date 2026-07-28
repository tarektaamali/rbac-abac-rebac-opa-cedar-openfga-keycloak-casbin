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

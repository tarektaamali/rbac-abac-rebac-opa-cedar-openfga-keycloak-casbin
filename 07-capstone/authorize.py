"""SafiBank Cloud — 07-capstone: the whole decision, one layered pipeline.

This composes chapters 1-4 into a single authorize() function that runs four
gates IN ORDER — tenant -> RBAC -> ABAC -> ReBAC — and reports which gate
decided. The order is load-bearing: the tenant wall is checked first.
"""
from dataclasses import dataclass


@dataclass
class Subject:
    id: str
    role: str        # customer | teller | branch_manager | auditor
    branch: str      # home branch (for tellers)
    manages: str     # branch a manager manages ("" otherwise)
    tenant: str      # dinarbank | carthage


@dataclass
class Account:
    id: str
    branch: str
    owner: str
    tenant: str


@dataclass
class Decision:
    allow: bool
    layer: str       # "tenant" | "rbac" | "abac" | "rebac" | "*"
    reason: str


def _related(subject, account):
    """ReBAC: is this staff member related to the account's branch?"""
    if subject.role == "teller":
        return subject.branch == account.branch
    if subject.role == "branch_manager":
        return subject.manages == account.branch
    return False


def authorize(subject, account, amount, hour):
    """Run the gates in order; the first failing gate decides. -> Decision."""
    # 1. TENANT — the wall comes first.
    if subject.tenant != account.tenant:
        return Decision(False, "tenant",
                        f"cross-tenant: {subject.tenant} != {account.tenant}")
    # 2. RBAC — may this role transfer at all?
    if subject.role not in ("teller", "branch_manager"):
        return Decision(False, "rbac", f"role {subject.role} may not transfer")
    # 3. ABAC — amount & branch hours.
    if amount > 10000:
        return Decision(False, "abac", f"over the 10,000 TND limit ({amount} TND)")
    if not (8 <= hour < 17):
        return Decision(False, "abac", f"after branch hours ({hour:02d}:00)")
    # 4. ReBAC — related to the account's branch?
    if not _related(subject, account):
        return Decision(False, "rebac", f"not related to branch {account.branch}")
    return Decision(True, "*", "all gates passed")

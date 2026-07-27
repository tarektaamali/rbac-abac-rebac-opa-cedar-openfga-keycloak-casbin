import os
import pytest
from main import build_enforcer, decide

HERE = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture
def enforcer():
    return build_enforcer()


# (subject, action, resource, expected) — the 9 canonical scenarios from the spec.
SCENARIOS = [
    ("amine", "view", "account", True),      # 1 teller can view
    ("amine", "transfer", "account", True),  # 2 teller can transfer
    ("amine", "approve_loan", "loan", False),# 3 teller cannot approve loans
    ("leila", "approve_loan", "loan", True), # 4 manager can approve
    ("leila", "transfer", "account", True),  # 5 manager inherits teller
    ("leila", "view", "account", True),      # 6 manager inherits teller
    ("youssef", "view", "account", True),    # 7 customer can view
    ("youssef", "transfer", "account", False),# 8 customer cannot transfer
    ("sonia", "transfer", "account", False), # 9 auditor is read-only
]


@pytest.mark.parametrize("sub,act,obj,expected", SCENARIOS)
def test_canonical_scenarios(enforcer, sub, act, obj, expected):
    assert decide(enforcer, sub, obj, act) is expected


def test_role_inheritance_specifically(enforcer):
    # Leila is a branch_manager but can transfer ONLY because manager inherits teller.
    assert decide(enforcer, "leila", "account", "transfer") is True


def test_build_enforcer_is_cwd_independent(tmp_path, monkeypatch):
    # Defaults resolve next to main.py, not the caller's CWD.
    monkeypatch.chdir(tmp_path)
    e = build_enforcer()
    assert decide(e, "amine", "account", "transfer") is True

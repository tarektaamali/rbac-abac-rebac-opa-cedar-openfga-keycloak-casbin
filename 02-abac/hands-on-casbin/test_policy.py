import os
import pytest
from main import build_enforcer, decide

HERE = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture
def enforcer():
    return build_enforcer()


def test_transfer_allowed_within_hours(enforcer):
    # Amine, 8,000 TND, same branch, 09:00 -> ALLOW
    assert decide(enforcer, "amine", "account", "transfer",
                  amount=8000, hour=9, sub_branch="Tunis", obj_branch="Tunis") is True


def test_transfer_denied_after_hours(enforcer):
    # THE canonical flip: same request, 22:00 -> DENY
    assert decide(enforcer, "amine", "account", "transfer",
                  amount=8000, hour=22, sub_branch="Tunis", obj_branch="Tunis") is False


def test_transfer_denied_over_limit(enforcer):
    assert decide(enforcer, "amine", "account", "transfer",
                  amount=12000, hour=9, sub_branch="Tunis", obj_branch="Tunis") is False


def test_transfer_denied_wrong_branch(enforcer):
    assert decide(enforcer, "amine", "account", "transfer",
                  amount=8000, hour=9, sub_branch="Tunis", obj_branch="Sfax") is False


def test_inheritance_still_holds_under_abac(enforcer):
    # Leila (branch_manager) inherits teller AND satisfies the conditions.
    assert decide(enforcer, "leila", "account", "transfer",
                  amount=8000, hour=9, sub_branch="Tunis", obj_branch="Tunis") is True


def test_unconditional_rules_ignore_context(enforcer):
    # view has cond=True; passing no context still works.
    assert decide(enforcer, "youssef", "account", "view") is True
    # customer cannot transfer at all (role layer denies, regardless of context).
    assert decide(enforcer, "youssef", "account", "transfer",
                  amount=8000, hour=9, sub_branch="Tunis", obj_branch="Tunis") is False


def test_auditor_readonly(enforcer):
    assert decide(enforcer, "sonia", "account", "view") is True
    assert decide(enforcer, "sonia", "account", "transfer",
                  amount=8000, hour=9, sub_branch="Tunis", obj_branch="Tunis") is False


def test_build_enforcer_is_cwd_independent(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    e = build_enforcer()
    assert decide(e, "amine", "account", "transfer",
                  amount=8000, hour=9, sub_branch="Tunis", obj_branch="Tunis") is True


def test_run_demo_returns_six_rows_with_the_flip(enforcer):
    from main import run_demo
    rows = run_demo(enforcer)
    assert len(rows) == 6
    d = {(s, amt, br, hr): allowed for (s, amt, br, hr, allowed) in rows}
    assert d[("amine", 8000, "Tunis", 9)] is True     # within hours
    assert d[("amine", 8000, "Tunis", 22)] is False    # THE flip: after hours
    assert d[("amine", 12000, "Tunis", 9)] is False    # over limit
    assert d[("amine", 8000, "Sfax", 9)] is False       # wrong branch
    assert d[("leila", 8000, "Tunis", 9)] is True       # manager inherits teller
    assert d[("youssef", 8000, "Tunis", 9)] is False    # customer role can't transfer

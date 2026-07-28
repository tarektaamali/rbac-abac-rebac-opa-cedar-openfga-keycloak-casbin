import os
import pytest
from main import build_store, check

HERE = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture
def store():
    return build_store()


def test_owner_path(store):
    allowed, reason = check(store, "user:youssef", "account:123")
    assert allowed is True
    assert "owns" in reason


def test_manager_from_branch_path(store):
    allowed, reason = check(store, "user:leila", "account:123")
    assert allowed is True
    assert "manages branch:tunis" in reason


def test_auditor_from_bank_path(store):
    allowed, reason = check(store, "user:sonia", "account:123")
    assert allowed is True
    assert "audits bank:dinarbank" in reason


def test_teller_has_no_path(store):
    # Amine is a teller, but role != relationship: no path to this account.
    allowed, reason = check(store, "user:amine", "account:123")
    assert allowed is False
    assert "no relationship path" in reason


def test_cross_tenant_isolation_falls_out_of_graph(store):
    # Leila manages a DinarBank branch; account:999 is Banque de Carthage. No path.
    allowed, reason = check(store, "user:leila", "account:999")
    assert allowed is False
    assert "no relationship path" in reason


def test_build_store_is_cwd_independent(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    s = build_store()
    allowed, _ = check(s, "user:youssef", "account:123")
    assert allowed is True

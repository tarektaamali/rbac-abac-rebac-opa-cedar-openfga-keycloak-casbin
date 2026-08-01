from authorize import Subject, Account, authorize


def sub(role="teller", branch="tunis", manages="", tenant="dinarbank", id="amine"):
    return Subject(id, role, branch, manages, tenant)


def acc(branch="tunis", owner="youssef", tenant="dinarbank", id="acc:123"):
    return Account(id, branch, owner, tenant)


def test_happy_path_allows():
    d = authorize(sub(), acc(), 8000, 9)
    assert d.allow is True and d.layer == "*"


def test_after_hours_denied_at_abac():
    d = authorize(sub(), acc(), 8000, 22)
    assert d.allow is False and d.layer == "abac"


def test_over_limit_denied_at_abac():
    d = authorize(sub(), acc(), 12000, 9)
    assert d.allow is False and d.layer == "abac"


def test_cross_tenant_denied_at_tenant():
    d = authorize(sub(tenant="dinarbank"), acc(tenant="carthage"), 8000, 9)
    assert d.allow is False and d.layer == "tenant"


def test_customer_denied_at_rbac():
    d = authorize(sub(role="customer"), acc(), 8000, 9)
    assert d.allow is False and d.layer == "rbac"


def test_wrong_branch_denied_at_rebac():
    d = authorize(sub(branch="tunis"), acc(branch="sfax"), 8000, 9)
    assert d.allow is False and d.layer == "rebac"


def test_manager_of_branch_allows():
    d = authorize(sub(role="branch_manager", manages="tunis"), acc(branch="tunis"), 8000, 9)
    assert d.allow is True and d.layer == "*"


def test_ordering_tenant_before_rebac():
    # Cross-tenant AND wrong-branch: must stop at TENANT (the first gate), not rebac.
    d = authorize(sub(branch="tunis", tenant="dinarbank"),
                  acc(branch="carthage", tenant="carthage"), 8000, 9)
    assert d.layer == "tenant"


def test_run_demo_decides_each_gate():
    from app import run_demo
    rows = run_demo()
    assert len(rows) == 7
    d = {(s, a, amt, hr): dec for (s, a, amt, hr, dec) in rows}
    assert d[("amine", "acc:123", 8000, 9)].allow is True
    assert d[("amine", "acc:123", 8000, 22)].layer == "abac"
    assert d[("amine", "acc:123", 12000, 9)].layer == "abac"
    assert d[("amine", "acc:999", 8000, 9)].layer == "tenant"
    assert d[("youssef", "acc:123", 8000, 9)].layer == "rbac"
    assert d[("amine", "acc:456", 8000, 9)].layer == "rebac"
    assert d[("leila", "acc:123", 8000, 9)].allow is True


def test_transfer_service_executes_and_denies():
    from app import TransferService
    svc = TransferService()
    assert svc.transfer("amine", "acc:123", 8000, 9).startswith("executed")
    assert "denied at tenant" in svc.transfer("amine", "acc:999", 8000, 9)
    assert len(svc.ledger) == 1  # only the allowed transfer was recorded

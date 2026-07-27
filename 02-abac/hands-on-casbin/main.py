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

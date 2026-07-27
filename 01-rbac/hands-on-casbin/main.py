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

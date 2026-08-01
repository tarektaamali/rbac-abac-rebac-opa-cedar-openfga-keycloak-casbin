package safibank.transfer

# Under OPA 1.0+ (Rego v1) the `if` keyword is built in — no keyword imports needed.

default allow := false

# You may transfer if the amount and hour are within policy (ABAC) AND you are
# staff of the branch that owns the account (RBAC role + ReBAC relationship).
allow if {
	input.amount <= 10000 # ABAC — amount limit (inclusive)
	input.hour >= 8 # ABAC — branch hours start
	input.hour < 17 # ABAC — branch hours end (17:00 exclusive)
	staff_of_owning_branch
}

# A teller of the branch that owns the account …
staff_of_owning_branch if {
	input.subject.role == "teller" # RBAC
	input.subject.branch == input.account.branch # relationship to the owning branch
}

# … or the manager who MANAGES that branch.
staff_of_owning_branch if {
	input.subject.role == "branch_manager" # RBAC
	input.subject.manages == input.account.branch # ReBAC — the "manages" relationship
}

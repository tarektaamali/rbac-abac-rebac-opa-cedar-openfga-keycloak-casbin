package safibank.transfer

test_teller_same_branch_in_hours_allowed if {
	allow with input as {"subject": {"role": "teller", "branch": "tunis", "manages": ""}, "account": {"branch": "tunis", "owner": "youssef"}, "amount": 8000, "hour": 9}
}

test_after_hours_denied if {
	not allow with input as {"subject": {"role": "teller", "branch": "tunis", "manages": ""}, "account": {"branch": "tunis", "owner": "youssef"}, "amount": 8000, "hour": 22}
}

test_over_limit_denied if {
	not allow with input as {"subject": {"role": "teller", "branch": "tunis", "manages": ""}, "account": {"branch": "tunis", "owner": "youssef"}, "amount": 12000, "hour": 9}
}

test_wrong_branch_denied if {
	not allow with input as {"subject": {"role": "teller", "branch": "tunis", "manages": ""}, "account": {"branch": "sfax", "owner": "youssef"}, "amount": 8000, "hour": 9}
}

test_manager_of_managed_branch_allowed if {
	allow with input as {"subject": {"role": "branch_manager", "branch": "tunis", "manages": "tunis"}, "account": {"branch": "tunis", "owner": "youssef"}, "amount": 8000, "hour": 9}
}

test_manager_of_other_branch_denied if {
	not allow with input as {"subject": {"role": "branch_manager", "branch": "sfax", "manages": "sfax"}, "account": {"branch": "tunis", "owner": "youssef"}, "amount": 8000, "hour": 9}
}

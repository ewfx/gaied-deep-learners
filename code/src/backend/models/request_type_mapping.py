REQUEST_TYPES = {
    "Adjustment": [],
    "AU Transfer": ["Reallocation Fees", "Amendment Fees", "Reallocation Principal"],
    "Closing Notice": ["Cashless Roll", "Decrease", "Increase"],
    "Commitment Change": [],
    "Fee Payment": ["Ongoing Fee", "Letter of Credit Fee"],
    "Money Movement - Inbound": ["Principal", "Interest", "Principal + Interest", "Principal + Interest + Fee"],
    "Money Movement - Outbound": ["Timebound", "Foreign Currency"]
}

# Define a priority score (lower number = higher priority)
REQUEST_PRIORITY = {
    "Money Movement - Inbound": 1,
    "Money Movement - Outbound": 2,
    "Adjustment": 3,
    "Fee Payment": 4,
    "AU Transfer": 5,
    "Closing Notice": 6,
    "Commitment Change": 7
}

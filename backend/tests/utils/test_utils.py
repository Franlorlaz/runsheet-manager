from datetime import datetime
from calendar import month_abbr

from app.utils import upgrade_str_counter


def test_upgrade_str_counter_increments_counter():
    prefix = "arbitrary_prefix-"
    assert prefix.endswith("-")

    existing = [
        f"{prefix}001",
        f"{prefix}002",
        f"{prefix}010",
    ]

    next_counter = upgrade_str_counter(str_ids=existing)
    new_str = upgrade_str_counter(str_ids=existing, prefix=prefix)

    assert next_counter == 11
    assert new_str == f"{prefix}011"


def test_ignores_other_prefixes():
    prefix = "arbitrary_prefix-"
    existing = [
        "24nov-099",
        f"{prefix}003",
        "25jan-001",
    ]

    new_str = upgrade_str_counter(existing, prefix=prefix)

    assert new_str == f"{prefix}004"


def test_ignores_malformed_str():
    prefix = "arbitrary_prefix-"
    existing = [
        f"{prefix}001",
        f"{prefix}abc",
        f"{prefix}",
        "invalid",
    ]

    next_counter = upgrade_str_counter(existing)
    new_str = upgrade_str_counter(existing, prefix=prefix)

    assert next_counter == 2
    assert new_str == f"{prefix}002"

from datetime import date

from arr import Contract, ContractHeader, ContractLine, annualize

import pytest


@pytest.fixture
def simple_contract():
    return Contract(
        1,
        ContractHeader(20_000, date(2024, 1, 1), date(2024, 12, 31)),
        [
            ContractLine(4_000, date(2024, 1, 1), date(2024, 12, 31), 1, True),
            ContractLine(4_000, date(2024, 1, 1), date(2024, 12, 31), 2, True),
            ContractLine(4_000, date(2024, 1, 1), date(2024, 12, 31), 3, True),
            ContractLine(4_000, date(2024, 1, 1), date(2024, 12, 31), 4, True),
            ContractLine(4_000, date(2024, 1, 1), date(2024, 12, 31), 5, False),
        ],
    )


def test_sanity():
    assert 1 == 1


def test_contract(simple_contract):
    assert type(simple_contract) == Contract
    assert type(simple_contract.header) == ContractHeader

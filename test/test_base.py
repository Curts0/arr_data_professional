import os
from datetime import date

from arr import Contract, ContractHeader, ContractLine

import pytest
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor


def test_sanity():
    assert 1 == 1


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


def test_contract(simple_contract):
    assert type(simple_contract) == Contract
    assert type(simple_contract.header) == ContractHeader


notebooks = [x for x in os.listdir() if os.path.splitext(x)[-1] == ".ipynb"]


@pytest.mark.parametrize("notebook_name", notebooks)
def test_notebook_run(notebook_name: str):
    with open(notebook_name) as f:
        nb = nbformat.read(f, as_version=4)
    ExecutePreprocessor().preprocess(nb)

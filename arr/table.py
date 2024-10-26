from .contract import Contract, ContractLine
from .annualize import annualize, active_check, deferred_check

from datetime import date
from typing import List, Literal

import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta


def get_end_of_month_range(start: date, end: date) -> np.ndarray:
    """Helper function to get a list of end of month dates.

    Args:
        start (date): Start date.
        end (date): End Date.

    Returns:
        ndarray: Numpy array of dates inbetween.
    """
    assert end > start, "end date must be later than start date"
    end_of_month_range = []
    working_date = start
    while working_date < end:
        end_of_month_range.append(working_date + relativedelta(day=31))
        working_date = working_date + relativedelta(months=1)
    return np.array(end_of_month_range)


def build_contracts_table(contracts: List[Contract]) -> pd.DataFrame:
    """Takes inputed Contract(s) converts to usable DataFrame.

    Args:
        contracts (List[Contract]): List of `Contract` dataclass.

    Returns:
        pd.DataFrame: DataFrame of Contract(s). 1 Row == 1 Line in a Contract.
            Both header and line information is in each row.
    """
    contracts = pd.DataFrame(contracts)
    headers = pd.DataFrame.from_records(contracts["header"])
    headers.rename(
        columns={
            "amount": "header_amount",
            "start_date": "header_start_date",
            "end_date": "header_end_date",
        },
        inplace=True,
    )
    lines_temp = contracts["lines"].explode()
    lines = pd.json_normalize(lines_temp)
    lines.index = lines_temp.index
    lines.rename(
        columns={
            "amount": "line_amount",
            "start_date": "line_start_date",
            "end_date": "line_end_date",
        },
        inplace=True,
    )
    df = (
        contracts.merge(headers, left_index=True, right_index=True)
        .merge(lines, left_index=True, right_index=True)
        .drop(columns=["header", "lines"])
        .reset_index(drop=True)
    )
    return df


def row_annualization(
    row: pd.Series, col_name: Literal["line", "header"], include_deferred: bool
) -> int:
    amount = annualize(
        ContractLine(
            row.line_amount,
            row[f"{col_name}_start_date"],
            row[f"{col_name}_end_date"],
            row.item_sku,
            row.renewable,
        ),
        row.period,
        "Month",
        True,
    )
    active = active_check(
        row[f"{col_name}_start_date"], row[f"{col_name}_end_date"], row.period
    )

    deferred = deferred_check(
        row.booking_date, row[f"{col_name}_start_date"], row.period
    )

    if active:
        return amount
    elif include_deferred and deferred:
        return amount
    else:
        return 0


def build_acv_table(
    contracts: List[Contract], by_lines: bool = True, include_deferred: bool = True
) -> pd.DataFrame:
    """Builds ACV DataFrame.

    Takes list of inputed `Contracts` and first builds a regular
    contract table with `build_contracts_table`. Then cross-joins
    with possible date values from `get_end_of_month_range`.
    Month range is determined by oldest and newest possible dates
    that are provided in the contracts. Depending on annualizing
    by header or by lines it will annualize the expected results.

    Args:
        contracts (List[Contract]): A list of the `Contract` dataclass.
        by_lines (bool, optional): bool to determine whether to
            annualize by header or by lines. If `True`, will annualize
            by lines, `False` will annualize by header. Defaults to True.
        include_deferred (bool, optional): bool to determine whether to
            include deferred ARR or not. If `True` data will include
            deferred ARR. `False` data will not include deferred ARR.
            Defaults to True.

    Returns:
        pd.DataFrame: Pandas dataframe as a matrix. The dates are the
            columns and contract id, item_sku, and renewability as
            the rows. ACV will be the values.
    """
    # 1
    all_lines = []

    for contract in contracts:
        all_lines += contract.lines

    min_booking_date = min([contract.header.booking_date for contract in contracts])
    min_start_date = min([line.start_date for line in all_lines])
    min_date = min(min_booking_date, min_start_date)
    max_date = max([line.end_date for line in all_lines])

    range = pd.DataFrame(get_end_of_month_range(min_date, max_date)).rename(
        columns={0: "period"}
    )

    # 2
    acv_table = range.merge(build_contracts_table(contracts), how="cross")

    # 3
    col_name = "line" if by_lines else "header"

    acv_table["acv"] = acv_table.apply(
        lambda row: row_annualization(row, col_name, include_deferred),
        axis=1,
    )

    # 4
    cols = ["period", "id", "item_sku", "renewable"]

    acv_table = acv_table[["period", "id", "item_sku", "renewable", "acv"]]

    acv_table = (
        pd.DataFrame(acv_table.groupby(cols).sum())
        .unstack(level=0)
        .drop(
            columns=[
                col for col in acv_table.columns if col not in cols and col != "acv"
            ]
        )
    )

    return acv_table["acv"]

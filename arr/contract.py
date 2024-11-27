from __future__ import annotations
from .annualize import annualize, active_check, deferred_check, get_end_of_month_range

from dataclasses import dataclass
from datetime import date
from typing import List

import pandas as pd


@dataclass
class ContractHeader:
    """Dataclass to handle the header of a contract.

    Args:
        amount (int): Total contract value.
        start_date (date): The start date of the Contract.
        end_date (date): The end date of the Contract.
        booking_date (date): The date the contract was booked.
            Defaults to `None`, if nothing is provided, but
            gets replaced to the `start_date` in the `__post_init__()`
    """

    amount: int
    start_date: date
    end_date: date
    booking_date: date = None

    def __post_init__(self):
        if self.booking_date is None:
            self.booking_date = self.start_date


@dataclass
class ContractLine:
    """Dataclass to handle contract lines.

    Args:
        amount (int): Total value of the line.
        start_date (date): The Start Date of the Contract.
        end_date (date): The End Date of the Contract.
        product (int): The product purchased by customer.
        renewable (bool): indicator whether or not product
            is renewable.
    """

    amount: int
    start_date: date
    end_date: date
    product: str
    renewable: bool


def repr_builder(contract):
    tcv = "{:,}".format(contract.header.amount)
    customer_name = (
        "Example Customer" if contract.customer is None else contract.customer
    )
    customer = "{:^60}".format(customer_name)
    title = "{:^60}".format(
        f"Contract #{str(contract.id)} - ${tcv} - {contract.header.booking_date}"
    )
    header = "{:^60}".format(
        f"{contract.header.start_date} - {contract.header.end_date}"
    )

    buffer = "*" * 60 + "\n"
    full_line_text = buffer + "product\tstart date\tend date\tamount\trenewable\n"
    full_line_text += buffer

    for line in contract.lines:
        fields = [
            line.product,
            line.start_date,
            line.end_date,
            "${:,}".format(line.amount),
            line.renewable,
        ]
        fields = list(map(str, fields))
        line_text = "\t".join(fields) + "\n"
        full_line_text += line_text

    full_line_text += buffer

    return "\n".join([customer, title, header, full_line_text])


@dataclass
class Contract:
    """Bringing it together."""

    id: int
    header: ContractHeader
    lines: List[ContractLine]
    customer: str = None

    def __repr__(self) -> str:
        return repr_builder(self)

    def to_df(self) -> pd.DataFrame:
        """Converts to usable DataFrame.

        Returns:
            pd.DataFrame: Contract attributes are named as is.
                contract header attributes will have prefix of
                'header.' and contract line attributes will
                have a prefix of 'line.'.
        """
        contract_dict = self.__dict__.copy()
        contract_dict["header"] = self.header.__dict__.copy()
        contract_dict["lines"] = [line.__dict__.copy() for line in self.lines]

        df = pd.json_normalize(contract_dict)
        lines = pd.DataFrame.from_dict(df["lines"].iloc[0]).add_prefix("line.")
        df = df.merge(lines, how="cross").drop(columns="lines")

        for col in df.columns:
            if "date" in col:
                df[col] = df[col].astype("datetime64[ns]")

        return df

    def to_annualize_df(
        self, by_lines: bool = True, arr: bool = True, deferred: bool = True
    ):
        # TODO: use  *args, **kwargs for more dynamic annualize func
        # pass through all the options

        df = self.to_df()
        min_date = min(df.select_dtypes("datetime64").min()).date()
        max_date = max(df.select_dtypes("datetime64").max()).date()

        range = pd.DataFrame(get_end_of_month_range(min_date, max_date)).rename(
            columns={0: "period"}
        )
        df = range.merge(df, how="cross")

        df["period"] = df["period"].astype("datetime64[ns]")

        col_name = "line" if by_lines else "header"

        df["active"] = df.apply(
            lambda row: active_check(
                row[f"{col_name}.start_date"],
                row[f"{col_name}.end_date"],
                row["period"],
            ),
            axis=1,
        )

        df["deferred"] = df.apply(
            lambda row: deferred_check(
                row["header.booking_date"],
                row["header.start_date"],
                row["line.start_date"],
                row["period"],
            ),
            axis=1,
        )

        annualize_name = "ARR" if arr else "ACV"

        df[annualize_name] = df.apply(
            lambda row: annualize(
                ContractLine(
                    row[f"line.amount"],
                    row[f"{col_name}.start_date"].date(),
                    row[f"{col_name}.end_date"].date(),
                    row["line.product"],
                    row["line.renewable"],
                ),
                row["period"].date(),
                "Month",
                True,
                False,
            ),
            axis=1,
        )

        cols = ["period", "id", "line.product"]

        if arr:
            df = df[df["line.renewable"] == True]

        if deferred:
            df = df[(df["active"] == True) | (df["deferred"] == True)]
        else:
            df = df[df["active"] == True]

        df = pd.DataFrame(df[cols + [annualize_name]].groupby(cols).sum()).unstack(
            level=0
        )

        df.fillna(0, inplace=True)

        return df

    @staticmethod
    def from_df(df: pd.DataFrame):
        return Contract(
            df.iloc[0]["id"],
            ContractHeader(
                df.iloc[0]["header.amount"],
                df.iloc[0]["header.start_date"],
                df.iloc[0]["header.end_date"],
                df.iloc[0]["header.booking_date"],
            ),
            [
                ContractLine(
                    line[1]["line.amount"],
                    line[1]["line.start_date"],
                    line[1]["line.end_date"],
                    line[1]["line.product"],
                    line[1]["line.renewable"],
                )
                for line in df.iterrows()
            ],
            df.iloc[0]["customer"],
        )

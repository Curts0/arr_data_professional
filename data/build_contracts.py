"""This is slop. I'm sorry."""


from random import choices, choice
from typing import List
from datetime import date

from arr import Contract, ContractHeader, ContractLine

import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta as rd

MIN_DATE = date(2020, 1, 1)
MAX_DATE = date(2026, 12, 31)
START_DATES = pd.date_range(MIN_DATE, MAX_DATE)
RENEWAL_CHANCE = 0.8
EXPANSION_CHANCE = 0.1
DOWNGRADE_CHANCE = 0.1

CUSTOMERS = pd.read_excel("data/saas_corp.xlsx", "customer")
CUSTOMERS.set_index("key", inplace=True)

PRODUCTS = pd.read_excel("data/saas_corp.xlsx", "product")
PRODUCTS.set_index("key", inplace=True)
PRODUCT_WEIGHTS = np.arange(0, 1, 1 / len(PRODUCTS))[::-1]
PRODUCT_COUNT = len(PRODUCTS["product_name"].unique())

print('reading manually added contracts')
CONTRACTS = pd.read_excel("data/saas_corp.xlsx", "contract")
date_cols = [
    "header.start_date",
    "header.end_date",
    "header.booking_date",
    "line.start_date",
    "line.end_date",
]

for col in date_cols:
    CONTRACTS[col] = CONTRACTS[col].astype("datetime64[ns]")

# print(
#     CONTRACTS.dtypes,
#     PRODUCTS.dtypes,
#     CUSTOMERS.dtypes,
#     sep="\n------------------------------------\n",
# )


def random_contract_range(
    contract_lengths: List[int] = [3, 6, 12, 24, 36],
    contract_weights: List[float] = [0.1, 0.05, 0.6, 0.2, 0.05],
) -> int:
    """Get a random contract length interval.

    Wrapper for:
    https://docs.python.org/3/library/random.html#random.choices

    Args:
        contract_lengths (List[int], optional): Possible contract lengths, in months.
            Defaults to [3, 6, 12, 24, 36].
        contract_weights (List[float], optional): Weights of the `contract_lengths`, arg.
            Defaults to [0.1, 0.05, 0.6, 0.2, 0.05].

    Returns:
        int: Length of contract in months.
    """
    return choices(contract_lengths, contract_weights)[0]


def initial_sale(customer: str) -> Contract:
    """Get customer start, end dates. Get customer items for first sale"""

    # TODO Return manual contract
    start_date = choice(START_DATES).date()
    contract_range = random_contract_range()
    end_date = start_date + rd(months=contract_range, days=-1)

    num_of_items = choices(range(1, PRODUCT_COUNT + 1), PRODUCT_WEIGHTS)[0]
    products = PRODUCTS.loc[np.random.choice(PRODUCTS.index, num_of_items, False)]

    contract = Contract(
        id=CONTRACTS["id"].max() + 1,
        header=ContractHeader(products["amount"].sum(), start_date, end_date),
        lines=[
            ContractLine(
                row[1]["amount"],
                start_date,
                end_date,
                row[1]["product_name"],
                row[1]["renewable"],
            )
            for row in products.iterrows()
        ],
        customer=customer,
    )

    return contract


def renewal(contract: Contract) -> Contract | None:
    could_renew = True if contract.header.end_date < MAX_DATE else False
    will_renew = choices([True, False], [RENEWAL_CHANCE, 1 - RENEWAL_CHANCE])[0]
    will_expand = choices([True, False], [EXPANSION_CHANCE, 1 - EXPANSION_CHANCE])[0]
    will_downgrade = choices([True, False], [DOWNGRADE_CHANCE, 1 - DOWNGRADE_CHANCE])[0]

    start_date = contract.header.end_date + rd(days=1)
    end_date = start_date + rd(months=random_contract_range(), days=-1)

    df = contract.to_df()

    current_products = PRODUCTS[
        PRODUCTS["product_name"].isin(df["line.product"].unique())
    ]

    potential_products = PRODUCTS[
        ~PRODUCTS["product_name"].isin(current_products["product_name"].unique())
    ]

    new_products = current_products

    if will_expand and len(current_products) < PRODUCT_COUNT:
        expansion = potential_products.loc[
            np.random.choice(potential_products.index, 1, False)
        ]
        new_products = pd.concat([expansion, current_products])

    if will_downgrade and len(current_products) > 1:
        rand_prod = np.random.choice(new_products.index, 1, False)
        new_products = new_products.drop(index=rand_prod)

    contract = Contract(
        id=CONTRACTS["id"].max() + 1,
        header=ContractHeader(new_products["amount"].sum(), start_date, end_date),
        lines=[
            ContractLine(
                row[1]["amount"],
                start_date,
                end_date,
                row[1]["product_name"],
                row[1]["renewable"],
            )
            for row in new_products.iterrows()
        ],
        customer=contract.customer,
    )

    if could_renew and will_renew:
        return contract
    else:
        return None


# initial sales
print('performing initial sales')
for customer in CUSTOMERS["customer"].unique():

    if customer in CONTRACTS["customer"].unique():
        pass
        # print(f"{customer} already in contract list")

    else:

        CONTRACTS = pd.concat(
            [CONTRACTS, initial_sale(customer).to_df()], ignore_index=True
        )

# subsequent renewals
# this is so badly written, sorry.
print('performing subsequent renewals')
renew_cycle = True
no_more_renewal = []
while renew_cycle:
    next_cycle = False
    contracts_to_check = (
        CONTRACTS[["customer", "id"]].groupby("customer").max()["id"].to_numpy()
    )
    for contract_id in contracts_to_check:
        contract = Contract.from_df(CONTRACTS[CONTRACTS["id"] == contract_id])
        renew_contract = renewal(contract)
        if renew_contract is None or contract.customer in no_more_renewal:
            no_more_renewal.append(contract.customer)
        else:
            df = renew_contract.to_df()
            CONTRACTS = pd.concat([df, CONTRACTS], ignore_index=True)
            next_cycle = True
    renew_cycle = next_cycle

from dataclasses import dataclass
from datetime import date
from typing import List


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
        item_sku (int): To designate item skus
    """

    amount: int
    start_date: date
    end_date: date
    item_sku: int
    renewable: bool


def repr_builder(contract):
    # TODO: Add customer name to repr
    tcv = "{:,}".format(contract.header.amount)
    title = "{:^55}".format(
        f"Contract #{str(contract.id)} - ${tcv} - {contract.header.booking_date}"
    )
    header = "{:^55}".format(
        f"{contract.header.start_date} - {contract.header.end_date}"
    )

    buffer = "*" * 55 + "\n"
    full_line_text = buffer + "sku\tstart date\tend date\tamount\trenewable\n"
    full_line_text += buffer

    for line in contract.lines:
        fields = [
            line.item_sku,
            line.start_date,
            line.end_date,
            line.amount,
            line.renewable,
        ]
        fields = list(map(str, fields))
        line_text = "\t".join(fields) + "\n"
        full_line_text += line_text

    full_line_text += buffer

    return "\n".join([title, header, full_line_text])


@dataclass
class Contract:
    """Bringing it together."""

    id: int
    header: ContractHeader
    lines: List[ContractLine]
    customer: str = None

    def __repr__(self) -> str:
        return repr_builder(self)

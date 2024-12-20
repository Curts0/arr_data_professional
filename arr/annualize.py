from typing import TYPE_CHECKING
from datetime import date, timedelta
from typing import Literal
from calendar import isleap

# TODO: fix type hinting for annualize func...
# if TYPE_CHECKING:
#     from .contract import Contract, ContractLine

from dateutil.relativedelta import relativedelta
import numpy as np


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


def active_check(start_date: date, end_date: date, period: date) -> bool:
    """Is the Contract Active?

    `True` == Yes contract is active in period.
    `False`== No contract is not active in period.
    """
    return start_date <= period <= end_date


def deferred_check(
    bookings_date: date, header_start_date: date, line_start_date: date, period: date
) -> bool:
    """Is the Contract Deferred?

    `True` == Yes contract is deferred in period.
    `False`== No contract is not deferred in period.
    """
    return (
        bookings_date < header_start_date
        and period < header_start_date
        and line_start_date == header_start_date
    )


def count_leap_days(start_date: date, end_date: date) -> int:
    """Helper function to output the # of leap days in date range.

    Args:
        start_date (date): Start date of contract.
        end_date (date): End date of contract.

    Returns:
        int: Number of leap days in the range of dates.
    """
    leap_check = start_date.year
    leap_days = []
    while leap_check <= end_date.year:
        if isleap(leap_check):
            leap_days.append(date(leap_check, 2, 29))
        leap_check += 1

    leap_count = len([*filter(lambda x: start_date <= x <= end_date, leap_days)])
    return leap_count


INTERVAL = Literal["Year", "Quarter", "Month", "Day"]


def get_contract_term(
    start_date: date, end_date: date, generalize_leap_year: bool, interval_str: INTERVAL
) -> int:
    """Primary use is to be nested in the `annualize` func.

    Will output the denominator of the ARR formula (Contract Term).

    Args:
        start_date (date): Start date of contract.
        end_date (date): End date of contract.
        generalize_leap_year (bool): Hard code 365 or add the extra day if `True`.
        interval_str (INTERVAL): see `INTERVAL` variable for possible options.

    Returns:
        int: Contract Term #.
    """

    # 1
    math_end_date = end_date + timedelta(days=1)
    contract_term_length_month = (math_end_date.year - start_date.year) * 12 + (
        math_end_date.month - start_date.month
    )
    contract_term_length_year = contract_term_length_month // 12
    contract_term_length_quarter = contract_term_length_month // 3

    contract_term_length_day = (math_end_date - start_date).days
    contract_term_nl_day = contract_term_length_day - count_leap_days(
        start_date, end_date
    )

    # 2
    contract_term_mapping = {
        "Year": contract_term_length_year,
        "Quarter": contract_term_length_quarter,
        "Month": contract_term_length_month,
        "Day": (
            contract_term_nl_day if generalize_leap_year else contract_term_length_day
        ),
    }

    return contract_term_mapping[interval_str]


def annualize(
    contract,
    period: date,
    interval_str: INTERVAL,
    generalize_leap_year: bool = True,
    print_details: bool = False,
) -> int:
    """Takes the input of `ContractHeader or `ContractLine` dataclass and annualizes tcv.

    Args:
        contract (ContractHeader | Contract Line): See dataclasses.
        period (date): The date in which we are looking at the ARR.
            Example, what is the ACV on Jan 31, 2024. Jan 31, 2024
            would be the `period`.
        interval_str (INTERVAL): The options to chose from when deciding
            what interval to multiply `tcv` by. Possible options are:
            "Year", "Quarter", "Month", "Day".
        generalize_leap_year (bool): Toggle to decide who to handle leap years.
            `True` will not consider leap years and set all years to 365 days.
            `False` will call `calendar.isleap(year)` of the `period` value
            to determine if the year has 366 days in it.
        print_details (bool): Optional if you want to see details
            of some of the args and variables.

    Returns:
        int: Returns Annual Contract Value. The annualized amount of
            Total Contract Value.
    """

    # 1
    if generalize_leap_year:
        day = 365
    else:
        day = 365 + isleap(period.year)

    # 2
    interval_mapping = {"Year": 1, "Quarter": 4, "Month": 12, "Day": day}
    time_interval = interval_mapping[interval_str]

    # 3
    contract_term = get_contract_term(
        contract.start_date, contract.end_date, generalize_leap_year, interval_str
    )

    # 4
    if print_details:
        print(contract)
        print(f"Period: {period}")
        print(f"Generalize Leap Year: {generalize_leap_year}")
        print(f"Time Interval: {interval_str} - {time_interval}")
        print(f"Contract Term: {contract_term}")
        print(f"{contract.amount} * ({time_interval}/{contract_term})")

    # 5
    try:
        fraction = time_interval / contract_term
    except ZeroDivisionError:
        fraction = 0

    return contract.amount * (fraction)

"""Helpfull utilities for the project."""

import pandas as pd


def fix_tz(
    time: str | pd.Timestamp | pd.Series | pd.DatetimeIndex,
    tz_from: str = "UTC",
    tz_to: str = "UTC",
) -> pd.Timestamp | pd.Series | pd.DatetimeIndex:
    """Convert a string or pandas time object to a different timezone.

    Args:
        time (str | pd.Timestamp | pd.Series | pd.DatetimeIndex): A string, pandas Timestamp, Series, or DatetimeIndex.
        tz_from (str): The timezone of the input time if tz-naive. Default is 'UTC'.
        tz_to (str): The target timezone. Default is 'UTC'.

    Returns:
        pd.Timestamp | pd.Series | pd.DatetimeIndex: The input time object converted to the target timezone. String input will be converted to pandas timestamp.
    """
    # Convert string to pandas Timestamp
    if isinstance(time, str):
        time = pd.Timestamp(time)

    # Depending on the type, convert to UTC
    if isinstance(time, pd.Series):
        return (
            time.dt.tz_convert(tz_to)
            if time.dt.tz
            else time.dt.tz_localize(tz_from).dt.tz_convert(tz_to)
        )
    elif isinstance(time, (pd.DatetimeIndex, pd.Timestamp)):
        return (
            time.tz_convert(tz_to)
            if time.tz
            else time.tz_localize(tz_from).tz_convert(tz_to)
        )
    else:
        raise TypeError(
            "Input must be a string, pandas Timestamp, Series, or DatetimeIndex."
        )


if __name__ == "__main__":
    pass

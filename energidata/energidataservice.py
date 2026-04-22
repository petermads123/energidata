"""API for collecting data from EnergiDataService."""

import json

import pandas as pd
import requests

_BASE_URL = "https://api.energidataservice.dk/dataset/"


def _get_prices(
    endpoint: str,
    start: pd.Timestamp,
    end: pd.Timestamp | None,
    bz: str | list[str],
    data_cols: str | list[str],
    tz_aware: bool = True,
) -> pd.DataFrame:
    """Helper method to fetch price data from EnergiDataService.

    Assumes a time column "TimeUTC" and a "PriceArea" column.
    Data is returned in a pivoted format with "UTC" as index and bz as columns.

    Args:
        endpoint (str): API endpoint to fetch data from.
        start (pd.Timestamp): start timestamp for the data.
        end (pd.Timestamp | None): end timestamp for the data.
        bz (str | list[str]): bidding zone(s) to filter the data by.
        data_cols (str | list[str]): column(s) to include in the returned DataFrame.
        tz_aware (bool): whether to return tz-aware timestamps in the "UTC" index.

    Returns:
        pd.DataFrame: DataFrame containing the price data.
            index:
                "UTC": timestamp in UTC timezone.
            data_cols:
                bz: price in EUR/MWh for the specified bidding zone(s).
    """
    if isinstance(bz, str):
        bz = [bz]
    if start.tzinfo is None:
        start = start.tz_localize("CET")
    if end is None:
        end = (start + pd.DateOffset(days=1)).normalize()
    if end.tzinfo is None and end is not None:
        end = end.tz_localize("CET")

    url = _BASE_URL + endpoint
    params = {
        "start": start.tz_convert("CET")
        .tz_localize(None)
        .isoformat(timespec="minutes"),
        "end": (
            end.tz_convert("CET").tz_localize(None).isoformat(timespec="minutes")
            if end is not None
            else (start + pd.DateOffset(days=1))
            .tz_convert("CET")
            .tz_localize(None)
            .normalize()
            .isoformat(timespec="minutes")
        ),
        "filter": json.dumps({"PriceArea": bz}),
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(
            f"Failed to fetch data: {response.status_code} - {response.text}"
        )
    data = response.json()
    records = data.get("records", [])
    df = pd.DataFrame(records)

    df["UTC"] = pd.to_datetime(df["TimeUTC"])
    if tz_aware:
        df["UTC"] = df["UTC"].dt.tz_localize("UTC")

    df = df.pivot(index="UTC", columns="PriceArea", values=data_cols)

    return df


def get_dayahead_prices(
    start: pd.Timestamp,
    end: pd.Timestamp | None = None,
    bz: str | list[str] = "DK2",
    tz_aware: bool = True,
) -> pd.DataFrame:
    """Get day-ahead price data from EnergiDataService.

    Args:
        start (pd.Timestamp): start timestamp for the data.
            If tz-naive, CET timezone is assumed.
        end (pd.Timestamp | None): end timestamp for the data (excluded).
            If tz-naive, CET timezone is assumed.
            If None, EOD of start is used.
            Default is None.
        bz (str | list[str]): bidding zone(s) to filter the data by.
            Valid bzs are "DK1", "DK2", "DE", "NO2", "SE3", "SE4".
            Default is "DK1".
        tz_aware (bool): whether to return tz-aware timestamps in the "UTC" column.
            Default is True.

    Returns:
        pd.DataFrame: DataFrame containing the day-ahead price data.
            "UTC": timestamp in UTC timezone.
            bz: price in EUR/MWh for the specified bidding zone(s).
    """
    return _get_prices(
        endpoint="DayAheadPrices",
        start=start,
        end=end,
        bz=bz,
        data_cols="DayAheadPriceEUR",
        tz_aware=tz_aware,
    )


def get_imbalance_prices(
    start: pd.Timestamp,
    end: pd.Timestamp | None = None,
    bz: str | list[str] = "DK1",
    tz_aware: bool = True,
) -> pd.DataFrame:
    """Get imbalance price data from EnergiDataService.

    Args:
        start (pd.Timestamp): start timestamp for the data.
            If tz-naive, CET timezone is assumed.
        end (pd.Timestamp | None): end timestamp for the data (excluded).
            If tz-naive, CET timezone is assumed.
            If None, EOD of start is used.
            Default is None.
        bz (str | list[str]): bidding zone(s) to filter the data by.
            Valid bzs are "DK1", "DK2", "DE", "NO2", "SE3", "SE4".
            Default is "DK1".
        tz_aware (bool): whether to return tz-aware timestamps in the "UTC" column.
            Default is True.

    Returns:
        pd.DataFrame: DataFrame containing the imbalance price data.
            "UTC": timestamp in UTC timezone.
            bz: price in EUR/MWh for the specified bidding zone(s).
    """
    return _get_prices(
        endpoint="ImbalancePrice",
        start=start,
        end=end,
        bz=bz,
        data_cols="ImbalancePriceEUR",
        tz_aware=tz_aware,
    )


if __name__ == "__main__":
    start = pd.Timestamp("2026-04-01")
    end = pd.Timestamp("2026-04-04")
    bzs = ["DK1", "DK2"]

    da_prices = get_dayahead_prices(start, end, bzs)
    imbalance_prices = get_imbalance_prices(start, end, bzs)

    print(da_prices)
    print(imbalance_prices)

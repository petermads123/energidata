"""This is a generic API class for data from energidataservice.dk."""

from typing import Any

import pandas as pd

from energidata.utils._genericapi import GenericAPI
from energidata.utils._utils import fix_tz


class EnergiDataServiceAPI(GenericAPI):
    """Generic API class for data from energidataservice.dk."""

    def __init__(self) -> None:
        """Initialize the EnergiDataServiceAPI class."""
        self.base_url = "https://api.energidataservice.dk/dataset/"

    def define_params(
        self,
        url_extension: str,
        start: str | pd.Timestamp | None = None,
        end: str | pd.Timestamp | None = None,
        tz: str = "CET",
        additional_params: dict | None = None,
    ) -> None:
        """Define parameters for the API call.

        Args:
            url_extension (str): The URL extension for the specific dataset.
            start (str | pd.Timestamp | None): The start date/time. Default is None.
            end (str | pd.Timestamp | None): The end date/time. Default is None.
            tz (str, optional): The time zone to assume the input dates have. Default is "CET".
            additional_params (dict | None, optional): Additional parameters to include. Default is None.
        """
        # Create empty params dict
        self.params = {}

        if start is not None:
            # If end is None make end one day after start
            start_fixed = fix_tz(start, tz_from=tz, tz_to=tz)
            # If end is None, set to start + 1 day (tz-aware. Can result in 92/96/100 timesteps due to DST)
            end_fixed = (
                (start_fixed + pd.DateOffset(days=1))
                if end is None
                else fix_tz(end, tz_from=tz, tz_to=tz)
            )

            self.start = fix_tz(start_fixed)
            self.end = fix_tz(end_fixed)
            self.tz = tz

            self.params["start"] = self.start.strftime("%Y-%m-%dT%H:%M")
            self.params["end"] = self.end.strftime("%Y-%m-%dT%H:%M")
            self.params["timezone"] = "UTC"

        if additional_params:
            filter_list = []
            for key, value in additional_params.items():
                filter_list.append(f"'{key}':{value}".replace("'", '"'))
            self.params["filter"] = "{" + ",".join(filter_list) + "}"

        # Define url
        self.url = self.base_url + url_extension

    def call_api(self) -> dict[str, Any]:
        """Call the API and return the data as a dictionary.

        Returns:
            dict[str, Any]: The data returned from the API call.
        """
        # Call the API
        self.data_dict = self.call(url=self.url, params=self.params)

        return self.data_dict

    def get_dataframe(self) -> pd.DataFrame:
        """Convert the data dictionary to a pandas DataFrame.

        Returns:
            pd.DataFrame: The data as a pandas DataFrame.
        """
        # Convert to DataFrame
        df = pd.DataFrame(self.data_dict["records"])

        # Rename and convert time columns
        if "TimeUTC" in df.columns:
            df = df.rename(columns={"TimeUTC": "UTC"})
            df = df.drop(columns=["TimeDK"])
            df["UTC"] = pd.to_datetime(df["UTC"]).dt.tz_localize("UTC")
            if self.tz != "UTC":
                df[self.tz] = df["UTC"].dt.tz_convert(self.tz)
            df = df.sort_values(["UTC", "PriceArea"]).reset_index(drop=True)

        return df


def get_day_ahead_prices(
    start: str | pd.Timestamp,
    end: str | pd.Timestamp | None = None,
    bidding_zone: str | list[str] | None = None,
    tz: str = "CET",
) -> pd.DataFrame:
    """Get day ahead prices for specified bidding zones and time range.

    If no end date is provided, data for one day from the start date is returned.
    Note that if the above is done, the output length might range from 92 to 100 due to DST.

    Args:
        start (str | pd.Timestamp): The start date/time.
        end (str | pd.Timestamp | None, Optional): The end date/time. Default is None.
        bidding_zone (str | list[str] | None, Optional): The bidding zone(s) to filter by. Default is None.
        tz (str, Optional): The time zone to assume the input dates have. Default is "CET".

    Returns:
        pd.DataFrame: ["UTC", "CET", "PriceArea", "DayAheadPriceEUR", "DayAheadPriceDKK"]
    """
    # Make sure bidding_zone is a list
    if isinstance(bidding_zone, str):
        bidding_zone = [bidding_zone]

    additional_params = {"PriceArea": bidding_zone} if bidding_zone else None

    api = EnergiDataServiceAPI()
    api.define_params(
        url_extension="DayAheadPrices",
        start=start,
        end=end,
        tz=tz,
        additional_params=additional_params,
    )
    api.call_api()
    df = api.get_dataframe()

    return df


def get_imbalance_prices(
    start: str | pd.Timestamp,
    end: str | pd.Timestamp | None = None,
    bidding_zone: str | list[str] | None = None,
    tz: str = "CET",
) -> pd.DataFrame:
    """Get imbalance prices for specified bidding zones and time range.

    If no end date is provided, data for one day from the start date is returned.
    Note that if the above is done, the output length might range from 92 to 100 due to DST.

    Args:
        start (str | pd.Timestamp): The start date/time.
        end (str | pd.Timestamp | None, Optional): The end date/time. Default is None.
        bidding_zone (str | list[str] | None, Optional): The bidding zone(s) to filter by. Default is None.
        tz (str, Optional): The time zone to assume the input dates have. Default is "CET".

    Returns:
        pd.DataFrame: ["UTC", "CET", "PriceArea", "ImbalancePriceEUR", "ImbalancePriceDKK" ...]
    """
    # Make sure bidding_zone is a list
    if isinstance(bidding_zone, str):
        bidding_zone = [bidding_zone]

    additional_params = {"PriceArea": bidding_zone} if bidding_zone else None

    api = EnergiDataServiceAPI()
    api.define_params(
        url_extension="ImbalancePrice",
        start=start,
        end=end,
        tz=tz,
        additional_params=additional_params,
    )
    api.call_api()
    df = api.get_dataframe()

    return df


def get_dso_tariffs(
    start: str | pd.Timestamp,
    end: str | pd.Timestamp | None = None,
    tz: str = "CET",
    dso: str | list[str] = "Radius Elnet A/S",
    tariff: str | list[str] = "Nettarif C",
) -> pd.DataFrame:
    """Get DSO tariffs for specified DSOs.

    If no end date is provided, data for one day from the start date is returned.
    Note that if the above is done, the output length might range from 92 to 100 due to DST.
    Values are given in DKK/kWh.
    For Radius, the dso name is "Radius Elnet A/S".
    For Cerius, the dso name is "Cerius A/S".
    For Radius and Cerius, the c-tariff is "Nettarif C".

    Args:
        start (str | pd.Timestamp): The start date/time.
        end (str | pd.Timestamp | None, Optional): The end date/time. Default is None.
        tz (str, Optional): The time zone to assume the input dates have. Default is "CET".
        dso (str | list[str]): The DSO(s) to filter by. Default is "Radius Elnet A/S".
        tariff (str | list[str]): The tariff(s) to filter by. Default is "Nettarif C".

    Returns:
        pd.DataFrame: ["UTC", "CET", "DSO", "TariffDKK"]
    """
    # Make sure dso is a list
    if isinstance(dso, str):
        dso = [dso]

    if isinstance(tariff, str):
        tariff = [tariff]

    additional_params = {}

    if dso:
        additional_params["ChargeOwner"] = dso

    if tariff:
        additional_params["Note"] = tariff

    api = EnergiDataServiceAPI()
    api.define_params(
        url_extension="DatahubPricelist",
        additional_params=additional_params,
    )
    api.params["limit"] = 0  # Get all data
    api.call_api()
    df_tariffs = api.get_dataframe()

    date_range = pd.date_range(
        start=fix_tz(start, tz_from=tz, tz_to="CET"),
        end=fix_tz(end, tz_from=tz, tz_to="CET")
        if end
        else fix_tz(start, tz_from=tz, tz_to="CET") + pd.DateOffset(days=1),
        freq="15min",
        inclusive="left",
    )

    prices = []
    for dso_ in dso:
        for tariff_ in tariff:
            prices.append(f"{dso_}_{tariff_}")

    df = pd.DataFrame(columns=["CET"] + prices)
    df["CET"] = date_range

    def _set_tariff(row: pd.Series) -> pd.Series:
        for dso_ in dso:
            for tariff_ in tariff:
                cet = row["CET"]
                value = df_tariffs.loc[
                    (df_tariffs["FromDate"] <= cet)
                    & (df_tariffs["ToDate"] > cet)
                    & (df_tariffs["ChargeOwner"] == dso_)
                    & (df_tariffs["Note"] == tariff_),
                ][f"Price{cet.hour}"]
                row[f"{dso_}_{tariff_}"] = value.values[0] if not value.empty else None
        return row

    df = df.apply(_set_tariff, axis=1)

    return df


# Testing
if __name__ == "__main__":
    df_spot = get_day_ahead_prices(start="2025-10-26", bidding_zone="DK1")
    # df_imbalance = get_imbalance_prices(start="2025-10-26", bidding_zone="DK1")
    # df_tariffs = get_dso_tariffs(
    #     start="2025-10-26", dso="Radius Elnet A/S", tariff="Nettarif C"
    # )
    print(df_spot)
    # print(df_imbalance)
    # print(df_tariffs)

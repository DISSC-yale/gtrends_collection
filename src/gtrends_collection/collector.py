"""Collect Google Trends health data."""

import datetime
from os import getenv
from os.path import isfile
from time import sleep
from typing import ClassVar, Dict, List, Union

from apiclient import discovery, errors
from pandas import DataFrame, concat, json_normalize, to_datetime

from gtrends_collection.utils import read_scope


class Collector:
    """
    Collect internet search volumes from the Google Trends timeline for health endpoint.

    See the [schema](https://trends.googleapis.com/$discovery/rest?version=v1beta)
    for more about the API. Only the `getTimelinesForHealth` endpoint is used here.

    Args:
        scope_dir (str): Directory containing the `terms.txt` and `locations.txt` files.
            See Specification.
        key_dir (str): Directory containing a `.env` file, to extract the
            `GOOGLE_API_KEY` variable from, if it is not already in the environment.
        terms_per_batch (int): Maximum terms to include in each collection batch.
            Theoretically 30 is the API's max, but more than 1 seems to not work.
        wait_time (float): Seconds to wait between each batch.
        version (str): Version of the service API.

    Specification:
        To process in batches, search terms and locations must be specified in separate
        files (`terms.txt` and `locations.txt`), stored in the `scope_dir` directory.
        These should contain 1 term / location code per line.

    Collection Process:
        Initializing this class retrieves the Google API service, stores the
        developer key, and points to the scope directory.

        The `process_batches()` method reads in the terms and locations,
        and collects them in batches over the specified time frame.

        Results from each batch are stored in the `batches` property,
        which can be pulled from in case the `process_batches` process does not complete
        (such as if the daily rate limit is reached).

        The `collect()` method collects a single batch, and
        can be used on its own.

    Examples:
        ```python
        from gtrends_collection import Collector

        # initialize the collector
        collector = Collector()
        ```
    """

    # time to wait between requests
    _regular_wait_time = 0.1
    # time to wait after a `rateLimitExceeded` error
    _fallback_wait_time = 2
    batches: ClassVar[List[DataFrame]] = []

    scope_dir = "scope"
    max_terms = 1

    def __init__(
        self,
        scope_dir: str = "scope",
        key_dir: str = ".",
        terms_per_batch: int = 1,
        wait_time: float = 0.1,
        version: str = "v1beta",
    ):
        self._regular_wait_time = wait_time
        self.scope_dir = scope_dir
        self.max_terms = terms_per_batch

        key = getenv("GOOGLE_API_KEY")
        if not key and isfile(f"{key_dir}/.env"):
            with open(f"{key_dir}/.env", encoding="utf-8") as content:
                for pair in content.read().split("\n"):
                    name, value = pair.split("=")
                    if name.startswith("GOOGLE_API_KEY"):
                        key = value.strip()
                        break
        if not key:
            msg = "no API key found (GOOGLE_API_KEY environment variable)"
            raise RuntimeError(msg)

        self.service = discovery.build(
            "trends",
            version,
            discoveryServiceUrl=f"https://trends.googleapis.com/$discovery/rest?version={version}",
            developerKey=key,
        )

    def process_batches(
        self,
        start: Union[str, None] = None,
        end: Union[str, None] = None,
        resolution: str = "week",
        override_terms: Union[List[str], None] = None,
        override_location: Union[List[str], None] = None,
    ) -> DataFrame:
        """
        Processes collection batches from scope.

        Args:
            start (str | None): First date to collect from; `YYYY-MM-DD`.
            end (str | None): Last date to collect from; `YYYY-MM-DD`.
            resolution (str): Collection resolution; `day`, `week`, `month`, or `year`.
            override_terms (str): List of terms to collect instead of those in scope.
                Useful for changing collection order or filling out select terms.
            override_location (str): List of locations to collect from instead of those in scope.

        Examples:
            ```python
            # collect across all scope-defined terms and locations in 2024
            data = collector.process_batches("2024-01-01", "2024-12-31")
            ```

        Returns:
            A `pandas.DataFrame` of the combined results.
        """

        params: Dict[str, Union[List[str], str]] = {"timelineResolution": resolution}
        if start:
            params["time_startDate"] = start
        if end:
            params["time_endDate"] = end

        terms = override_terms if override_terms else read_scope(self.scope_dir, "terms")
        locations = override_location if override_location else read_scope(self.scope_dir, "locations")
        locations = {loc if len(loc) < 9 else loc.split("-")[2] for loc in locations}

        for term_set in range(0, len(terms), self.max_terms):
            for location in locations:
                batch_params = {
                    "terms": terms[term_set : (term_set + self.max_terms)],
                    **params,
                }
                batch_params[_location_type(location)] = location
                batch = self.collect(location, batch_params)
                self.batches.append(batch)
                sleep(self._regular_wait_time)

        data = concat(self.batches)
        return data

    def collect(
        self,
        location: str,
        params: Dict[str, Union[List[str], str]],
    ) -> DataFrame:
        """
        Collect a single batch.

        Args:
            location (str): Country (e.g., `US`), region (state; e.g., `US-AL`),
                or DMA (metro area; e.g., `US-AL-630` or `630`) code.
            params (dict[str, list[str] | str]): A dictionary with the following entries:

                * `terms` (list[str]): List of terms to collect.
                * `timelineResolution` (str): Collection resolution; `day`, `week`, `month`, or `year`.
                * `time_startDate` (str): First date to collect from; `YYYY-MM-DD`.
                * `time_endDate` (str): First date to collect from; `YYYY-MM-DD`.

        Examples:
            ```python
            # collect a small, custom sample
            data = collector.collect(
                "US-NY",
                {
                    "terms": ["cough", "/m/01b_21"],
                    "timelineResolution": "month",
                    "time_startDate": "2014-01-01",
                    "time_endDate": "2024-01-01",
                },
            )
            ```

        Returns:
            A `pandas.DataFrame` of the prepared results, with these columns:

                * `value`: Number indicating search volume.
                * `date`: Date the searches were recorded on.
                * `location`: Location code in which searches were recorded from.
                * `term`: The search term.
                * `retrieved`: Date retrived from the API.
        """

        try:
            # pylint: disable=E1101
            response = self.service.getTimelinesForHealth(**params).execute()
        except errors.HttpError as e:
            if e.status_code == 429:
                sleep(self._fallback_wait_time)
                return self.collect(location, params)
            raise e
        today = (datetime.datetime.now(datetime.timezone.utc)).strftime("%Y-%m-%d")
        data = []
        for line in response["lines"]:
            points = json_normalize(line["points"])
            points["date"] = to_datetime(points["date"], format="mixed").dt.strftime("%Y-%m-%d")
            points["location"] = location
            points["term"] = line["term"]
            points["retrieved"] = today
            data.append(points)
        return concat(data)


def _location_type(location: str):
    return "geoRestriction_" + ({2: "country", 5: "region", 3: "dma"}[len(location)])

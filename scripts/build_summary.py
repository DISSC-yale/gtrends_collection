"""Builds metadata."""

import datetime
from typing import List

import pandas
from pyarrow.dataset import dataset

from gtrends_collection import Collector

if __name__ == "__main__":
    data = dataset("data").to_table().to_pandas()

    observations = pandas.DataFrame(index=data["location"].unique())

    dates: List[pandas.DataFrame] = []
    summaries: List[pandas.DataFrame] = []

    for term, term_data in data.groupby("term"):
        date_range = term_data["date"].agg(["min", "max"])
        date_range.name = term
        dates.append(date_range)

        location_coverage = term_data["location"].value_counts()
        location_coverage.name = term
        observations = observations.join(location_coverage)

        summary = term_data["value"].agg(["min", "mean", "std", "max"])
        summary.name = term
        summaries.append(summary)

    collector = Collector()
    observations.index = collector.full_metro_area_codes(observations.index)

    with open("docs_source/Data.md", "w", encoding="utf-8") as out:
        out.writelines(
            [
                "Summaries of the data collected as of "
                + datetime.datetime.now(datetime.timezone.utc).strftime("%I:%M:%S %p UTC on %Y-%m-%d")
                + "\n\n## Dates\n\n",
                pandas.concat(dates, axis=1).T.to_markdown(),
                "\n\n## Values\n\n",
                pandas.concat(summaries, axis=1).T.to_markdown(),
                "\n\n## Observations By Location\n\n",
                observations.to_markdown(),
            ]
        )

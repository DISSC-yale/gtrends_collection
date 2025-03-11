"""Builds metadata."""

import datetime
from os import makedirs

from pandas import Index
from pyarrow.dataset import dataset

from gtrends_collection import Collector, full_metro_area_codes, full_term_names

if __name__ == "__main__":
    makedirs("summaries", exist_ok=True)
    data = dataset("data").to_table().to_pandas()

    observations = (
        data.groupby(["location", "term"])["value"]
        .agg("count")
        .reset_index()
        .pivot(columns="term", index="location", values="value")
    )
    collector = Collector()
    observations.index = full_metro_area_codes("scope", observations.index)
    observations.to_csv("summaries/observations.csv")

    means = (
        data.groupby(["location", "term"])["value"]
        .agg("mean")
        .reset_index()
        .pivot(columns="term", index="location", values="value")
    )
    means.index = full_metro_area_codes("scope", means.index)
    means.to_csv("summaries/means.csv")

    dates = data.groupby("term")["date"].agg(["min", "max"])
    dates.index = Index(full_term_names("scope", dates.index), name="term")
    summaries = data.groupby("term")["value"].agg(["min", "mean", "std", "max"])
    summaries.index = Index(full_term_names("scope", summaries.index), name="term")

    summaries_url = "https://github.com/DISSC-yale/gtrends_collection/blob/main/summaries/"
    with open("docs_source/Data.md", "w", encoding="utf-8") as out:
        out.writelines(
            [
                "Summaries of the data collected as of "
                + datetime.datetime.now(datetime.timezone.utc).strftime("%I:%M:%S %p UTC on %Y-%m-%d")
                + f"\n\n## Locations\n\n* [Observations]({summaries_url}observations.csv)"
                + f"\n* [Means]({summaries_url}means.csv)"
                + "\n\n## Dates\n\n",
                dates.to_markdown(),
                "\n\n## Values\n\n",
                summaries.to_markdown(floatfmt=".2f"),
                "\n",
            ]
        )

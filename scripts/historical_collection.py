"""Collected trends over their complete histories."""

if __name__ == "__main__":
    import pyarrow.dataset
    from apiclient import errors
    from pandas import concat

    from gtrends_collection import Collector, write_to_dataset

    terms = (
        pyarrow.dataset.dataset("data")
        .scanner(["term"])
        .to_table()["term"]
        .to_pandas()
        .value_counts()
        .sort_values()
        .index
    )

    collector = Collector()
    try:
        collector.process_batches(override_terms=terms)
    except errors.HttpError as e:
        print(e)
    if collector.batches:
        write_to_dataset(concat(collector.batches))

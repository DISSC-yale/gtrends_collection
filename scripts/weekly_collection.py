"""Collected trends from the last week."""

if __name__ == "__main__":
    import datetime

    from apiclient import errors
    from pandas import concat

    from gtrends_collection import Collector, write_to_dataset

    collector = Collector()
    try:
        collector.process_batches(
            (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(7)).strftime("%Y-%m-%d")
        )
    except errors.HttpError as e:
        print(e)
    if collector.batches:
        write_to_dataset(concat(collector.batches))

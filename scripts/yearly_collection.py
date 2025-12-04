"""Collected trends over their complete histories."""

if __name__ == "__main__":
    from apiclient import errors
    from pandas import concat

    from gtrends_collection import Collector, write_to_dataset

    collector = Collector()
    try:
        collector.process_batches(resolution="year")
    except errors.HttpError as e:
        print(e)
    if collector.batches:
        write_to_dataset(concat(collector.batches), "data_yearly")

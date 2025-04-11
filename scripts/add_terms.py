"""Adds terms to scope and performs a historical collection of them."""

import argparse
import re

from apiclient import errors
from pandas import concat

from gtrends_collection import Collector, read_scope, write_to_dataset

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("terms", help="A comma-separated string of terms to be added.")
    terms = re.split("\\s*,\\s*", parser.parse_args().terms)
    if not terms:
        msg = 'No terms passed; include them in the call, e.g., `python scripts/add_terms.py "term, another term"`.'
        raise RuntimeError(msg)

    existing_terms = read_scope("scope", "terms")
    for term in terms:
        if term not in existing_terms:
            existing_terms.append(term)
    with open("scope/terms.txt", "w", encoding="utf-8") as file:
        file.write("\n".join(existing_terms))

    collector = Collector()
    try:
        collector.process_batches(override_terms=terms)
    except errors.HttpError as e:
        print(e)
    if collector.batches:
        write_to_dataset(concat(collector.batches))

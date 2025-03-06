"""Write and manage trends dataset."""

from glob import glob
from math import ceil
from os import listdir, makedirs, unlink
from time import time
from urllib.parse import quote_plus

import pyarrow
import pyarrow.dataset
import pyarrow.parquet
from pandas import DataFrame

gtrends_schema = pyarrow.schema(
    [
        pyarrow.field("value", pyarrow.float64()),
        pyarrow.field("date", pyarrow.string()),
        pyarrow.field("location", pyarrow.string()),
        pyarrow.field("term", pyarrow.string()),
    ]
)


def write_to_dataset(data: DataFrame, data_dir="data", defragment=True):
    """
    Write term fragments to a Parquet dataset.

    Args:
      data (DataFrame): Collection results.
      data_dir (str): Directory of the Parquet dataset.
      defragment (bool): If `True`, defragments the dataset after writing new fragments.
    """
    for term, group in data.groupby("term"):
        encoded_term = quote_plus(term)
        part_dir = f"{data_dir}/term={encoded_term}/"
        makedirs(part_dir, exist_ok=True)
        pyarrow.Table.from_pandas(group, schema=gtrends_schema)
        pyarrow.parquet.write_table(
            pyarrow.Table.from_pandas(group, schema=gtrends_schema),
            f"{part_dir}fragment-{ceil(time())!s}-0.parquet",
            compression="gzip",
        )
    if defragment:
        defragment_dataset(data_dir)


def defragment_dataset(data_dir="data"):
    """
    Defragments the dataset partitions.

    Args:
      data_dir (str): directory of the Parquet dataset.
    """
    for part_name in listdir(data_dir):
        part_dir = f"{data_dir}/{part_name}/"
        part = pyarrow.dataset.dataset(
            part_dir, gtrends_schema, format="parquet", exclude_invalid_files=True
        ).to_table()
        pyarrow.parquet.write_table(part, f"{part_dir}part-0.parquet", compression="gzip")
        for fragment in glob(f"{part_dir}fragment*.parquet"):
            unlink(fragment)

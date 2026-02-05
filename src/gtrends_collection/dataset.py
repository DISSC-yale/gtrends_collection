"""Write and manage trends dataset."""

import hashlib
import json
from glob import glob
from math import ceil
from os import listdir, makedirs, unlink
from os.path import abspath, dirname, isfile
from time import time
from urllib.parse import quote_plus
from typing import Dict, Union

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
        pyarrow.field("retrieved", pyarrow.string()),
    ]
)


def write_to_dataset(data: DataFrame, data_dir: str = "data", defragment: bool = True):
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
        pyarrow.parquet.write_table(
            pyarrow.Table.from_pandas(group, schema=gtrends_schema),
            f"{part_dir}fragment-{ceil(time())!s}-0.parquet",
            compression="gzip",
        )
    if defragment:
        defragment_dataset(data_dir)
    update_status(data_dir)


def defragment_dataset(data_dir: str = "data"):
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


def update_status(data_dir: str, log_file: Union[str, None] = None):
    """
    Records state of data files.

    Args:
      data_dir (str): directory of a Parquet dataset.
      log_file (str): path to the log file.
    """
    if log_file is None:
        log_file = dirname(abspath(data_dir)) + "/status.json"
    print(log_file)
    files = glob(f"{data_dir}/**/*.parquet")
    if isfile(log_file):
        with open(log_file, "r", encoding="utf-8") as file:
            state = json.load(file)
    else:
        state: Dict[str, str] = {}
    for file in files:
        with open(file, "rb") as file_buffer:
            content = file_buffer.read()
            state[file.replace("\\", "/")] = hashlib.md5(content).hexdigest()
    with open(log_file, "w", encoding="utf-8") as file:
        json.dump(state, file, indent=2)

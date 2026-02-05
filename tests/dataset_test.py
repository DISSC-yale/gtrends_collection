import json
from os.path import isfile
from tempfile import TemporaryDirectory

from pandas import DataFrame
from pyarrow.dataset import dataset

from gtrends_collection import write_to_dataset


def test_dataset():
    with TemporaryDirectory() as tempdir:
        data_dir = tempdir + "/data"
        data = DataFrame(
            {
                "term": ["a", "b"],
                "value": [0] * 2,
                "date": ["2004-01-01"] * 2,
                "location": ["US"] * 2,
                "retrieved": ["2025-03-07"] * 2,
            }
        )
        write_to_dataset(data, data_dir)
        assert dataset(data_dir).scanner(["term"]).to_table()["term"].to_pylist() == data["term"].to_list()

        log_file = tempdir + "/status.json"
        assert isfile(log_file)
        with open(log_file, "r", encoding="utf-8") as file:
            state = json.load(file)
        assert data_dir.replace("\\", "/") + "/term=b/part-0.parquet" in state

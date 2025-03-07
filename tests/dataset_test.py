from tempfile import TemporaryDirectory

from pandas import DataFrame
from pyarrow.dataset import dataset

from gtrends_collection import write_to_dataset


def test_dataset():
    with TemporaryDirectory() as tempdir:
        data = DataFrame(
            {
                "term": ["a", "b"],
                "value": [0] * 2,
                "date": ["2004-01-01"] * 2,
                "location": ["US"] * 2,
                "retrieved": ["2025-03-07"] * 2,
            }
        )
        write_to_dataset(data, tempdir)
        assert dataset(tempdir).scanner(["term"]).to_table()["term"].to_pylist() == data["term"].to_list()

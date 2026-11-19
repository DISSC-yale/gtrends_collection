# Google Trends Collection Framework

This is in part a simple Python package to handle collection from the Google Trends beta research API,
and a minimal framework to organize historical and continuous collection.

## Data

A selection of data are collected in the `data` directory (weekly data updated weekly)
and in the `data_yearly` directory (yearly data updated weekly).

The selection is defined by the files in the `scope` directory.

### Local Use

To work with the data locally, you can clone this repository:

```sh
git clone --depth=1 https://github.com/DISSC-yale/gtrends_collection.git
```

Then load the data in Python:

```python
from pyarrow.dataset import dataset

data = dataset("gtrends_collection/data").to_table().to_pandas()
```

or R:

```R
library(arrow)

data <- open_dataset("gtrends_collection/data") |> dplyr::collect()
```

### Collection

The `scripts/historical_collection.py` script is used to collect full histories
based on the scope files:

```sh
python scripts/historical_collection.py
```

The `scripts/weekly_collection.py` script is used by the GitHub Actions workflow
to add new data each week. The `scripts/yearly_collection.py` script is used
by another workflow to add yearly data each month.

The `scripts/add_terms.py` script can be used to add and collect new terms:

```sh
python scripts/add_terms.py "term, another term"
```

Any topic or category terms should also be manually added to `scope/term_map.csv`.

#### Authentication

A developer key is required to collect from the beta API.

This can either be set to the `GOOGLE_API_KEY` environment variable,
or stored in an `.env` file:

```sh
GOOGLE_API_KEY=AlphanumericKey
```

## Rebuilding

### Scripts

Some scripts are used to build parts of the repository.

#### Summary

The `scripts/build_summary.py` script creates `docs_source/Data.md`:

```sh
python scripts/build_summary.py
```

The `scripts/build_summary_yearly.py` script creates `docs_source/Data_Yearly.md`:

#### Metadata

The `scripts/build_metadata.py` script creates `scope/locations.txt`:

```sh
python scripts/build_metadata.py
```

### Hatch

[Hatch](https://hatch.pypa.io) is used to manage package testing:

```sh
hatch run test
```

And building of the documentation site:

```sh
hatch run docs:build
```

## Legal Disclaimer

Data are provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and noninfringement. In no event shall the authors, contributors, or copyright holders be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the data or the use or other dealings in the data.

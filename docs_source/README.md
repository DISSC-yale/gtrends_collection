# Google Trends Collection Framework

This is in part a simple Python package to handle collection from the Google Trends beta research API,
and a minimal framework to organize historical and continuous collection.

## Data

A selection of data are collected in the `data` directory, and are updated weekly.

The selection is defined by the files in the `scope` directory.

The `scipts/build_metadata.py` script was used to create `scope/locations.txt`:

```sh
python scripts/build_metadata.py
```

## Authentication

A developer key is required to access the beta API.

This can either be set to the `GOOGLE_API_KEY` environment variable,
or stored in an `.env` file:

```sh
GOOGLE_API_KEY=AlphanumericKey
```

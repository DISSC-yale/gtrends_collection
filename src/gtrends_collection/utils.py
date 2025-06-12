"""Utility function to interact with framework resources and trends data."""

from os.path import isfile
from typing import Dict, List

import pandas


def read_scope(scope_dir: str, which: str) -> List[str]:
    """
    Reads in a scope file.

    Args:
        scope_dir (str): Directory containing scope files.
        which (str): Name of the file to be read in (e.g., `locations`).

    Examples:
        ```python
        terms = read_scope("./scope", "terms")
        ```

    Returns:
        A list of terms or locations.
    """
    with open(f"{scope_dir}/{which}.txt", encoding="utf-8") as content:
        locations = [code.strip() for code in content.readlines()]
    return locations


def full_term_names(scope_dir: str, terms: List[str], include_id: bool = True) -> List[str]:
    """
    Converts topic and category IDs to their full names, based on `scope_dir/term_map.csv`.

    Args:
        terms (List[str]): Terms to be converted.

    Examples:
        ```python
        full_term_names("./scope", ["/m/0cycc", "/g/11hy9m64ws"])
        ```

    Returns:
        A version of `terns` with any matching terms converted.
    """
    map_file = f"{scope_dir}/term_map.csv"
    if not isfile(map_file):
        return terms
    term_map = pandas.read_csv(map_file, index_col="id")["name"].to_dict()
    return [term_map.get(term, term) + (f" ({term})" if include_id and term.startswith("/") else "") for term in terms]


def full_metro_area_codes(scope_dir: str, locations: List[str]) -> List[str]:
    """
    Adds country and state codes to metro area codes (e.g., `630` becomes `US-AL-630`),
    based on `scope_dir/locations.txt`.

    Args:
        locations (List[str]): Locations to potentially prepend full location codes to.

    Examples:
        ```python
        full_metro_area_codes("./scope", ["630", "743"])
        ```

    Returns:
        A version of `locations` with any matching locations expanded.
    """
    location_map: Dict[str, str] = {}
    for location in read_scope(scope_dir, "locations"):
        if len(location) == 9:
            location_parts = location.split("-")
            location_map[location_parts[2]] = location
    return [location_map.get(loc, loc) for loc in locations]

from gtrends_collection import full_metro_area_codes, full_term_names


def test_term_conversion():
    names = ["rsv", "Influenza (/m/0cycc)", "Respiratory syncytial virus (/g/11hy9m64ws)"]
    terms = ["rsv", "/m/0cycc", "/g/11hy9m64ws"]
    assert full_term_names("scope", terms) == names


def test_location_conversion():
    full = ["US-AL", "US-AL-630", "US-AK-743"]
    partial = ["US-AL", "630", "743"]
    assert full_metro_area_codes("scope", partial) == full

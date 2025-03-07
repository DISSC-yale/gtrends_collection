import datetime
from typing import List, Union
from unittest.mock import patch

from gtrends_collection import Collector


# pylint: disable=C0103
class Build:
    """Minimal representation of the service builder."""

    def __init__(
        self,
        service: Union[str, None] = None,
        version: Union[str, None] = None,
        discoveryServiceUrl: Union[str, None] = None,
        developerKey: Union[str, None] = None,
    ):
        self.service = service
        self.version = version
        self.discoveryServiceUrl = discoveryServiceUrl
        self.versdeveloperKeyion = developerKey

    def getTimelinesForHealth(self, **kwargs):

        return Service(**kwargs)


class Service:
    """Minimal representation of trends service API."""

    def __init__(
        self,
        terms: List[str],
        timelineResolution: str,
        time_startDate="2004-01-01",
        time_endDate=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
        geoRestriction_state: Union[str, None] = None,
        geoRestriction_region: Union[str, None] = None,
        geoRestriction_dma: Union[str, None] = None,
    ):
        self.terms = terms
        self.timelineResolution = timelineResolution
        self.time_startDate = time_startDate
        self.time_endDate = time_endDate
        self.geoRestriction_state = geoRestriction_state
        self.geoRestriction_region = geoRestriction_region
        self.geoRestriction_dma = geoRestriction_dma

    def execute(self):
        """GET values."""
        return {
            "lines": [
                {
                    "term": self.terms[0],
                    "points": [{"date": self.time_startDate, "value": 0.0}, {"date": self.time_endDate, "value": 0.0}],
                }
            ]
        }


@patch("apiclient.discovery.build", Build)
def test_collector():
    collector = Collector(wait_time=0)
    data = collector.process_batches()
    assert data.columns.to_list() == ["date", "value", "location", "term", "retrieved"]


def test_code_conversion():
    collector = Collector()
    assert collector.full_metro_area_codes(["630"]) == ["US-AL-630"]

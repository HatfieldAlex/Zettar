import unittest
from unittest.mock import patch

from django.test import SimpleTestCase

from data_pipeline.resources.data_resource_instances import utils
from data_pipeline.resources.data_resource_instances.utils import normalise_raw_name_entry


class NormaliseRawNameEntryTests(SimpleTestCase):
    """
    Tests for the `normalise_raw_name_entry` function using example substation
    names from various DNOs (Distribution Network Operators).

    These are not exhaustive but represent common formatting patterns used by:
    - NGED (National Grid Electricity Distribution)
    - UKPN (UK Power Networks)
    - NPg (Northern Powergrid)
    """
    def test_nged(self):
        self.assertEqual(
            normalise_raw_name_entry("Groby Road 33 11kv S Stn"),
            "Groby Road"
        )
    def test_ukpn(self):
        self.assertEqual(
            normalise_raw_name_entry("CLIFF QUAY GRID 132KV"),
            "Cliff Quay Grid"
        )
    def test_np(self):
        self.assertEqual(
            normalise_raw_name_entry("AUSTERFIELD 66/33/11KV 925"),
            "Austerfield"
        )

from django.test import TestCase
from django.contrib.gis.geos import Point
from .models.substations import GSPSubstation, BSPSubstation, PrimarySubstation
from .utils.view_helpers import find_nearest_substation_obj


class FindNearestSubstationFuncTestCase(TestCase):
    """Tests the find_nearest_substation_obj function"""

    def setUp(self):
        """Create test substations and initialize common test data."""
        self.substation_1 = PrimarySubstation.objects.create(
            name="Primary 1",
            geolocation=Point(
                -3.5924521424325064, 50.72095863371211, srid=4326
            ),
        )
        self.substation_2 = PrimarySubstation.objects.create(
            name="Primary 2",
            geolocation=Point(
                -3.251875990277052, 50.81476274479066, srid=4326
            ),
        )
        self.substation_3 = BSPSubstation.objects.create(
            name="BSP 1",
            geolocation=Point(-3.537520504988079, 50.7070457296884, srid=4326),
        )
        self.substation_type = "primary"
        self.geolocation = Point(
            -3.518981092895627, 50.732042515778836, srid=4326
        )

    def test_expected_closest_location(self):
        """Should return the closest primary substation."""
        self.assertEqual(
            self.substation_1,
            find_nearest_substation_obj(
                self.geolocation, self.substation_type
            ),
        )

    def test_invalid_substation_type_raises_error(self):
        """Should raise ValueError for an invalid substation type."""
        with self.assertRaises(ValueError):
            find_nearest_substation_obj(
                self.geolocation, "not primary, bsp, or gsp"
            )

    def test_invalid_location_raises_type_error(self):
        """Should raise TypeError when location is not a Point."""
        with self.assertRaises(TypeError):
            find_nearest_substation_obj("not in Point format", "primary")

    def test_no_match_found(self):
        """Should return None if no substation matches the type."""
        self.assertIsNone(find_nearest_substation_obj(self.geolocation, "gsp"))

from django.test import TestCase
from django.contrib.gis.geos import Point
from .models import Substation, NewConnection, ConnectionStatus
from .constants import APPLICATION_STATUS_FIELDS
from .utils.view_helpers import find_nearest_substation_obj, get_substation_object_connection_data
from decimal import Decimal



class FindNearestSubstationFuncTestCase(TestCase):
    """Test cases for the 'find_nearest_substation_obj' function.

    Includes validation of correct nearest substation lookup,
    behavior with invalid input, and no match scenarios.
    """

    def setUp(self):
        """Create test substations and initialize common test data."""
        self.substation_1 = Substation.objects.create(
            name="Primary 1",
            type="primary",
            geolocation=Point(
                -3.5924521424325064, 50.72095863371211, srid=4326
            ),
        )
        self.substation_2 = Substation.objects.create(
            name="Primary 2",
            type="primary",
            geolocation=Point(
                -3.251875990277052, 50.81476274479066, srid=4326
            ),
        )
        self.substation_3 = Substation.objects.create(
            name="BSP 1",
            type="bsp",
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


# class GetSubstationObjectConnectionDataFuncTestCase(TestCase):
#     """Tests for 'get_substation_object_connection_data'.

#     Verifies total demand/generation counts, capacity rounding (ROUND_DOWN),
#     status-bucket aggregation for statuses in APPLICATION_STATUS_FIELDS,
#     and handling of None values and empty related sets.
#     """

#     def setUp(self):
#         """Create a substation and a few connection/status records."""
#         self.substation = Substation.objects.create(
#             name="Alpha Primary",
#             type="primary",
#         )

#         # Pick two known-valid statuses directly from APPLICATION_STATUS_FIELDS
#         # so the test stays aligned with your codebase.
#         self.status_a_value = APPLICATION_STATUS_FIELDS[0]
#         # If there is only one status configured, reuse it for the second;
#         # otherwise pick the second one.
#         self.status_b_value = (
#             APPLICATION_STATUS_FIELDS[1]
#             if len(APPLICATION_STATUS_FIELDS) > 1
#             else APPLICATION_STATUS_FIELDS[0]
#         )

#         self.status_a = ConnectionStatus.objects.create(status=self.status_a_value)
#         self.status_b = ConnectionStatus.objects.create(status=self.status_b_value)

#         # A status that should not be counted in status-bucket sums
#         self.status_other = ConnectionStatus.objects.create(status="__not_in_application_fields__")

#         # Connections that should contribute to totals and status buckets
#         NewConnection.objects.create(
#             substation=self.substation,
#             demand_count=2,
#             total_demand_capacity_mw=Decimal("10.9"),
#             generation_count=1,
#             total_generation_capacity_mw=Decimal("5.6"),
#             connection_status=self.status_a,
#         )
#         NewConnection.objects.create(
#             substation=self.substation,
#             demand_count=3,
#             total_demand_capacity_mw=Decimal("1.1"),
#             generation_count=4,
#             total_generation_capacity_mw=Decimal("2.4"),
#             connection_status=self.status_b,
#         )

#         # A connection with Nones should be treated as zeros and not break anything.
#         NewConnection.objects.create(
#             substation=self.substation,
#             demand_count=None,
#             total_demand_capacity_mw=None,
#             generation_count=None,
#             total_generation_capacity_mw=None,
#             connection_status=self.status_other,
#         )

#     def test_aggregate_totals_and_status_buckets(self):
#         """Should aggregate counts/capacities and bucket by valid statuses, rounding down capacities."""
#         data = get_substation_object_connection_data(self.substation)

#         # Substation identity
#         self.assertEqual(data["nearest_substation_name"], "Alpha Primary")
#         self.assertEqual(data["nearest_substation_type"], "primary")

#         # Totals (2+3 from first two; None treated as 0)
#         self.assertEqual(data["demand_application_sum"], 5)
#         self.assertEqual(data["generation_application_sum"], 5)

#         # Capacities: (10.9 + 1.1) -> 12.0 -> Decimal('12'); (5.6 + 2.4) -> 8.0 -> Decimal('8')
#         self.assertEqual(data["demand_capacity_mw"], Decimal("12"))
#         self.assertEqual(data["generation_capacity_mw"], Decimal("8"))

#         # Status buckets only for statuses in APPLICATION_STATUS_FIELDS
#         self.assertEqual(
#             data[f"demand_{self.status_a_value}_status_sum"], 2
#         )
#         self.assertEqual(
#             data[f"generation_{self.status_a_value}_status_sum"], 1
#         )
#         self.assertEqual(
#             data[f"demand_{self.status_b_value}_status_sum"], 3
#         )
#         self.assertEqual(
#             data[f"generation_{self.status_b_value}_status_sum"], 4
#         )

#         # No buckets for a status not in APPLICATION_STATUS_FIELDS
#         self.assertNotIn(f"demand_{self.status_other.status}_status_sum", data)
#         self.assertNotIn(f"generation_{self.status_other.status}_status_sum", data)

#     def test_no_connections_returns_zeros(self):
#         """Should return zeros and Decimal('0') capacities when no related connections exist."""
#         empty_substation = Substation.objects.create(
#             name="Empty BSP",
#             type="bsp",
#         )
#         data = get_substation_object_connection_data(empty_substation)

#         self.assertEqual(data["nearest_substation_name"], "Empty BSP")
#         self.assertEqual(data["nearest_substation_type"], "bsp")
#         self.assertEqual(data.get("demand_application_sum", 0), 0)
#         self.assertEqual(data.get("generation_application_sum", 0), 0)
#         self.assertEqual(data.get("demand_capacity_mw", Decimal("0")), Decimal("0"))
#         self.assertEqual(data.get("generation_capacity_mw", Decimal("0")), Decimal("0"))

from django.test import SimpleTest
from unittest.mock import patch
from location_input.utils import get_osrm_driving_distance

class OSRMTest(SimpleTest):

    @patch('location_input.requests.get')
    def test_osrm_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'code': 'Ok',
            'routes': [{'distance': 12345.56}]
        }

        coord1 = (-122.42, 37.78)
        coord2 = (-122.45, 37.76)

        result = get_osrm_driving_distance(coord1, coord2)
        self.assertEqual(result, 1234.56)

    @patch("myapp.utils.requests.get")
    def test_osrm_error_status(self, mock_get):
        # Simulate API returning error status code
        mock_get.return_value.status_code = 400
        mock_get.return_value.json.return_value = {
            "code": "InvalidQuery",
            "message": "Bad coordinates"
        }

        result = get_osrm_driving_distance((0, 0), (0, 0))
        self.assertIsNone(result)

    @patch("myapp.utils.requests.get")
    def test_osrm_exception(self, mock_get):
        # Simulate a network error
        mock_get.side_effect = Exception("Network error")

        result = get_osrm_driving_distance((0, 0), (0, 0))
        self.assertIsNone(result)

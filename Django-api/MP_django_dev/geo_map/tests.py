from django.test import TestCase

# Import the methods you wan to test
from geo_map.processing import compute_map_data

# Pandas import for test cases
import pandas as pd

# Create your tests here.


class ComputeMapDataTestCase(TestCase):
    def setUp(self):
        df_test_empty = pd.DataFrame([])
        df_test_no_duplicates = pd.DataFrame(
            [[1, 2, 3, 4, 5], [1, 2, 3, 4, 5]]
        )
        df_test_duplicates = pd.DataFrame(
            [[1, 2, 2, 4, 4, 4], [1, 2, 2, 4, 4, 4]]
        )

    def test_empty(self):
        result = compute_map_data(df_test_empty)
        self.assertEqual(result, None)

    def test_no_duplicates(self):
        result = compute_map_data(df_test_empty)
        self.assertEqual(result, None)

    def test_duplicates(self):
        result = compute_map_data(df_test_empty)
        self.assertEqual(result, None)

#!/usr/bin/env python3
"""Unit tests for utils module."""

import unittest
from parameterized import parameterized
from utils import access_nested_map

class TestAccessNestedMap(unittest.TestCase):
    def access_nested_map(self, nested_map, path, expected):
        """Access nested map with key path.
        Parameters
        ----------
        nested_map: Mapping
            A nested map"""
    @parameterized.expand([
        ({}, ("a",), "'a"),
        ({"a": 1}, ("a", "b"), {"'b'"}),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        with self.assertRaises(KeyError) as cm:
            access_nested_map(nested_map, path)
        self.assertEqual(str(cm.exception), expected)

if __name__ == "__main__":
    unittest.main()
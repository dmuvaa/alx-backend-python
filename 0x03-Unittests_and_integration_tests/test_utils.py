#!/usr/bin/env python3
"""Unit tests for utils module."""

import unittest
from parameterized import parameterized
from utils import access_nested_map

class TestAccessNestedMap(unittest.TestCase):
    """TestAccessNestedMap class to test access_nested_map function"""
    @parameterized.expand([
        ({}, ("a",), "'a"),
        ({"a": 1}, ("a", "b"), {"'b'"}),
    ])
    def test_access_nested_map(self, nested_map, path, expected_msg):
        with self.assertRaises(KeyError) as cm:
            access_nested_map(nested_map, path)
        self.assertEqual(str(cm.exception), expected_msg)

if __name__ == "__main__":
    unittest.main()
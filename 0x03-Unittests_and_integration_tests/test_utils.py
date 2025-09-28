#!/usr/bin/env python3
"""Unittests for utils."""

import unittest
from unittest.mock import patch, Mock

from parameterized import parameterized

from utils import access_nested_map, get_json, memoize


class TestAccessNestedMap(unittest.TestCase):
    """Tests for utils.access_nested_map."""

    @parameterized.expand([
        ({}, ("a",), "'a'"),
        ({"a": 1}, ("a", "b"), "'b'"),
    ])
    def test_access_nested_map_exception(self, nested_map, path, expected_msg):
        """
        Ensure KeyError (with expected message) 
        is raised for missing keys.
        """
        with self.assertRaises(KeyError) as cm:
            access_nested_map(nested_map, path)
        self.assertEqual(str(cm.exception), expected_msg)


class TestGetJson(unittest.TestCase):
    """Tests for utils.get_json."""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    def test_get_json(self, url, payload):
        """Patch requests.get and verify return value and call arguments."""
        mock_resp = Mock()
        mock_resp.json.return_value = payload
        with patch("utils.requests.get", return_value=mock_resp) as mock_get:
            response = get_json(url)
        self.assertEqual(response, payload)
        mock_get.assert_called_once_with(url)


class TestMemoize(unittest.TestCase):
    """Tests for utils.memoize decorator."""

    def test_memoize(self):
        """a_method should be called once; 
        a_property should return cached value."""
        class TestClass:
            """Helper class to exercise memoize."""

            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        with patch.object(
                TestClass,
                "a_method",
                return_value=42
        ) as mock_method:
            obj = TestClass()
            self.assertEqual(obj.a_property, 42)
            self.assertEqual(obj.a_property, 42)
            mock_method.assert_called_once()


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Unittests for client."""

import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Tests for GithubOrgClient class."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org, mock_get_json):
        payload = {"login": org, "id": 12345}
        mock_get_json.return_value = payload

        client = GithubOrgClient(org)
        self.assertEqual(client.org, payload)
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org}"
        )

    @parameterized.expand([
        ({"repos_url": "http://example.com/repos"}, "http://example.com/repos"),
        ({"repos_url": "http://holberton.io/repos"}, "http://holberton.io/repos"),
    ])
    def test_public_repos_url(self, org_payload, expected_url):
        with patch.object(
            GithubOrgClient,
            "org",
            new_callable=PropertyMock,
            return_value=org_payload,
        ):
            client = GithubOrgClient("anyorg")
            self.assertEqual(client._public_repos_url, expected_url)

    @parameterized.expand([
        (["repo1", "repo2", "repo3"], None,
         [{"name": "repo1"}, {"name": "repo2"}, {"name": "repo3"}]),
        (["repo1", "repo3"], "apache-2.0",
         [{"name": "repo1", "license": {"key": "apache-2.0"}},
          {"name": "repo2", "license": {"key": "mit"}},
          {"name": "repo3", "license": {"key": "apache-2.0"}}]),
    ])
    @patch("client.get_json")
    def test_public_repos(self, expected, license_key, api_payload, mock_gj):
        repos_url = "https://api.github.com/orgs/testorg/repos"
        mock_gj.return_value = api_payload

        with patch.object(
            GithubOrgClient,
            "_public_repos_url",
            new_callable=PropertyMock,
            return_value=repos_url,
        ) as mock_url:
            client = GithubOrgClient("testorg")
            result = client.public_repos(license=license_key)

        self.assertEqual(result, expected)
        mock_url.assert_called_once()
        mock_gj.assert_called_once_with(repos_url)


if __name__ == "__main__":
    unittest.main(verbosity=2)
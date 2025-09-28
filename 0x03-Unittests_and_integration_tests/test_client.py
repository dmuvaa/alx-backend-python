#!/usr/bin/env python3

"""Unittests for client."""

import unittest
from unittest.mock import patch, Mock
from client import GithubOrgClient
from parameterized import parameterized

class TestGithubOrgClient(unittest.TestCase):
    """Tests for GithubOrgClient class."""

    @parameterized.expand([
        ("google", {"login": "google"}),
        ("abc", {"login": "abc"}),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, org_payload, mock_get_json):
        """Test that the org method returns the correct payload."""
        mock_get_json.return_value = org_payload
        client = GithubOrgClient(org_name)
        self.assertEqual(client.org(), org_payload)
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    @parameterized.expand([
        ({"repos_url": "http://example.com/repos"}, "http://example.com/repos"),
        ({"repos_url": "http://holberton.io/repos"}, "http://holberton.io/repos"),
    ])
    @patch.object(GithubOrgClient, 'org', new_callable=property)
    def test_public_repos_url(self, org_payload, expected_url, mock_org):
        """Test that _public_repos_url returns the correct URL."""
        mock_org.return_value = org_payload
        client = GithubOrgClient("any_org")
        self.assertEqual(client._public_repos_url, expected_url)

    @parameterized.expand([
        (["repo1", "repo2", "repo3"], None,
         [{"name": "repo1"}, {"name": "repo2"}, {"name": "repo3"}]),
        (["repo1", "repo2"], "apache-2.0",
         [{"name": "repo1", "license": {"key": "apache-2.0"}},
          {"name": "repo2", "license": {"key": "mit"}},
          {"name": "repo3", "license": {"key": "apache-2.0"}}]),
    ])
    @patch.object(GithubOrgClient, 'repos_payload', new_callable=property)
    def test_public_repos(self, expected_repos, license_key,
                          mock_repos_payload):
        """Test that public_repos returns the correct list of repo names."""
        mock_repos_payload.return_value = [
            {"name": repo["name"], "license": repo.get("license")}
            for repo in expected_repos
        ]
        client = GithubOrgClient("any_org")
        self.assertEqual(client.public_repos(license=license_key), expected_repos)
        mock_repos_payload.assert_called_once()

if __name__ == "__main__":
    unittest.main()
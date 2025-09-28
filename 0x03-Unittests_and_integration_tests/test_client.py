#!/usr/bin/env python3

"""Unittests for client."""

import unittest
from unittest.mock import patch, Mock
from client import GithubOrgClient
from parameterized import parameterized

class TestGithubOrgClient(unittest.TestCase):
    """Tests for GithubOrgClient class."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org, mock_get_json):
        """org should return the payload from client.get_json; called once."""
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
    
    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """public_repos should return repo names and call deps once."""
        payload = [{"name": "alpha"}, {"name": "beta"}, {"name": "gamma"}]
        mock_get_json.return_value = payload

        url = "https://api.github.com/orgs/testorg/repos"
        with patch.object(
            GithubOrgClient,
            "_public_repos_url",
            new_callable=PropertyMock,
            return_value=url,
        ) as mock_url:
            client = GithubOrgClient("testorg")
            repos = client.public_repos()

        self.assertEqual(repos, ["alpha", "beta", "gamma"])
        mock_url.assert_called_once()
        mock_get_json.assert_called_once_with(url)

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
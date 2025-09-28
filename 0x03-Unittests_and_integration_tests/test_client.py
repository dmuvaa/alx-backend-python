#!/usr/bin/env python3
"""Unittests for client.GithubOrgClient."""

import unittest
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized, parameterized_class

from client import GithubOrgClient
from fixtures import (
    org_payload,
    repos_payload,
    expected_repos,
    apache2_repos,
)


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org, mock_get_json):
        """org returns payload from client.get_json; called once."""
        payload = {"login": org, "id": 42, "repos_url": f"url/{org}"}
        mock_get_json.return_value = payload

        client = GithubOrgClient(org)
        self.assertEqual(client.org, payload)

        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org}"
        )

    @parameterized.expand([
        ({"repos_url": "http://example.com/repos"}, "http://example.com/repos"),
        ({"repos_url": "http://holberton.io/repos"},
         "http://holberton.io/repos"),
    ])
    def test_public_repos_url(self, org_payload_param, expected_url):
        """_public_repos_url pulls repos_url from org payload."""
        with patch.object(
            GithubOrgClient,
            "org",
            new_callable=PropertyMock,
            return_value=org_payload_param,
        ):
            client = GithubOrgClient("anyorg")
            self.assertEqual(client._public_repos_url, expected_url)

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """
        public_repos returns repo names; mocks URL property and get_json.
        Both mocked elements should be called exactly once.
        """
        repos_url = "https://api.github.com/orgs/testorg/repos"
        payload = [{"name": "alpha"}, {"name": "beta"}, {"name": "gamma"}]
        mock_get_json.return_value = payload

        with patch.object(
            GithubOrgClient,
            "_public_repos_url",
            new_callable=PropertyMock,
            return_value=repos_url,
        ) as mock_url:
            client = GithubOrgClient("testorg")
            result = client.public_repos()

        self.assertEqual(result, ["alpha", "beta", "gamma"])
        mock_url.assert_called_once()
        mock_get_json.assert_called_once_with(repos_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """has_license returns True only when the repo's license key matches."""
        self.assertEqual(
            GithubOrgClient.has_license(repo, license_key),
            expected,
        )


@parameterized_class([{
    "org_payload": org_payload,
    "repos_payload": repos_payload,
    "expected_repos": expected_repos,
    "apache2_repos": apache2_repos,
}])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration tests for GithubOrgClient.public_repos.

    Only external HTTP (requests.get) is mocked; client/utils logic runs.
    """

    @classmethod
    def setUpClass(cls):
        """Start patcher for requests.get and wire fixture side effects."""
        cls.get_patcher = patch("requests.get")
        mock_get = cls.get_patcher.start()

        # Build URL -> payload mapping from fixtures
        org_login = cls.org_payload.get("login")
        org_url = GithubOrgClient.ORG_URL.format(org=org_login)
        repos_url = cls.org_payload.get("repos_url")

        def _json_for(url):
            if url == org_url:
                return cls.org_payload
            if url == repos_url:
                return cls.repos_payload
            # If unexpected URL shows up, make it obvious in failures
            raise AssertionError(f"Unexpected URL requested: {url}")

        def _side_effect(url, *args, **kwargs):
            m = Mock()
            m.json.return_value = _json_for(url)
            return m

        mock_get.side_effect = _side_effect

    @classmethod
    def tearDownClass(cls):
        """Stop the requests.get patcher."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Unfiltered repo names should match expected_repos fixture."""
        client = GithubOrgClient(self.org_payload["login"])
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Filtering by apache-2.0 should match apache2_repos fixture."""
        client = GithubOrgClient(self.org_payload["login"])
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
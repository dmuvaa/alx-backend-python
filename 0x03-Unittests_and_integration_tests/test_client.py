#!/usr/bin/env python3
"""Unittests for client.GithubOrgClient."""

import unittest
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized, parameterized_class

from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org, mock_get_json):
        """GithubOrgClient.org returns payload from client.get_json (called once)."""
        payload = {"login": org, "repos_url": f"https://api.github.com/orgs/{org}/repos"}
        mock_get_json.return_value = payload

        client = GithubOrgClient(org)
        self.assertEqual(client.org, payload)
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org}"
        )

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """
        public_repos returns repo names; mocks _public_repos_url and get_json.
        Both mocked objects should be called exactly once.
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
            self.assertEqual(client.public_repos(), ["alpha", "beta", "gamma"])

        mock_url.assert_called_once()
        mock_get_json.assert_called_once_with(repos_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """has_license returns True iff repo['license']['key'] == license_key."""
        self.assertEqual(
            GithubOrgClient.has_license(repo, license_key),
            expected,
        )


# Unpack the single tuple from TEST_PAYLOAD into class params
@parameterized_class([{
    "org_payload": TEST_PAYLOAD[0][0],
    "repos_payload": TEST_PAYLOAD[0][1],
    "expected_repos": TEST_PAYLOAD[0][2],
    "apache2_repos": TEST_PAYLOAD[0][3],
}])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration tests for GithubOrgClient.public_repos.

    Only the external HTTP (requests.get) is mocked. client/utils code runs.
    """

    @classmethod
    def setUpClass(cls):
        """Patch requests.get so .json() returns fixtures based on URL."""
        cls.get_patcher = patch("requests.get")
        mock_get = cls.get_patcher.start()

        # Fixture only gives repos_url; org login isn't included, but we know it's google.
        org_login = "google"
        org_url = GithubOrgClient.ORG_URL.format(org=org_login)
        repos_url = cls.org_payload["repos_url"]

        def _json_for(url):
            if url == org_url:
                # in real GitHub, org payload would include 'login'; add it here
                payload = dict(cls.org_payload)
                payload.setdefault("login", org_login)
                return payload
            if url == repos_url:
                return cls.repos_payload
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
        """Unfiltered names should equal expected_repos fixture."""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Filtering by apache-2.0 should equal apache2_repos fixture."""
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

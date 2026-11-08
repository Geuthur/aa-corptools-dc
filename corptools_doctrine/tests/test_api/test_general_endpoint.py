"""Tests for the general API endpoints (menu and user)."""

# Standard Library
from http import HTTPStatus

# Django
from django.urls import reverse

# AA CorpTools Doctrine
from corptools_doctrine.tests import AuthTestCase
from corptools_doctrine.tests.testdata.app import UserMainFactory

API_URL = "corptools_doctrine:api"


class TestGeneralAPI(AuthTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.basic = UserMainFactory(permissions=["corptools_doctrine.basic_access"])
        cls.admin = UserMainFactory(
            permissions=[
                "corptools_doctrine.basic_access",
                "corptools_doctrine.admin_access",
            ]
        )

    def test_menu_should_deliver_links_without_badge(self):
        # given
        url = reverse(f"{API_URL}:get_menu")
        self.client.force_login(self.basic)
        # when
        response = self.client.get(url)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()
        self.assertEqual(
            [link["link"] for link in data["left_links"]], ["/", "/overview/"]
        )
        self.assertEqual(data["right_links"], [])
        for link in data["left_links"]:
            self.assertFalse(link["is_external"])
            self.assertIsNone(link["badge"])
            self.assertFalse(link["has_errors"])

    def test_menu_should_show_manage_link_for_admin_access(self):
        # given
        url = reverse(f"{API_URL}:get_menu")
        self.client.force_login(self.admin)
        # when
        response = self.client.get(url)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            [link["link"] for link in response.json()["right_links"]], ["/manage/"]
        )

    def test_user_should_set_is_admin_from_admin_access(self):
        # given
        url = reverse(f"{API_URL}:get_user")
        # when / then
        self.client.force_login(self.basic)
        self.assertFalse(self.client.get(url).json()["is_admin"])
        self.client.force_login(self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(response.json()["is_admin"])
        self.assertTrue(response.json()["permissions"]["admin_access"])

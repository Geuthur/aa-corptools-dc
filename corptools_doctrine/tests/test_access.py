"""TestView class."""

# Standard Library
from http import HTTPStatus
from unittest.mock import patch

# Django
from django.test import RequestFactory, TestCase
from django.urls import reverse

# AA CorpTools Doctrine
# AA Corptools Doctrine Checker
from corptools_doctrine import views
from corptools_doctrine.tests import DoctrineCheckerTestCase
from corptools_doctrine.tests.testdata.utils import create_eveitemtype

INDEX_PATH = "corptools_doctrine.views"


class TestViewIndexAccess(DoctrineCheckerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.evetype = create_eveitemtype(
            type_id=1,
            name="Test Level",
        )

    def test_doctrine_view(self):
        """Test should load doctrine view."""
        # given
        request = self.factory.get(
            reverse(
                "corptools_doctrine:doctrine",
            )
        )
        request.user = self.user
        # when
        response = views.doctrine(request=request)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_corporation_doctrine_view(self):
        """Test should load corporation doctrine view."""
        # given
        request = self.factory.get(
            reverse(
                "corptools_doctrine:corporation_doctrine",
                args=[self.manage_own_character.character.corporation.corporation_id],
            )
        )
        request.user = self.manage_own_user
        # when
        response = views.corporation_doctrine(
            request=request,
            corporation_id=self.manage_own_character.character.corporation.corporation_id,
        )
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_overview_view(self):
        """Test should load overview view."""
        # given
        request = self.factory.get(reverse("corptools_doctrine:overview"))
        request.user = self.user
        # when
        response = views.overview(request=request)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_administration_view(self):
        """Test should load administration view."""
        # given
        request = self.factory.get(
            reverse(
                "corptools_doctrine:administration",
            )
        )
        request.user = self.manage_user
        # when
        response = views.manage(request=request)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_add_doctrine_view(self):
        """Test should load add doctrine view."""
        # given
        request = self.factory.get(
            reverse(
                "corptools_doctrine:add_doctrine",
            )
        )
        request.user = self.manage_user
        # when
        response = views.doctrine(request=request)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)

    @patch(INDEX_PATH + ".messages")
    def test_ajax_doctrine_view(self, mock_messages):
        """Test should load ajax doctrine view."""
        # Test Data
        form_data = {
            "name": "Test Skillplan",
            "order_weight": 1,
            "category": "Test Category",
            "skill_list": "Test Level 1\nTest Level 5\nTest Level 3",
        }

        request = self.factory.post(
            reverse("corptools_doctrine:ajax_doctrine"),
            data=form_data,
        )
        request.user = self.manage_user

        # Test Action
        response = views.ajax_doctrine(request)

        # Exptected Results
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        mock_messages.success.assert_called_once()

    @patch(INDEX_PATH + ".messages")
    def test_ajax_doctrine_view_error(self, mock_messages):
        """Test should load ajax doctrine view with error."""
        # given
        form_data = {}
        # when
        request = self.factory.post(
            reverse("corptools_doctrine:ajax_doctrine"),
            data=form_data,
        )

        request.user = self.manage_user

        response = views.ajax_doctrine(request)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        mock_messages.error.assert_called_once()

    @patch(INDEX_PATH + ".messages")
    def test_ajax_doctrine_view_wrong_parsed_skills(self, mock_messages):
        """Test should load ajax doctrine view with wrong parsed skills."""
        # given
        form_data = {
            "name": "Test Skillplan",
            "order_weight": 1,
            "category": "Test Category",
            "skill_list": "Invalid Skill Format",
        }
        # when
        request = self.factory.post(
            reverse("corptools_doctrine:ajax_doctrine"),
            data=form_data,
        )

        request.user = self.manage_user

        response = views.ajax_doctrine(request)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        mock_messages.error.assert_called_with(
            request,
            "There was an error with your skill plan: Skill List (Skillplan format): Line 1: 'Invalid Skill Format' - Invalid format. Use 'Skill Name Level' (Level 1-5) or EVE localized format",
        )

"""Tests for the auth hooks."""

# Standard Library
from unittest.mock import patch

# Django
from django.test import TestCase

# AA CorpTools Doctrine
from corptools_doctrine import app_settings
from corptools_doctrine.auth_hooks import MADoctrineCheckerMenuItem


class TestMenuItemName(TestCase):
    def test_should_use_default_name(self):
        """Test the menu entry shows the default app name."""
        # Test Action
        menu_item = MADoctrineCheckerMenuItem()

        # Test Result
        self.assertEqual(menu_item.text, "Doctrine Checker")

    def test_should_use_app_name_setting(self):
        """Test the menu entry shows the name from AA_CORPTOOLS_DOCTRINE_APP_NAME."""
        # Test Action
        with patch.object(app_settings, "AA_CORPTOOLS_DOCTRINE_APP_NAME", "Fits"):
            menu_item = MADoctrineCheckerMenuItem()

        # Test Result
        self.assertEqual(menu_item.text, "Fits")

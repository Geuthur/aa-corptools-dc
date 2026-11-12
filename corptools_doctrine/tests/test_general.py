"""Tests for the General model permission helpers."""

# Django
from django.contrib.auth.models import AnonymousUser

# AA CorpTools Doctrine
from corptools_doctrine.models import General
from corptools_doctrine.tests import AuthTestCase
from corptools_doctrine.tests.testdata.app import UserMainFactory


class TestGeneralPermissions(AuthTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.no_access = UserMainFactory(permissions=[])
        cls.manager = UserMainFactory(
            permissions=[
                "corptools_doctrine.basic_access",
                "corptools_doctrine.manage_access",
            ]
        )

    def test_codenames_should_stay_unchanged(self):
        self.assertEqual(
            [value for value, _ in General._meta.permissions],
            [
                "basic_access",
                "corp_access",
                "alliance_access",
                "manage_access",
                "admin_access",
            ],
        )

    def test_get_perm_should_accept_enum_and_string(self):
        self.assertEqual(
            General.get_perm(General.Permission.CORP_ACCESS),
            "corptools_doctrine.corp_access",
        )
        self.assertEqual(
            General.get_perm("corp_access"), "corptools_doctrine.corp_access"
        )

    def test_has_perm(self):
        self.assertTrue(General.has_perm(self.user, General.Permission.BASIC_ACCESS))
        self.assertFalse(
            General.has_perm(self.no_access, General.Permission.BASIC_ACCESS)
        )

    def test_has_perm_should_be_false_without_user(self):
        self.assertFalse(General.has_perm(None, General.Permission.BASIC_ACCESS))
        self.assertFalse(General.has_perm(object(), General.Permission.BASIC_ACCESS))
        self.assertFalse(
            General.has_perm(AnonymousUser(), General.Permission.BASIC_ACCESS)
        )

    def test_has_any_perm(self):
        self.assertTrue(
            General.has_any_perm(
                self.user,
                General.Permission.CORP_ACCESS,
                General.Permission.BASIC_ACCESS,
            )
        )
        self.assertFalse(
            General.has_any_perm(self.no_access, General.Permission.BASIC_ACCESS)
        )
        self.assertFalse(General.has_any_perm(None, General.Permission.BASIC_ACCESS))

    def test_has_management_access(self):
        self.assertTrue(General.has_management_access(self.manager))
        self.assertFalse(General.has_management_access(self.user))
        self.assertFalse(General.has_management_access(None))

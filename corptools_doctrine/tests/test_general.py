"""Tests for the permission definitions in General."""

# Standard Library
import re
from pathlib import Path

# AA CorpTools Doctrine
import corptools_doctrine
from corptools_doctrine.models import General
from corptools_doctrine.tests import AuthTestCase

APP_LABEL = "corptools_doctrine"
# Permission strings like "<app_label>.<codename>" in quotes, any app label
PERMISSION_PATTERN = re.compile(r"[\"']([A-Za-z0-9_]+)\.([A-Za-z0-9_]*_access)[\"']")
# Django permissions of the models are disabled via default_permissions
IGNORED_SUFFIXES = ("tests", "migrations")


class TestGeneralPermissions(AuthTestCase):
    def test_codenames_should_stay_unchanged(self):
        self.assertEqual(
            [codename for codename, _ in General._meta.permissions],
            [
                "basic_access",
                "corp_access",
                "alliance_access",
                "manage_access",
                "admin_access",
            ],
        )

    def test_used_permission_strings_should_exist_in_general(self):
        """Every permission string used in the code is defined in General.Meta.permissions."""
        defined = {f"{APP_LABEL}.{c}" for c, _ in General._meta.permissions}
        used: dict[str, set[str]] = {}
        root = Path(corptools_doctrine.__file__).parent

        for path in root.rglob("*.py"):
            relative = path.relative_to(root)
            if any(part in IGNORED_SUFFIXES for part in relative.parts):
                continue
            for label, codename in PERMISSION_PATTERN.findall(path.read_text("utf-8")):
                used.setdefault(f"{label}.{codename}", set()).add(str(relative))

        self.assertTrue(used, "No permission strings found, pattern is broken.")
        unknown = {c: sorted(f) for c, f in used.items() if c not in defined}
        self.assertEqual(unknown, {})

    def test_has_management_access(self):
        # AA CorpTools Doctrine
        from corptools_doctrine.tests.testdata.app import UserMainFactory

        self.assertTrue(
            General.objects.has_management_access(
                UserMainFactory(permissions=["corptools_doctrine.manage_access"])
            )
        )
        self.assertTrue(
            General.objects.has_management_access(
                UserMainFactory(permissions=["corptools_doctrine.admin_access"])
            )
        )
        self.assertFalse(
            General.objects.has_management_access(
                UserMainFactory(permissions=["corptools_doctrine.basic_access"])
            )
        )

    def test_has_access_methods(self):
        # AA CorpTools Doctrine
        from corptools_doctrine.tests.testdata.app import UserMainFactory

        def user(*codenames):
            return UserMainFactory(
                permissions=[f"corptools_doctrine.{c}" for c in codenames]
            )

        manager = General.objects
        basic = user("basic_access")
        self.assertTrue(manager.has_basic_access(basic))
        self.assertFalse(manager.has_basic_access(user("corp_access")))

        self.assertTrue(manager.has_corp_access(user("corp_access")))
        self.assertFalse(manager.has_corp_access(basic))
        self.assertTrue(manager.has_alliance_access(user("alliance_access")))
        self.assertFalse(manager.has_alliance_access(basic))

        self.assertTrue(manager.has_manage_access(user("manage_access")))
        self.assertFalse(manager.has_manage_access(user("admin_access")))

        self.assertTrue(manager.has_admin_access(user("admin_access")))
        self.assertFalse(manager.has_admin_access(user("manage_access")))
        self.assertFalse(manager.has_admin_access(basic))

    def test_superuser_should_have_admin_corp_alliance_and_management_access(self):
        manager = General.objects
        self.assertTrue(manager.has_admin_access(self.superuser))
        self.assertTrue(manager.has_corp_access(self.superuser))
        self.assertTrue(manager.has_alliance_access(self.superuser))
        self.assertTrue(manager.has_management_access(self.superuser))

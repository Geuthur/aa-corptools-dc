"""TestAPI class."""

# Standard Library
import json

# Alliance Auth
from allianceauth.eveonline.models import EveCorporationInfo

# Alliance Auth (External Libs)
from corptools.models.skills import SkillList

# AA CorpTools Doctrine
from corptools_doctrine.models import Doctrine
from corptools_doctrine.tests import DoctrineCheckerTestCase
from corptools_doctrine.tests.testdata.utils import (
    add_new_permission_to_user,
    create_owner_from_user,
)

MODULE_PATH = "corptools_doctrine.managers"


class TestDoctrineManager(DoctrineCheckerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        create_owner_from_user(cls.user, owner_type="corporation")
        create_owner_from_user(cls.superuser, owner_type="corporation")

        cls.eve_corp = EveCorporationInfo.objects.filter(
            corporation_id=cls.user_character.character.corporation.corporation_id
        )
        cls.eve_corp2 = EveCorporationInfo.objects.filter(
            corporation_id=cls.superuser_character.character.corporation.corporation_id
        )
        cls.skilllist = SkillList.objects.create(
            name="Test Skill List",
            skill_list=json.dumps({"Mining Barge": 5}),
            order_weight=1,
        )

        cls.doctrine = Doctrine.objects.create(
            skilllist=cls.skilllist,
            category="Test Category",
        )

    def test_visible_to_should_not_include_any_corporations(self):
        """
        Test access permissions for Doctrine without permissions.

        ### Expected Result
        - User without permissions cannot access any corporations.
        """
        corporation = Doctrine.objects.visible_eve_corporations(self.user)
        self.assertNotIn(self.eve_corp, corporation)
        self.assertNotIn(self.eve_corp2, corporation)

    def test_visible_to_should_include_own_corporation_only(self):
        """
        Test access permissions for Doctrine with 'corp_access' permission.

        ### Expected Result
        - User with 'corp_access' permission can access their own corporation only.
        - User can not access other corporations.
        """
        self.user = add_new_permission_to_user(
            user=self.user, permission_name="corptools_doctrine.corp_access"
        )
        self.user.refresh_from_db()
        corporation = Doctrine.objects.visible_eve_corporations(self.user)
        self.assertQuerySetEqual(self.eve_corp, corporation)
        self.assertNotIn(self.eve_corp2, corporation)

    def test_visible_to_should_include_all_corporations(self):
        """
        Test access permissions for Doctrine with superuser permission.

        ### Expected Result
        - User with superuser permission can access all corporations.
        """
        corporation = Doctrine.objects.visible_eve_corporations(
            self.superuser
        ).order_by("corporation_id")
        corporations = (
            EveCorporationInfo.objects.all()
            .order_by("corporation_id")
            .order_by("corporation_id")
        )
        self.assertQuerySetEqual(corporations, corporation)

    def test_visible_to_should_include_all_corporations_admin_access(self):
        """
        Test access permissions for Doctrine with 'admin_access' permission.

        ### Expected Result
        - User with 'admin_access' permission can access all corporations.
        """
        corporation = Doctrine.objects.visible_eve_corporations(
            self.manage_user
        ).order_by("corporation_id")
        corporations = (
            EveCorporationInfo.objects.all()
            .order_by("corporation_id")
            .order_by("corporation_id")
        )
        self.assertQuerySetEqual(corporations, corporation)

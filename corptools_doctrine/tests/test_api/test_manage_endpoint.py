"""TestAPI class."""

# Standard Library
import json
from http import HTTPStatus

# Django
from django.urls import reverse

# Alliance Auth
from allianceauth.eveonline.models import EveCorporationInfo

# Alliance Auth (External Libs)
from corptools.models.audits import CharacterAudit as Character
from corptools.models.skills import SkillList

# AA CorpTools Doctrine
from corptools_doctrine.models import Doctrine
from corptools_doctrine.tests import DoctrineCheckerTestCase
from corptools_doctrine.tests.testdata.utils import create_owner_from_user

API_PATH = "corptools_doctrine.api.manage"
API_URL = "corptools_doctrine:api"


class TestManageAPI(DoctrineCheckerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.corp_audit = create_owner_from_user(cls.user, owner_type="corporation")
        create_owner_from_user(cls.superuser, owner_type="corporation")
        create_owner_from_user(cls.no_access, owner_type="corporation")

        cls.skilllist = SkillList.objects.create(
            name="Test Skill List",
            skill_list=json.dumps({"Mining Barge": 5}),
            order_weight=1,
        )

        cls.doctrine = Doctrine.objects.create(
            skilllist=cls.skilllist,
            category="Test Category",
        )

    def test_manage_doctrine_endpoint_access(self):
        # given
        url = reverse(f"{API_URL}:manage_doctrines")
        self.client.force_login(self.manage_user)
        # when
        response = self.client.get(url)
        response_json = response.json()
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn("Test Skill List", response_json[0]["name"]["sort"])
        self.assertIn("Test Category", response_json[0]["category"]["sort"])

    def test_manage_doctrine_endpoint_no_access(self):
        # given
        url = reverse(f"{API_URL}:manage_doctrines")
        self.client.force_login(self.user)
        # when
        response = self.client.get(url)
        # then
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_account_overview_endpoint(self):
        # given
        url = reverse(f"{API_URL}:get_account_overview")
        self.client.force_login(self.user)
        # when
        response = self.client.get(url)
        response_json = response.json()
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response_json), 1)

    def test_account_overview_endpoint_admin_access(self):
        # given
        url = reverse(f"{API_URL}:get_account_overview")
        self.client.force_login(self.manage_user)
        # when
        response = self.client.get(url)
        response_json = response.json()

        all_characters = Character.objects.count()
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response_json), all_characters)

    def test_account_overview_no_access(self):
        # given
        url = reverse(f"{API_URL}:get_account_overview")
        self.client.force_login(self.user)
        # when
        response = self.client.get(url)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_corporation_overview_endpoint(self):
        # given
        url = reverse(f"{API_URL}:get_corporation_overview")
        self.client.force_login(self.user)
        # when
        response = self.client.get(url)
        response_json = response.json()

        counted_corps = len(response_json)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(counted_corps, 1)

    def test_corporation_overview_endpoint_admin_access(self):
        # given
        url = reverse(f"{API_URL}:get_corporation_overview")
        self.client.force_login(self.manage_user)

        # when
        response = self.client.get(url)
        response_json = response.json()

        counted_corps = len(response_json)
        all_corps = EveCorporationInfo.objects.count()

        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(counted_corps, all_corps)

    def test_corporation_overview_no_access(self):
        # given
        url = reverse(f"{API_URL}:get_corporation_overview")
        self.client.force_login(self.no_access)
        # when
        response = self.client.get(url)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)

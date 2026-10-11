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
        # Test Data
        url = reverse(f"{API_URL}:manage_doctrines")
        self.client.force_login(self.manage_user)

        # Test Action
        response = self.client.get(url)
        response_json = response.json()

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response_json[0]["name"], "Test Skill List")
        self.assertEqual(response_json[0]["category"], "Test Category")

    def test_manage_doctrine_endpoint_no_access(self):
        # Test Data
        url = reverse(f"{API_URL}:manage_doctrines")
        self.client.force_login(self.user)

        # Test Action
        response = self.client.get(url)

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_update_doctrine_should_succeed(self):
        # Test Data
        url = reverse(f"{API_URL}:update_doctrine", kwargs={"pk": self.doctrine.pk})
        self.client.force_login(self.manage_user)
        payload = {
            "name": "Updated Skill List",
            "category": "Updated Category",
            "order_weight": 5,
            "show_on_audit": False,
        }

        # Test Action
        response = self.client.put(
            url, data=json.dumps(payload), content_type="application/json"
        )
        response_json = response.json()

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response_json["name"], "Updated Skill List")
        self.assertEqual(response_json["category"], "Updated Category")
        self.assertEqual(response_json["order_weight"], 5)
        self.assertFalse(response_json["show_on_audit"])

    def test_delete_doctrine_should_succeed(self):
        # Test Data
        new_skilllist = SkillList.objects.create(
            name="To Delete",
            skill_list=json.dumps({"Mining Barge": 1}),
            order_weight=99,
        )
        new_doc = Doctrine.objects.create(
            skilllist=new_skilllist,
            category="Temp",
        )
        url = reverse(f"{API_URL}:delete_doctrine", kwargs={"pk": new_doc.pk})
        self.client.force_login(self.manage_user)

        # Test Action
        response = self.client.delete(url)
        response_json = response.json()

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(response_json["success"])
        self.assertFalse(Doctrine.objects.filter(pk=new_doc.pk).exists())

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

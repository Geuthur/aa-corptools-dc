"""TestAPI class."""

# Standard Library
import json
from http import HTTPStatus
from unittest.mock import patch

# Third Party
from evesde_factory.allianceauth import EveCharacterFactory

# Django
from django.urls import reverse

# Alliance Auth
from allianceauth.eveonline.models import EveCorporationInfo

# Alliance Auth (External Libs)
from corptools.models.audits import CharacterAudit as Character
from corptools.models.skills import SkillList

# AA CorpTools Doctrine
from corptools_doctrine.models import Doctrine
from corptools_doctrine.tests import AuthTestCase
from corptools_doctrine.tests.testdata.app import UserMainFactory
from corptools_doctrine.tests.testdata.utils import create_owner_from_user

API_PATH = "corptools_doctrine.api.manage"
API_URL = "corptools_doctrine:api"


class TestManageAPI(AuthTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.no_access = UserMainFactory(permissions=[])
        cls.manage_user = UserMainFactory(
            permissions=[
                "corptools_doctrine.basic_access",
                "corptools_doctrine.corp_access",
                "corptools_doctrine.alliance_access",
                "corptools_doctrine.manage_access",
                "corptools_doctrine.admin_access",
            ],
            main_character__character=EveCharacterFactory(
                corporation=cls.user.profile.main_character.corporation
            ),
        )

        for user in (cls.user, cls.no_access, cls.superuser, cls.manage_user):
            create_owner_from_user(user=user)
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

    def _post_json(self, url, payload):
        return self.client.post(
            url, data=json.dumps(payload), content_type="application/json"
        )

    def _put_json(self, url, payload):
        return self.client.put(
            url, data=json.dumps(payload), content_type="application/json"
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
        self.assertEqual(response.json(), {"error": "Permission Denied"})

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

    def test_overviews_should_return_403_when_nothing_is_visible(self):
        # Test Data
        self.client.force_login(self.user)

        for name, manager_method in (
            ("get_account_overview", "visible_eve_characters"),
            ("get_corporation_overview", "visible_eve_corporations"),
        ):
            with self.subTest(endpoint=name):
                url = reverse(f"{API_URL}:{name}")

                # Test Action
                with patch.object(
                    Doctrine.objects.__class__, manager_method, return_value=None
                ):
                    response = self.client.get(url)

                # Expected Result
                self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
                self.assertEqual(response.json(), {"error": "Permission Denied"})

    def test_create_doctrine_should_return_403_without_manage_access(self):
        # Test Data
        url = reverse(f"{API_URL}:create_doctrine")
        self.client.force_login(self.user)

        # Test Action
        response = self._post_json(url, {"name": "New", "skill_list": "Mining 1"})

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(response.json(), {"error": "Permission Denied"})

    def test_create_doctrine_should_return_400_with_form_errors(self):
        # Test Data
        url = reverse(f"{API_URL}:create_doctrine")
        self.client.force_login(self.manage_user)

        # Test Action
        response = self._post_json(url, {"name": "", "skill_list": ""})

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(list(response.json()), ["error"])
        self.assertTrue(response.json()["error"])

    def test_create_doctrine_should_return_400_with_empty_skill_plan(self):
        # Test Data
        url = reverse(f"{API_URL}:create_doctrine")
        self.client.force_login(self.manage_user)

        # Test Action
        with patch(
            f"{API_PATH}.forms.SkillListForm.get_parsed_skills", return_value={}
        ):
            response = self._post_json(
                url, {"name": "Empty Plan", "skill_list": "Mining Barge 1"}
            )

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(
            response.json(), {"error": "Your skill plan is empty. Please add skills."}
        )

    def test_update_doctrine_should_return_403_without_manage_access(self):
        # Test Data
        url = reverse(f"{API_URL}:update_doctrine", kwargs={"pk": self.doctrine.pk})
        self.client.force_login(self.user)

        # Test Action
        response = self._put_json(url, {"category": "X"})

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(response.json(), {"error": "Permission Denied"})

    def test_update_doctrine_should_return_404_for_unknown_doctrine(self):
        # Test Data
        url = reverse(f"{API_URL}:update_doctrine", kwargs={"pk": 999999})
        self.client.force_login(self.manage_user)

        # Test Action
        response = self._put_json(url, {"category": "X"})

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(response.json(), {"error": "Doctrine not found"})

    def test_update_doctrine_should_return_400_for_duplicate_name(self):
        # Test Data
        other = SkillList.objects.create(
            name="Other Skill List",
            skill_list=json.dumps({"Mining Barge": 1}),
            order_weight=2,
        )
        Doctrine.objects.create(skilllist=other, category="Other")
        url = reverse(f"{API_URL}:update_doctrine", kwargs={"pk": self.doctrine.pk})
        self.client.force_login(self.manage_user)

        # Test Action
        response = self._put_json(url, {"name": "other skill list"})

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(
            response.json(), {"error": "Skill list with this name already exists"}
        )

    def test_update_doctrine_should_return_400_for_invalid_order_weight(self):
        # Test Data
        url = reverse(f"{API_URL}:update_doctrine", kwargs={"pk": self.doctrine.pk})
        self.client.force_login(self.manage_user)

        # Test Action
        response = self._put_json(url, {"order_weight": 1000})

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(
            response.json(), {"error": "Order weight must be between 0 and 999"}
        )

    def test_delete_doctrine_should_return_403_without_manage_access(self):
        # Test Data
        url = reverse(f"{API_URL}:delete_doctrine", kwargs={"pk": self.doctrine.pk})
        self.client.force_login(self.user)

        # Test Action
        response = self.client.delete(url)

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(response.json(), {"error": "Permission Denied"})
        self.assertTrue(Doctrine.objects.filter(pk=self.doctrine.pk).exists())

    def test_delete_doctrine_should_return_404_for_unknown_doctrine(self):
        # Test Data
        url = reverse(f"{API_URL}:delete_doctrine", kwargs={"pk": 999999})
        self.client.force_login(self.manage_user)

        # Test Action
        response = self.client.delete(url)

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(response.json(), {"error": "Doctrine not found."})

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

    def test_corporation_overview_should_return_403_without_basic_access(self):
        # given
        url = reverse(f"{API_URL}:get_corporation_overview")
        self.client.force_login(self.no_access)
        # when
        response = self.client.get(url)
        # then
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(response.json(), {"error": "Permission Denied"})

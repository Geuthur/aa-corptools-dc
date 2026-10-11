"""Tests for the Corporation Doctrines API endpoint."""

# Standard Library
import json
from http import HTTPStatus

# Django
from django.urls import reverse

# Alliance Auth (External Libs)
from corptools.models.skills import Skill as CharacterSkill
from corptools.models.skills import SkillList

# AA CorpTools Doctrine
from corptools_doctrine.api import schema
from corptools_doctrine.models import Doctrine
from corptools_doctrine.tests import DoctrineCheckerTestCase
from corptools_doctrine.tests.testdata.utils import create_owner_from_user

API_URL = "corptools_doctrine:api"


class TestCorporationDoctrinesAPI(DoctrineCheckerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        create_owner_from_user(cls.user, owner_type="corporation")
        cls.characteraudit = create_owner_from_user(cls.user)

        cls.skilllist = SkillList.objects.create(
            name="Mining Ops",
            skill_list=json.dumps({"Mining Barge": 5}),
            order_weight=1,
            show_on_audit=True,
        )

        cls.doctrine = Doctrine.objects.create(
            skilllist=cls.skilllist,
            category="Industrial",
        )

    def test_get_corporation_doctrines_should_return_members_with_populated_doctrines(
        self,
    ):
        # Test Data
        CharacterSkill.objects.update_or_create(
            character=self.characteraudit,
            skill_id=self.item_type.id,
            defaults={
                "skill_name": self.item_type,
                "active_skill_level": 5,
                "trained_skill_level": 5,
                "skillpoints_in_skill": 1280000,
            },
        )
        url = reverse(
            f"{API_URL}:get_corporation_doctrines",
            kwargs={"corporation_id": 2001},
        )
        self.client.force_login(self.manage_own_user)

        # Test Action
        response = self.client.get(url)
        response_json = response.json()

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIsInstance(response_json, list)
        self.assertGreater(len(response_json), 0)

        # Verify that doctrines dict is populated and not empty
        member_entry = next(
            (
                m
                for m in response_json
                if m["character"]["character_id"]
                == self.user_character.character.character_id
            ),
            None,
        )
        self.assertIsNotNone(member_entry)
        self.assertIn("Mining Ops", member_entry["doctrines"])
        doctrine_info = member_entry["doctrines"]["Mining Ops"]
        self.assertEqual(doctrine_info["name"], "Mining Ops")
        self.assertEqual(doctrine_info["category"], "Industrial")
        # Skill level 5 matches requirement 5 -> 0 missing skills (ready)
        self.assertEqual(len(doctrine_info["skills"]), 0)

    def test_get_corporation_doctrines_should_return_missing_skills_when_untrained(
        self,
    ):
        # Test Data
        CharacterSkill.objects.update_or_create(
            character=self.characteraudit,
            skill_id=self.item_type.id,
            defaults={
                "skill_name": self.item_type,
                "active_skill_level": 1,
                "trained_skill_level": 1,
                "skillpoints_in_skill": 250,
            },
        )
        url = reverse(
            f"{API_URL}:get_corporation_doctrines",
            kwargs={"corporation_id": 2001},
        )
        self.client.force_login(self.manage_own_user)

        # Test Action
        response = self.client.get(url)
        response_json = response.json()

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)
        member_entry = next(
            (
                m
                for m in response_json
                if m["character"]["character_id"]
                == self.user_character.character.character_id
            ),
            None,
        )
        self.assertIsNotNone(member_entry)
        self.assertIn("Mining Ops", member_entry["doctrines"])
        doctrine_info = member_entry["doctrines"]["Mining Ops"]
        # Untrained -> missing skill should be listed
        self.assertGreater(len(doctrine_info["skills"]), 0)
        self.assertEqual(doctrine_info["skills"][0]["skill_name"], "Mining Barge")
        self.assertEqual(doctrine_info["skills"][0]["required_level"], 5)

    def test_get_corporation_doctrines_should_fail_permission_denied_for_unauthorized_user(
        self,
    ):
        # Test Data
        url = reverse(
            f"{API_URL}:get_corporation_doctrines",
            kwargs={"corporation_id": 2001},
        )
        self.client.force_login(self.no_access)

        # Test Action
        response = self.client.get(url)

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_get_corporation_members_list_should_return_members_and_doctrines(
        self,
    ):
        # Test Data
        url = reverse(
            f"{API_URL}:get_corporation_members_list",
            kwargs={"corporation_id": 2001},
        )
        self.client.force_login(self.manage_own_user)

        # Test Action
        response = self.client.get(url)
        response_json = response.json()

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn("members", response_json)
        self.assertIn("doctrines", response_json)
        self.assertIn("corporation_id", response_json)
        self.assertIn("corporation_name", response_json)
        self.assertEqual(response_json["corporation_id"], 2001)
        self.assertGreater(len(response_json["members"]), 0)
        self.assertGreater(len(response_json["doctrines"]), 0)
        self.assertEqual(response_json["doctrines"][0]["name"], "Mining Ops")

    def test_get_corporation_members_list_should_fail_for_unauthorized_user(
        self,
    ):
        # Test Data
        url = reverse(
            f"{API_URL}:get_corporation_members_list",
            kwargs={"corporation_id": 2001},
        )
        self.client.force_login(self.no_access)

        # Test Action
        response = self.client.get(url)

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_audit_corporation_members_should_return_audited_doctrines_for_character_ids(
        self,
    ):
        # Test Data
        CharacterSkill.objects.update_or_create(
            character=self.characteraudit,
            skill_id=self.item_type.id,
            defaults={
                "skill_name": self.item_type,
                "active_skill_level": 5,
                "trained_skill_level": 5,
                "skillpoints_in_skill": 1280000,
            },
        )
        url = reverse(
            f"{API_URL}:audit_corporation_members",
            kwargs={"corporation_id": 2001},
        )
        self.client.force_login(self.manage_own_user)
        payload = {"character_ids": [self.user_character.character.character_id]}

        # Test Action
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
        )
        response_json = response.json()

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIsInstance(response_json, list)
        self.assertEqual(len(response_json), 1)
        member = response_json[0]
        self.assertEqual(
            member["character"]["character_id"],
            self.user_character.character.character_id,
        )
        self.assertIn("Mining Ops", member["doctrines"])
        self.assertEqual(len(member["doctrines"]["Mining Ops"]["skills"]), 0)

    def test_audit_corporation_members_should_fail_for_unauthorized_user(
        self,
    ):
        # Test Data
        url = reverse(
            f"{API_URL}:audit_corporation_members",
            kwargs={"corporation_id": 2001},
        )
        self.client.force_login(self.no_access)

        # Test Action
        response = self.client.post(
            url,
            data=json.dumps({"character_ids": [12345]}),
            content_type="application/json",
        )

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_audit_corporation_members_should_filter_by_category(self):
        # Test Data
        url = reverse(
            f"{API_URL}:audit_corporation_members",
            kwargs={"corporation_id": 2001},
        )
        self.client.force_login(self.manage_own_user)
        payload = {
            "character_ids": [self.user_character.character.character_id],
            "category": "NonExistentCategory",
        }

        # Test Action
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
        )
        response_json = response.json()

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response_json), 1)
        # Filtered by non-existent category -> doctrines dict should be empty
        self.assertEqual(len(response_json[0]["doctrines"]), 0)

    def test_audit_corporation_members_should_filter_by_doctrine_ids(self):
        # Test Data
        url = reverse(
            f"{API_URL}:audit_corporation_members",
            kwargs={"corporation_id": 2001},
        )
        self.client.force_login(self.manage_own_user)
        payload = {
            "character_ids": [self.user_character.character.character_id],
            "doctrine_ids": [self.doctrine.pk],
        }

        # Test Action
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
        )
        response_json = response.json()

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response_json), 1)
        self.assertIn("Mining Ops", response_json[0]["doctrines"])

    def test_get_corporation_doctrines_should_filter_by_category_query_param(self):
        # Test Data
        url = reverse(
            f"{API_URL}:get_corporation_doctrines",
            kwargs={"corporation_id": 2001},
        )
        self.client.force_login(self.manage_own_user)

        # Test Action
        response = self.client.get(f"{url}?category=NonExistentCategory")
        response_json = response.json()

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertGreater(len(response_json), 0)
        self.assertEqual(len(response_json[0]["doctrines"]), 0)

    def test_get_corporation_doctrines_should_filter_by_doctrine_ids_query_param(self):
        # Test Data
        url = reverse(
            f"{API_URL}:get_corporation_doctrines",
            kwargs={"corporation_id": 2001},
        )
        self.client.force_login(self.manage_own_user)

        # Test Action
        response = self.client.get(f"{url}?doctrine_ids={self.doctrine.pk}")
        response_json = response.json()

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertGreater(len(response_json), 0)
        user_entry = next(
            (
                m
                for m in response_json
                if m["character"]["character_id"]
                == self.user_character.character.character_id
            ),
            None,
        )
        self.assertIsNotNone(user_entry)
        self.assertIn("Mining Ops", user_entry["doctrines"])

    def test_doctrine_audit_filter_methods(self):
        # Test Data
        audit_filter = schema.DoctrineAuditFilter(
            category=self.doctrine.category,
            doctrine_ids=[self.doctrine.pk],
        )

        # Test Action
        doctrines = audit_filter.get_doctrines()
        skill_names = audit_filter.get_required_skill_names(doctrines)

        # Expected Result
        self.assertEqual(len(doctrines), 1)
        self.assertEqual(doctrines[0].pk, self.doctrine.pk)
        self.assertIn("Mining Barge", skill_names)

    def test_get_doctrines_should_return_character_doctrines(self):
        # Test Data
        CharacterSkill.objects.update_or_create(
            character=self.characteraudit,
            skill_id=self.item_type.id,
            defaults={
                "skill_name": self.item_type,
                "active_skill_level": 5,
                "trained_skill_level": 5,
                "skillpoints_in_skill": 1280000,
            },
        )
        url = reverse(
            f"{API_URL}:get_doctrines",
            kwargs={"character_id": self.user_character.character.character_id},
        )
        self.client.force_login(self.user)

        # Test Action
        response = self.client.get(url)
        response_json = response.json()

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIsInstance(response_json, list)
        self.assertGreater(len(response_json), 0)
        char_entry = next(
            (
                c
                for c in response_json
                if c["character"]["character_id"]
                == self.user_character.character.character_id
            ),
            None,
        )
        self.assertIsNotNone(char_entry)
        self.assertIn("Mining Ops", char_entry["doctrines"])

    def test_get_doctrines_should_evaluate_targeted_character_only(self):
        # Test Data
        url = reverse(
            f"{API_URL}:get_doctrines",
            kwargs={"character_id": self.user_character.character.character_id},
        )
        self.client.force_login(self.user)

        # Test Action
        response = self.client.get(
            f"{url}?target_character_id={self.user_character.character.character_id}"
        )
        response_json = response.json()

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIsInstance(response_json, list)
        self.assertGreater(len(response_json), 0)

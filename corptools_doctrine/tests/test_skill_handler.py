# Standard Library
import json

# Alliance Auth (External Libs)
from corptools.models.skills import Skill as CharacterSkill
from corptools.models.skills import SkillList

# AA CorpTools Doctrine
from corptools_doctrine.helpers.skill_handler import SkillListHandler
from corptools_doctrine.models import Doctrine
from corptools_doctrine.tests import DoctrineCheckerTestCase
from corptools_doctrine.tests.testdata.utils import create_owner_from_user


class TestSkillHandler(DoctrineCheckerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.characteraudit = create_owner_from_user(user=cls.user)
        cls.sk_check = {
            "Skill II": 2,
            "Skill I": 1,
        }

        cls.skilllist = SkillList.objects.create(
            name="fit",
            skill_list=json.dumps(cls.sk_check),
            order_weight=1,
        )

        cls.doctrine = Doctrine.objects.create(
            skilllist=cls.skilllist, category="Test Category"
        )

        cls.charskill = CharacterSkill.objects.create(
            character=cls.characteraudit,
            skill_id=cls.item_type.id,
            skill_name=cls.item_type,
            active_skill_level=3,
            skillpoints_in_skill=900000,
            trained_skill_level=5,
        )

    def test_check_skill_lists_v2_should_evaluate_character_skills(self):
        """Test should check skill lists v2 for linked characters."""
        # Test Data
        handler = SkillListHandler()
        linked_characters = list(
            self.user.character_ownerships.all().select_related("character")
        )
        doctrines = Doctrine.objects.filter(pk=self.doctrine.pk)

        # Test Action
        result = handler.check_skill_lists_v2(
            doctrines=doctrines,
            linked_characters=linked_characters,
        )

        # Expected Result
        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0].character.character_name,
            self.characteraudit.character.character_name,
        )
        self.assertEqual(len(result[0].doctrines), 1)
        self.assertEqual(result[0].doctrines[0].name, "fit")

    def test_check_skill_lists_v2_should_return_empty_on_no_characters(self):
        """Test should return empty list when no linked characters provided."""
        # Test Data
        handler = SkillListHandler()
        doctrines = Doctrine.objects.filter(pk=self.doctrine.pk)

        # Test Action
        result = handler.check_skill_lists_v2(
            doctrines=doctrines,
            linked_characters=[],
        )

        # Expected Result
        self.assertEqual(result, [])

    def test_get_skill_list_v2_should_return_schema_for_user(self):
        """Test should retrieve CharacterSkillListSchema for user."""
        # Test Data
        handler = SkillListHandler()
        doctrines = Doctrine.objects.filter(pk=self.doctrine.pk)

        # Test Action
        result = handler.get_skill_list_v2(
            user_id=self.user.pk,
            doctrines=doctrines,
        )

        # Expected Result
        self.assertEqual(len(result.characters), 1)
        self.assertEqual(
            result.characters[0].character.character_name,
            self.characteraudit.character.character_name,
        )

    def test_get_accounts_skill_list_v2_should_return_bulk_user_data(self):
        """Test should get bulk skill lists for multiple users via v2."""
        # Test Data
        handler = SkillListHandler()
        doctrines = Doctrine.objects.filter(pk=self.doctrine.pk)

        # Test Action
        result = handler.get_accounts_skill_list_v2(
            users=[self.user],
            doctrines=doctrines,
        )

        # Expected Result
        self.assertIn(self.user.pk, result)
        self.assertEqual(
            result[self.user.pk]["chars"],
            [self.characteraudit.character.character_id],
        )
        self.assertTrue(result[self.user.pk]["data"])
        self.assertEqual(len(result[self.user.pk]["data"].characters), 1)

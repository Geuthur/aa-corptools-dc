# Standard Library
import json

# Alliance Auth (External Libs)
from corptools.models.skills import Skill as CharacterSkill
from corptools.models.skills import SkillList

# AA CorpTools Doctrine
from corptools_doctrine import __title__
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

    def test_get_skill_list_hash(self):
        """Test should generate correct skill list hash."""
        # given
        handler = SkillListHandler()
        skills = ["Skill A", "Skill B", "Skill C"]
        expected_hash = "3d6a81fde9ea9a3e2e791536378c37f6"
        # then
        self.assertEqual(handler._get_skill_list_hash(skills), expected_hash)

    def test_get_chars_hash(self):
        """Test should generate correct character hash."""
        # given
        handler = SkillListHandler()
        characters = [1001, 1002, 1003]
        expected_hash = "fee1f06f37321e04f41a8caaa2f23330"
        # then
        self.assertEqual(handler._get_chars_hash(characters), expected_hash)

    def test_generate_doctrine_html(self):
        """Test should generate doctrine HTML snippet."""
        # given
        handler = SkillListHandler()
        # when
        html = handler._generate_doctrine_html(
            skill_list_name="Test Doctrine",
            character_id=1001,
            has_missing_skills=True,
            skill_list_pk=1,
        )
        # then
        self.assertIn("Test Doctrine", html)
        self.assertIn("1001", html)
        self.assertIn("btn-danger", html)
        self.assertIn("<i class='fa-solid fa-copy'></i>", html)

    def test_generate_doctrine_html_no_missing(self):
        """Test should generate doctrine HTML snippet for complete skills."""
        # given
        handler = SkillListHandler()
        # when
        html = handler._generate_doctrine_html(
            skill_list_name="Test Doctrine",
            character_id=1001,
            has_missing_skills=False,
        )
        # then
        self.assertIn("Test Doctrine", html)
        self.assertIn("btn-success", html)
        self.assertIn("<i class='fa-solid fa-check'></i>", html)

    def test_check_skill_lists(self):
        """Test should check skill lists for linked characters."""
        # Test Data
        CharacterSkill.objects.create(
            character=self.characteraudit,
            skill_id=self.evetype.type_id,
            skill_name=self.evetype,
            active_skill_level=3,
            skillpoints_in_skill=900000,
            trained_skill_level=5,
        )

        handler = SkillListHandler()
        linked_characters = [self.user_character.character.character_id]

        # Test Action
        result = handler.check_skill_lists(
            doctrines=[self.doctrine],
            linked_characters=linked_characters,
        )

        character_name = self.characteraudit.character.character_name

        # Expected Results
        self.assertIn(character_name, result)
        self.assertIn("fit", result[character_name]["doctrines"])
        self.assertTrue(result[character_name]["doctrines"]["fit"]["html"])
        self.assertIn("Mining Barge", result[character_name]["skills"])

    def test_check_skill_lists_no_skills(self):
        """Test should check skill lists for linked characters with no skills."""
        # Test Data
        handler = SkillListHandler()
        linked_characters = [self.user_character.character.character_id]

        # Test Action
        result = handler.check_skill_lists(
            doctrines=[self.doctrine],
            linked_characters=linked_characters,
        )

        # Expected Results
        self.assertEqual({}, result)

    def test_get_users_skill_lists(self):
        """Test should get users skill lists."""
        # Test Data
        handler = SkillListHandler()
        doctrines = Doctrine.objects.filter(pk=self.doctrine.pk)

        # Test Action
        result = handler.get_accounts_skill_list(users=[self.user], doctrines=doctrines)

        # Expected Results
        self.assertIn(self.user.pk, result)
        self.assertIn(
            self.characteraudit.character.character_id, result[self.user.pk]["chars"]
        )
        self.assertIn("doctrines", result[self.user.pk]["data"])
        self.assertIn("characters", result[self.user.pk]["data"])
        self.assertIn("skills_list", result[self.user.pk]["data"])

# Standard Library
import json

# Alliance Auth (External Libs)
from corptools.models.skills import SkillList

# AA CorpTools Doctrine
from corptools_doctrine import __title__
from corptools_doctrine.models import Doctrine, skillvalidator
from corptools_doctrine.tests import DoctrineCheckerTestCase
from corptools_doctrine.tests.testdata.utils import create_owner_from_user


class TestModelsSkillChecker(DoctrineCheckerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.characteraudit = create_owner_from_user(
            user=cls.user,
        )

    def test__str__(self):
        """Test should return skill checker string representation."""
        skilllist = SkillList.objects.create(
            name="Test Skillplan",
            skill_list='{"Test Level 1": 1, "Test Level 5": 5, "Test Level 3": 3}',
            order_weight=1,
        )

        doctrine = Doctrine.objects.create(
            skilllist=skilllist, category="Test Category"
        )

        self.assertEqual(
            str(doctrine),
            f"{doctrine.skilllist.name} ({doctrine.skilllist.order_weight})",
        )

    def test_skillvalidator_is_valid(self):
        """Test should validate skills correctly."""
        # given
        sk_check = {
            "Mining Barge": 3,
        }

        result = skillvalidator(value=json.dumps(sk_check))

        self.assertIsNone(result)

    def test_skillvalidator_invalid_skill(self):
        """Test should raise ValidationError for invalid skill."""
        # given
        sk_check = {
            "Invalid Skill": 3,
        }

        with self.assertRaisesMessage(Exception, "Invalid Skill is not a valid skill."):
            skillvalidator(value=json.dumps(sk_check))

    def test_skillvalidator_invalid_level(self):
        """Test should raise ValidationError for invalid skill level."""
        # given
        sk_check = {
            "Mining Barge": 10,
        }

        with self.assertRaisesMessage(
            Exception, "Mining Barge level must be between 0 and 5."
        ):
            skillvalidator(value=json.dumps(sk_check))

    def test_skillvalidator_non_integer_level(self):
        """Test should raise ValidationError for non-integer skill level."""
        # given
        sk_check = {
            "Mining Barge": "high",
        }

        with self.assertRaisesMessage(
            Exception, "Mining Barge level must be an integer."
        ):
            skillvalidator(value=json.dumps(sk_check))

    def test_skillvalidator_invalid_json(self):
        """Test should raise ValidationError for invalid JSON."""
        # given
        sk_check = "Not a JSON string"

        with self.assertRaisesMessage(
            Exception, "Please provide a valid skill list in JSON format."
        ):
            skillvalidator(value=sk_check)

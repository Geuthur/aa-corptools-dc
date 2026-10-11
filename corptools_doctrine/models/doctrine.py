# Standard Library
import json

# Django
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from corptools.models.eve_models import EveItemType
from corptools.models.skills import SkillList

# AA CorpTools Doctrine
from corptools_doctrine import __title__
from corptools_doctrine.managers.doctrine_manager import DoctrineManager
from corptools_doctrine.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)


def skillvalidator(value):
    """
    Custom validator to check if the skill list is valid JSON.
    """
    try:
        skills = json.loads(value)
        for skill, level in skills.items():
            if not EveItemType.objects.filter(
                name=skill, group__category_id=16
            ).exists():
                raise ValidationError(
                    _("{skill} is not a valid skill.").format(skill=skill)
                )
            try:
                lvl = int(level)
            except ValueError as exc:
                raise ValidationError(
                    _("{skill} level must be an integer.").format(skill=skill)
                ) from exc
            if lvl < 0 or lvl > 5:
                raise ValidationError(
                    _("{skill} level must be between 0 and 5.").format(skill=skill)
                )
    except ValueError as exc:
        raise ValidationError(
            _("Please provide a valid skill list in JSON format.")
        ) from exc


class Doctrine(models.Model):
    objects: DoctrineManager = DoctrineManager()

    class Meta:
        default_permissions = ()
        db_table = "doctrinechecker_doctrine"
        indexes = [
            models.Index(fields=["category"], name="doctrineche_categor_42ee5d_idx"),
            models.Index(
                fields=["category", "skilllist"], name="ctdc_doc_cat_skill_idx"
            ),
            models.Index(
                fields=["skilllist", "category"], name="ctdc_doc_skill_cat_idx"
            ),
        ]

    skilllist = models.ForeignKey(
        SkillList,
        on_delete=models.CASCADE,
        verbose_name=_("Skill List"),
        help_text=_("The skill list to be used for this skill checker."),
    )
    category = models.CharField(
        max_length=20,
        null=True,
        default=None,
        verbose_name=_("Category"),
        help_text=_("Category of the skill list, used for grouping."),
    )

    def __str__(self):
        return f"{self.skilllist.name} ({self.skilllist.order_weight})"

    def get_skills(self) -> dict:
        """
        Return the skills defined in the associated SkillList as a dictionary.
        """
        return json.loads(self.skilllist.skill_list)

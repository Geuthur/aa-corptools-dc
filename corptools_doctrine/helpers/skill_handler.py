# Standard Library
import json
from hashlib import md5

# Third Party
from ninja import Schema

# Django
from django.apps import apps
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.html import format_html

# Alliance Auth
from allianceauth.authentication.models import CharacterOwnership

# Alliance Auth (External Libs)
from corptools.models.skills import Skill as CharacterSkill

# AA CorpTools Doctrine
from corptools_doctrine import __title__
from corptools_doctrine.api.schema import Character
from corptools_doctrine.app_settings import AA_CORPTOOLS_DOCTRINE_CACHE
from corptools_doctrine.models import Doctrine
from corptools_doctrine.providers import logger

SKILL_CACHE_TIMEOUT_SECONDS = 60 * 60 * 72  # 72 hours
SKILL_CACHE_HEADERS_KEY = "CTDC_SKILL_HEADER"
SKILL_CACHE_USER_KEY = "CTDC_SKILL_LISTS_{}"


def fittings_installed() -> bool:
    return apps.is_installed(app_name="fittings")


class DoctrineSchema(Schema):
    skills: dict
    order: int
    category: str
    html: str


class DoctrineResponseSchema(Schema):
    character: Character
    doctrines: list[DoctrineSchema]


class SkillListHandler:
    """handler for skill lists."""

    def _get_skill_list_hash(self, skills: list[str]) -> str:
        """Generate a hash for the skill list names."""
        return md5(",".join(str(x) for x in sorted(skills)).encode()).hexdigest()

    def _get_chars_hash(self, characters: list[int]) -> str:
        return md5(",".join(str(x) for x in sorted(characters)).encode()).hexdigest()

    def _build_account_cache_key(self, characters):
        """Build a cache key based on the character IDs."""
        return SKILL_CACHE_USER_KEY.format(self._get_chars_hash(characters))

    def _generate_doctrine_html(
        self,
        skill_list_name: str,
        character_id: int,
        has_missing_skills: bool,
        skill_list_pk: int = None,
    ) -> str:
        """Generate HTML for doctrine buttons based on skill status."""
        html = f"<div class='doctrine-item btn-group' role='group' data-doctrine='{skill_list_name}'>"
        html += "<button type='button' "

        if has_missing_skills:
            url = reverse(
                viewname="corptools_doctrine:api:get_missing_skills",
                kwargs={"character_id": character_id, "pk": skill_list_pk},
            )
            html += f"class='btn btn-danger btn-sm' data-bs-toggle='modal' data-bs-target='#corptools-request-doctrine-skills' data-action='{url}'>"
        else:
            html += "class='btn btn-success btn-sm'>"

        html += f"{skill_list_name}</button>"
        html += "<button type='button' class='flex-one btn "

        if has_missing_skills:
            html += f"btn-danger btn-sm' id='copy-{skill_list_name}-{character_id}'>"
            html += "<i class='fa-solid fa-copy'></i>"
        else:
            html += "btn-success btn-sm'>"
            html += "<i class='fa-solid fa-check'></i>"
        html += "</button></div>"

        return format_html(html)

    def check_skill_lists(self, doctrines: list[Doctrine], linked_characters):
        """Check if the skill lists are up to date."""
        skills = (
            CharacterSkill.objects.filter(
                character__character__character_id__in=list(linked_characters)
            )
            .select_related("skill_name", "skill_name__group", "character__character")
            .order_by("skill_name__name")
        )

        skill_dict = {}
        skill_list_dict = {}
        skill_list_misc = {}

        for skill in skills:
            character = skill.character.character.character_name
            skill_group = skill.skill_name.group.name

            # Create a new entry for the character if it doesn't exist
            if character not in skill_dict:
                skill_dict[character] = {
                    "character_id": skill.character.character.character_id,
                    "skills": {},
                }

            # Add the skill to the dictionary
            skill_dict[character]["skills"][skill.skill_name.name] = {
                "skill_group": skill_group,
                "sp_total": skill.skillpoints_in_skill,
                "active_level": skill.active_skill_level,
                "trained_level": skill.trained_skill_level,
            }

        # Get the skill lists and their skills
        for doctrine in doctrines:
            skill_list_dict[doctrine.skilllist.name] = doctrine.get_skills()
            skill_list_misc[doctrine.skilllist.name] = {}
            skill_list_misc[doctrine.skilllist.name]["pk"] = doctrine.pk
            skill_list_misc[doctrine.skilllist.name][
                "order-weight"
            ] = doctrine.skilllist.order_weight
            skill_list_misc[doctrine.skilllist.name]["category"] = doctrine.category

        for character, character_data in skill_dict.items():
            character_data["doctrines"] = {}
            for skill_list_name, skills in skill_list_dict.items():
                character_data["doctrines"][skill_list_name] = {}
                character_data["doctrines"][skill_list_name]["skills"] = {}
                for skill, level in skills.items():
                    level = int(level)
                    if level > character_data["skills"].get(skill, {}).get(
                        "active_level", 0
                    ):
                        character_data["doctrines"][skill_list_name]["skills"][
                            skill
                        ] = level

                # Add metadata for the doctrine
                character_data["doctrines"][skill_list_name]["order"] = skill_list_misc[
                    skill_list_name
                ]["order-weight"]
                character_data["doctrines"][skill_list_name]["category"] = (
                    skill_list_misc[skill_list_name]["category"]
                )

                has_missing_skills = bool(
                    character_data["doctrines"][skill_list_name]["skills"]
                )
                character_data["doctrines"][skill_list_name]["html"] = (
                    self._generate_doctrine_html(
                        skill_list_name=skill_list_name,
                        character_id=character_data["character_id"],
                        has_missing_skills=has_missing_skills,
                        skill_list_pk=skill_list_misc[skill_list_name]["pk"],
                    )
                )
        return skill_dict

    def get_accounts_skill_list(
        self, users: list[int], doctrines: QuerySet[Doctrine]
    ) -> dict:
        """Get the skill list for multiple users."""
        linked_characters = CharacterOwnership.objects.filter(user__in=users).values(
            "user_id", "character__character_name", "character__character_id"
        )

        skill_list_hash = self._get_skill_list_hash(
            doctrines.values_list("skilllist__name")
        )
        cached_header = cache.get(SKILL_CACHE_HEADERS_KEY, False)
        skill_lists_up_to_date = cached_header == skill_list_hash

        user_chars = {}
        for u in linked_characters:
            if u["user_id"] not in user_chars:
                user_chars[u["user_id"]] = {"chars": []}
            user_chars[u["user_id"]]["chars"].append(u["character__character_id"])

        for uid, character in user_chars.items():
            if skill_lists_up_to_date:
                cache_key = self._build_account_cache_key(character["chars"])
                cached_skills = cache.get(cache_key, False)

                if (
                    cached_skills is not False and AA_CORPTOOLS_DOCTRINE_CACHE
                ):  # check if cached at all?
                    cached_skills = json.loads(cached_skills)
                    if cached_skills.get("doctrines", False) != skill_list_hash:
                        character["data"] = self.get_skill_list(
                            user_id=uid, doctrines=doctrines
                        )
                    else:
                        character["data"] = cached_skills
                else:
                    character["data"] = self.get_skill_list(
                        user_id=uid, doctrines=doctrines
                    )
            else:
                character["data"] = self.get_skill_list(
                    user_id=uid, doctrines=doctrines
                )

        return user_chars

    def get_skill_list(
        self, user_id: int, doctrines: QuerySet[Doctrine], force_rebuild=True
    ) -> dict:
        """Get the skill list for a user."""
        linked_characters = (
            User.objects.get(id=user_id)
            .character_ownerships.all()
            .values_list("character__character_id", flat=True)
        )

        skill_list_hash = self._get_skill_list_hash(
            doctrines.values_list("skilllist__name")
        )
        cached_header = cache.get(SKILL_CACHE_HEADERS_KEY, False)
        skill_lists_up_to_date = cached_header == skill_list_hash

        account_key = self._build_account_cache_key(linked_characters)

        if skill_lists_up_to_date and not force_rebuild:
            cached_skills = cache.get(account_key, False)

            if cached_skills is not False and AA_CORPTOOLS_DOCTRINE_CACHE:
                logger.debug(
                    "Using cached skill list for user %s: %s",
                    user_id,
                    account_key,
                )
                cached_skills = json.loads(cached_skills)
                if cached_skills.get("doctrines", False) == skill_list_hash:
                    return cached_skills

        output = {
            "doctrines": skill_list_hash,
            "characters": account_key,
            "skills_list": self.check_skill_lists(doctrines, linked_characters),
        }

        output_json = json.dumps(output)

        # Cache the result if caching is enabled
        if AA_CORPTOOLS_DOCTRINE_CACHE:
            cache.set(
                account_key,
                output_json,
                SKILL_CACHE_TIMEOUT_SECONDS,
            )
            cache.set(SKILL_CACHE_HEADERS_KEY, skill_list_hash)
        return output

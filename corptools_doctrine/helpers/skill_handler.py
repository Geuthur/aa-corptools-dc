# Standard Library
from collections import defaultdict
from time import perf_counter

# Django
from django.contrib.auth.models import User
from django.db.models import QuerySet

# Alliance Auth
from allianceauth.authentication.models import CharacterOwnership

# Alliance Auth (External Libs)
from corptools.models.audits import CharacterAudit
from corptools.models.skills import Skill as CharacterSkill

# AA CorpTools Doctrine
from corptools_doctrine.api.schema import (
    CharacterDoctrineSchema,
    CharacterSchema,
    CharacterSkillListSchema,
    CharacterSkillsSchema,
    DoctrineSchema,
    DoctrineSkillsSchema,
)
from corptools_doctrine.helpers.eveonline import get_character_portrait_url
from corptools_doctrine.models import Doctrine
from corptools_doctrine.providers import logger


class SkillListHandler:
    """Handler for skill lists."""

    def get_skill_list_v2(
        self,
        user_id: int,
        doctrines: QuerySet[Doctrine] | list[Doctrine],
        target_character_ids: list[int] | None = None,
        include_character_skills: bool = True,
    ) -> CharacterSkillListSchema:
        """Get the skill list for a user without database caching."""
        user = User.objects.get(id=user_id)
        linked_characters = list(
            user.character_ownerships.all().select_related("character")
        )

        if target_character_ids is not None:
            eval_characters = [
                c
                for c in linked_characters
                if c.character.character_id in target_character_ids
            ]
        else:
            eval_characters = linked_characters

        characters = self.check_skill_lists_v2(
            doctrines=doctrines,
            linked_characters=eval_characters,
            include_character_skills=include_character_skills,
        )

        return CharacterSkillListSchema(
            characters=characters,
        )

    # pylint: disable=too-many-locals, too-many-positional-arguments, too-many-branches, too-many-arguments
    def check_skill_lists_v2(
        self,
        doctrines: list[Doctrine] | QuerySet[Doctrine],
        linked_characters: list[CharacterOwnership],
        include_skills: bool = True,
        skills_by_char: dict[int, list[CharacterSkill]] | None = None,
        parsed_doctrines: list[dict] | None = None,
        include_character_skills: bool = True,
        audited_char_ids: set[int] | None = None,
    ) -> list[CharacterDoctrineSchema]:
        """Check if the skill lists are satisfied using bulk queries."""
        response_character_skills: list[CharacterDoctrineSchema] = []
        if not linked_characters:
            return response_character_skills

        char_ids = [c.character.character_id for c in linked_characters]

        # Pre-parse doctrine skill requirements once if not provided
        if parsed_doctrines is None:
            parsed_doctrines = []
            for doctrine in doctrines:
                parsed_doctrines.append(
                    {
                        "doctrine": doctrine,
                        "skills": doctrine.get_skills() if include_skills else {},
                    }
                )

        required_skill_names = {
            skill_name
            for doc in parsed_doctrines
            for skill_name in doc["skills"].keys()
        }

        if skills_by_char is None:
            skills_filter = {
                "character__character__character_id__in": char_ids,
            }
            if not include_character_skills and required_skill_names:
                skills_filter["skill_name__name__in"] = required_skill_names

            all_skills = CharacterSkill.objects.filter(**skills_filter).select_related(
                "skill_name", "character__character"
            )

            skills_by_char = defaultdict(list)
            for skill in all_skills:
                cid = skill.character.character.character_id
                skills_by_char[cid].append(skill)

        for character in linked_characters:
            char_id = character.character.character_id
            if audited_char_ids is not None:
                if char_id not in audited_char_ids:
                    continue
            else:
                skills = skills_by_char.get(char_id, [])
                if not skills:
                    continue

            skills = skills_by_char.get(char_id, [])

            if include_character_skills:
                character_skills: list[CharacterSkillsSchema] = [
                    CharacterSkillsSchema(
                        name=skill.skill_name.name,
                        skill_group=(
                            skill.skill_name.group.name
                            if hasattr(skill.skill_name, "group")
                            else ""
                        ),
                        sp_total=skill.skillpoints_in_skill,
                        active_level=skill.active_skill_level,
                        trained_level=skill.trained_skill_level,
                    )
                    for skill in skills
                ]
                character_skills_lookup = {
                    skill.name: skill.active_level for skill in character_skills
                }
            else:
                character_skills = []
                character_skills_lookup = {
                    skill.skill_name.name: skill.active_skill_level for skill in skills
                }

            doctrines_list: list[DoctrineSchema] = []
            for doc_data in parsed_doctrines:
                doctrine = doc_data["doctrine"]
                doc_skills = doc_data["skills"]
                missing_skills: list[DoctrineSkillsSchema] = []

                if include_skills and doc_skills:
                    for skill_name, required_level in doc_skills.items():
                        required_level_int = int(required_level)
                        char_level = character_skills_lookup.get(skill_name, 0)

                        if char_level < required_level_int:
                            missing_skills.append(
                                DoctrineSkillsSchema(
                                    skill_name=skill_name,
                                    required_level=required_level_int,
                                )
                            )

                html_content = ""

                doctrines_list.append(
                    DoctrineSchema(
                        id=doctrine.pk,
                        name=doctrine.skilllist.name,
                        skills=missing_skills,
                        order=doctrine.skilllist.order_weight,
                        category=doctrine.category or "",
                        character_id=char_id,
                        html=html_content,
                    )
                )

            response_character_skills.append(
                CharacterDoctrineSchema(
                    character=CharacterSchema(
                        character_icon=get_character_portrait_url(
                            character_id=char_id,
                            as_html=True,
                        ),
                        character_name=character.character.character_name,
                        character_id=char_id,
                        corporation_id=character.character.corporation_id,
                        corporation_name=character.character.corporation_name,
                        alliance_id=character.character.alliance_id,
                        alliance_name=character.character.alliance_name,
                    ),
                    skills=character_skills,
                    doctrines=doctrines_list,
                )
            )
        return response_character_skills

    def get_accounts_skill_list_v2(
        self,
        users: list[User | int] | set[User | int],
        doctrines: QuerySet[Doctrine] | list[Doctrine],
    ) -> dict:
        """Get the skill list for multiple users using bulk queries."""
        endpoint_started = perf_counter()

        user_ids = [u.id if isinstance(u, User) else int(u) for u in users]
        if not user_ids:
            return {}

        linked_characters = list(
            CharacterOwnership.objects.filter(user_id__in=user_ids).select_related(
                "character"
            )
        )

        all_char_ids = [o.character.character_id for o in linked_characters]

        # Pre-parse doctrines once
        if hasattr(doctrines, "select_related"):
            doctrines_list = list(doctrines.select_related("skilllist"))
        else:
            doctrines_list = list(doctrines)

        parsed_doctrines = [
            {
                "doctrine": d,
                "skills": {k: int(v) for k, v in d.get_skills().items()},
            }
            for d in doctrines_list
        ]

        required_skill_names = {
            skill_name
            for doc in parsed_doctrines
            for skill_name in doc["skills"].keys()
        }

        # Bulk fetch only doctrine-required skills across all characters (no filesort, no unused group join)
        skills_filter = {
            "character__character__character_id__in": all_char_ids,
        }
        if required_skill_names:
            skills_filter["skill_name__name__in"] = required_skill_names

        all_skills = CharacterSkill.objects.filter(**skills_filter).select_related(
            "skill_name", "character__character"
        )

        skills_by_char: dict[int, list[CharacterSkill]] = defaultdict(list)
        for skill in all_skills:
            cid = skill.character.character.character_id
            skills_by_char[cid].append(skill)

        audited_char_ids = set(
            CharacterAudit.objects.filter(
                character__character_id__in=all_char_ids
            ).values_list("character__character_id", flat=True)
        )

        user_ownerships: dict[int, list[CharacterOwnership]] = defaultdict(list)
        user_char_ids: dict[int, list[int]] = defaultdict(list)
        for ownership in linked_characters:
            user_ownerships[ownership.user_id].append(ownership)
            user_char_ids[ownership.user_id].append(ownership.character.character_id)

        user_chars = {}
        for uid in user_ids:
            chars = user_ownerships.get(uid, [])
            cids = user_char_ids.get(uid, [])
            evaluated_chars = self.check_skill_lists_v2(
                doctrines=doctrines_list,
                linked_characters=chars,
                skills_by_char=skills_by_char,
                parsed_doctrines=parsed_doctrines,
                include_character_skills=False,
                audited_char_ids=audited_char_ids,
            )
            user_chars[uid] = {
                "chars": cids,
                "data": CharacterSkillListSchema(
                    characters=evaluated_chars,
                ),
            }

        total_time = round((perf_counter() - endpoint_started) * 1000, 2)
        logger.debug(
            "Generated bulk skill lists for %s users in %.2f ms",
            len(user_ids),
            total_time,
        )
        return user_chars

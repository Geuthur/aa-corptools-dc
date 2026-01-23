# Standard Library
from typing import Any

# Third Party
from ninja import NinjaAPI, Schema

# Django
from django.core.exceptions import ObjectDoesNotExist
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from corptools.api.helpers import get_alts_queryset
from corptools.models.audits import CharacterAudit as Character

# AA CorpTools Doctrine
from corptools_doctrine import __title__
from corptools_doctrine.api import schema
from corptools_doctrine.api.helpers import (
    _collect_user_doctrines,
    get_corporation,
    get_main_character,
)
from corptools_doctrine.helpers.skill_handler import SkillListHandler
from corptools_doctrine.models import Doctrine
from corptools_doctrine.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)
skills = SkillListHandler()


class MissingSkillsSchema(Schema):
    name: str
    trained_level: int
    needed_level: int


class DoctrineApiEndpoints:
    tags = ["Doctrine"]

    # pylint: disable=too-many-statements
    def __init__(self, api: NinjaAPI):
        @api.get(
            "{character_id}/doctrines/",
            response={200: list[schema.CharacterDoctrines], 403: str},
            tags=self.tags,
        )
        def get_doctrines(request, character_id: int):
            if character_id == 0:
                character_id = request.user.profile.main_character.character_id
            perms, main = get_main_character(request, character_id)

            if not perms:
                return 403, str(_("Permission Denied"))

            characters = get_alts_queryset(main)

            doctrines = Doctrine.objects.filter(skilllist__show_on_audit=True)

            # Get the skill lists for the main character
            skilllists = skills.get_skill_list(
                user_id=main.character_ownership.user_id, doctrines=doctrines
            )

            # Active skill lists are the ones that are visible in the UI
            visibles = list(
                Doctrine.objects.filter(skilllist__show_on_audit=True).values_list(
                    "skilllist__name", flat=True
                )
            )

            output = {}

            for character in characters:
                character: EveCharacter
                output[character.character_id] = {
                    "character": character,
                    "doctrines": {},
                    "skills": {},
                }

            for k, s in skilllists["skills_list"].items():
                for k, d in s["doctrines"].items():
                    if k in visibles:
                        output[s["character_id"]]["doctrines"][k] = d
                # Add skills to the character
                output[s["character_id"]]["skills"] = s["skills"]

            return list(output.values())

        @api.get(
            "{corporation_id}/doctrines/view/corporation/",
            response={200: list[schema.CorporationDoctrines], 403: str},
            tags=self.tags,
        )
        def get_corporation_doctrines(request: WSGIRequest, corporation_id: int):
            if corporation_id == 0:
                corporation_id = request.user.profile.main_character.corporation_id
            perm = get_corporation(request, corporation_id)[0]

            if not perm:
                return 403, str(_("Permission Denied"))

            # Get all characters in the corporation
            corporation_characters = Character.objects.filter(
                character__corporation_id=corporation_id,
            ).select_related(
                "character",
                "character__character_ownership",
                "character__character_ownership__user",
            )

            # Active skill lists are the ones that are visible in the UI
            doctrines = Doctrine.objects.filter(skilllist__show_on_audit=True)

            # Process corporation members and build character data
            users, main_characters, all_characters = self._process_corporation_members(
                corporation_characters
            )

            # Get skill lists for all users
            response_skill_list = skills.get_accounts_skill_list(
                users=users, doctrines=doctrines
            )
            # Process skill data for each user
            self._process_user_skills(
                response_skill_list, main_characters, all_characters, doctrines
            )

            return list(main_characters.values())

        @api.get(
            "{character_id}/doctrines/{pk}/",
            response={200: Any, 403: str},
            tags=self.tags,
        )
        def get_missing_skills(request, character_id: int, pk: int):
            if character_id == 0:
                character_id = request.user.profile.main_character.character_id
            response, character = get_main_character(request, character_id)

            if not response:
                return 403, str(_("Permission Denied"))

            doctrines = Doctrine.objects.filter(skilllist__show_on_audit=True)

            # Get the skill lists for the main character
            user_skilllists = skills.get_skill_list(
                user_id=character.character_ownership.user_id, doctrines=doctrines
            )

            missing_skills_response: list[MissingSkillsSchema] = []
            try:
                skill_checker = Doctrine.objects.get(pk=pk)
            except Doctrine.DoesNotExist:
                return render(
                    request,
                    "corptools_doctrine/partials/api/missing-skills.html",
                    context={"doctrine": None, "skills": missing_skills_response},
                )

            doctrine_skills = skill_checker.get_skills()

            # Find the character in the skill lists
            character_skills = self._find_character_skills(
                user_skilllists["skills_list"], character_id
            )

            if character_skills is None:
                return 403, _("Character not found in skill lists")

            for skill_name, skill_data in doctrine_skills.items():
                trained_level = 0
                if skill_name in character_skills:
                    trained_level = character_skills[skill_name].get("trained_level", 0)

                missing_skills_response.append(
                    MissingSkillsSchema(
                        name=skill_name,
                        trained_level=trained_level,
                        needed_level=skill_data,
                    )
                )

            context = {"doctrine": skill_checker, "skills": missing_skills_response}

            return render(
                request,
                "corptools_doctrine/partials/api/missing-skills.html",
                context=context,
            )

        @api.get(
            "doctrines/{pk}/",
            response={200: Any, 403: str},
            tags=self.tags,
        )
        def get_doctrine_skills(request, pk: int):
            perms = request.user.has_perm("corptools_doctrine.basic_access")

            if not perms:
                return 403, str(_("Permission Denied"))

            try:
                skilllist = Doctrine.objects.get(pk=pk)
            except Doctrine.DoesNotExist:
                return render(
                    request,
                    "corptools_doctrine/partials/api/doctrine.html",
                    context={"doctrine": None},
                )

            context = {"doctrine": skilllist}

            return render(
                request,
                "corptools_doctrine/partials/api/doctrine.html",
                context=context,
            )

    def _create_character_data(self, character: Character) -> dict[str, Any]:
        """Helper function to create character data."""
        return {
            "character_name": character.character_name,
            "character_id": character.character_id,
            "corporation_id": character.corporation_id,
            "corporation_name": character.corporation_name,
            "alliance_id": character.alliance_id,
            "alliance_name": character.alliance_name,
        }

    def _process_corporation_members(self, corporation_characters: list[Character]):
        """Process corporation members and build character data structures."""
        users = set()
        main_characters = {}
        all_characters = {}

        # Create a dictionary to hold all characters
        for member in corporation_characters:
            # Store all character data for later use
            all_characters[member.character.character_id] = self._create_character_data(
                member.character
            )

            try:
                assert member.character.character_ownership.user.profile.main_character
            except AssertionError:
                continue
            except ObjectDoesNotExist:
                continue

            # Process users with main characters
            if member.character.character_ownership.user.profile.main_character:
                users.add(member.character.character_ownership.user)
                main_char = (
                    member.character.character_ownership.user.profile.main_character
                )

                # Only add if we haven't processed this main character yet
                if main_char.character_id not in main_characters:
                    main_characters[main_char.character_id] = {
                        "user_id": member.character.character_ownership.user.id,
                        "character": self._create_character_data(main_char),
                        "alts": [],
                        "doctrines": {},
                    }

        return users, main_characters, all_characters

    def _process_user_skills(
        self,
        response_skill_list: dict,
        main_characters,
        all_characters: dict,
        doctrines: list[QuerySet[Doctrine]],
    ):
        """Process skill data for each user."""
        corp_character_ids = set(all_characters.keys())

        for user_id, corp_data in response_skill_list.items():
            if not ("data" in corp_data and "skills_list" in corp_data["data"]):
                continue

            # Filter to corporation characters only
            corp_skills_list = {
                char_key: char_data
                for char_key, char_data in corp_data["data"]["skills_list"].items()
                if char_data["character_id"] in corp_character_ids
            }

            if not corp_skills_list:
                continue

            # Find the main character for this user
            main_char_id = self._find_main_character_id(main_characters, user_id)

            if main_char_id and main_char_id in main_characters:
                # Collect doctrines
                user_doctrines = _collect_user_doctrines(corp_skills_list, doctrines)
                main_characters[main_char_id]["doctrines"] = user_doctrines

                # Collect alts (all corp characters except main)
                alts = [
                    all_characters[char_data["character_id"]]
                    for char_data in corp_skills_list.values()
                    if char_data["character_id"] != main_char_id
                ]
                main_characters[main_char_id]["alts"] = alts

    def _find_main_character_id(self, main_characters, user_id):
        """Find the main character ID for a given user ID."""
        for char_id, char_data in main_characters.items():
            if char_data["user_id"] == user_id:
                return char_id
        return None

    def _find_character_skills(self, skills_list: dict, character_id: int) -> dict:
        """Find character skills in the skills list."""
        for character_data in skills_list.values():
            if character_data["character_id"] == character_id:
                return character_data["skills"]
        return None

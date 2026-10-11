# Standard Library
from collections import defaultdict
from time import perf_counter
from typing import Any

# Third Party
from ninja import NinjaAPI, Query

# Django
from django.core.exceptions import ObjectDoesNotExist
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q, QuerySet
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.authentication.models import CharacterOwnership
from allianceauth.eveonline.models import EveCharacter
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from corptools.api.helpers import get_alts_queryset
from corptools.models.audits import CharacterAudit as Character
from corptools.models.skills import Skill

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


class DoctrineApiEndpoints:
    tags = ["Doctrine"]

    # pylint: disable=too-many-statements
    def __init__(self, api: NinjaAPI):
        @api.get(
            "{character_id}/doctrines/",
            response={200: list[schema.CharacterDoctrines], 403: str},
            tags=self.tags,
        )
        # pylint: disable=too-many-locals
        def get_doctrines(
            request,
            character_id: int,
            target_character_id: int | None = None,
            all_characters: bool = False,
        ):
            if character_id == 0:
                character_id = request.user.profile.main_character.character_id
            perms, main = get_main_character(request, character_id)

            if not perms:
                return 403, str(_("Permission Denied"))

            characters = get_alts_queryset(main)
            doctrines = Doctrine.objects.filter(skilllist__show_on_audit=True)

            if all_characters:
                target_ids = None
            elif target_character_id is not None:
                target_ids = [target_character_id]
            else:
                target_ids = [character_id]

            # Get the skill lists for the evaluated character(s)
            character_skills_list = skills.get_skill_list_v2(
                user_id=main.character_ownership.user_id,
                doctrines=doctrines,
                target_character_ids=target_ids,
                include_character_skills=False,
            )

            # Active skill lists are the ones that are visible in the UI
            visibles = set(doctrines.values_list("skilllist__name", flat=True))

            # Map evaluated doctrines by character_id
            eval_doctrines_by_char: dict[int, dict] = {}
            for char in character_skills_list.characters:
                char_doctrines = {}
                for doctrine in char.doctrines:
                    if doctrine.name in visibles:
                        char_doctrines[doctrine.name] = (
                            doctrine.model_dump()
                            if hasattr(doctrine, "model_dump")
                            else doctrine
                        )
                eval_doctrines_by_char[char.character.character_id] = char_doctrines

            response_doctrine_list: list[schema.CharacterDoctrines] = []
            # Initialize response with all characters and populated doctrines
            for character_obj in characters:
                character_obj: EveCharacter
                cid = character_obj.character_id
                response_doctrine_list.append(
                    schema.CharacterDoctrines(
                        character=schema.CharacterSchema(
                            character_icon=None,
                            character_name=character_obj.character_name,
                            character_id=cid,
                            corporation_id=character_obj.corporation_id,
                            corporation_name=character_obj.corporation_name,
                            alliance_id=character_obj.alliance_id,
                            alliance_name=character_obj.alliance_name,
                        ),
                        doctrines=eval_doctrines_by_char.get(cid, {}),
                    )
                )

            return response_doctrine_list

        @api.get(
            "{corporation_id}/doctrines/members/",
            response={200: schema.CorporationMembersResponse, 403: str},
            tags=self.tags,
        )
        def get_corporation_members_list(request: WSGIRequest, corporation_id: int):
            if corporation_id == 0:
                corporation_id = request.user.profile.main_character.corporation_id
            perm, corp_obj = get_corporation(request, corporation_id)

            if not perm or not corp_obj:
                return 403, str(_("Permission Denied"))

            corp_char_pks = list(
                EveCharacter.objects.filter(corporation_id=corporation_id).values_list(
                    "id", flat=True
                )
            )

            corporation_characters = Character.objects.filter(
                character_id__in=corp_char_pks,
            ).select_related(
                "character",
                "character__character_ownership",
                "character__character_ownership__user",
                "character__character_ownership__user__profile",
                "character__character_ownership__user__profile__main_character",
            )

            doctrines = Doctrine.objects.filter(
                skilllist__show_on_audit=True
            ).select_related("skilllist")

            _users, main_characters, _all_chars = self._process_corporation_members(
                corporation_characters
            )

            members = [
                schema.CorporationMemberOverview(
                    character=schema.CharacterSchema(
                        character_icon=None,
                        character_name=data["character"]["character_name"],
                        character_id=data["character"]["character_id"],
                        corporation_id=data["character"]["corporation_id"],
                        corporation_name=data["character"]["corporation_name"],
                        alliance_id=data["character"].get("alliance_id"),
                        alliance_name=data["character"].get("alliance_name"),
                    ),
                    alts=(
                        [
                            schema.CharacterSchema(
                                character_icon=None,
                                character_name=alt["character_name"],
                                character_id=alt["character_id"],
                                corporation_id=alt["corporation_id"],
                                corporation_name=alt["corporation_name"],
                                alliance_id=alt.get("alliance_id"),
                                alliance_name=alt.get("alliance_name"),
                            )
                            for alt in data.get("alts", [])
                        ]
                        if data.get("alts")
                        else None
                    ),
                )
                for data in main_characters.values()
            ]

            active_doctrines = [
                schema.ActiveDoctrineOverview(
                    id=d.pk,
                    name=d.skilllist.name,
                    category=d.category or "",
                    order=d.skilllist.order_weight,
                )
                for d in doctrines
            ]

            return 200, schema.CorporationMembersResponse(
                corporation_id=corp_obj.corporation_id,
                corporation_name=corp_obj.corporation_name,
                members=members,
                doctrines=active_doctrines,
            )

        @api.post(
            "{corporation_id}/doctrines/audit-members/",
            response={200: list[schema.CorporationDoctrines], 403: str},
            tags=self.tags,
        )
        def audit_corporation_members(
            request: WSGIRequest,
            corporation_id: int,
            data: schema.AuditMembersRequest,
        ):
            if corporation_id == 0:
                corporation_id = request.user.profile.main_character.corporation_id
            perm = get_corporation(request, corporation_id)[0]

            if not perm:
                return 403, str(_("Permission Denied"))

            return 200, self._audit_corporation_members(
                corporation_id=corporation_id,
                character_ids=data.character_ids if data else None,
                filters=data.to_filter() if data else None,
            )

        @api.get(
            "{corporation_id}/doctrines/view/corporation/",
            response={200: list[schema.CorporationDoctrines], 403: str},
            tags=self.tags,
        )
        def get_corporation_doctrines(
            request: WSGIRequest,
            corporation_id: int,
            filters: schema.DoctrineAuditFilter = Query(...),
        ):
            if corporation_id == 0:
                corporation_id = request.user.profile.main_character.corporation_id
            perm = get_corporation(request, corporation_id)[0]

            if not perm:
                return 403, str(_("Permission Denied"))

            return 200, self._audit_corporation_members(
                corporation_id=corporation_id,
                filters=filters,
            )

        @api.get(
            "{character_id}/doctrines/{pk}/",
            response={200: schema.MissingSkillsResponse, 403: dict, 404: dict},
            tags=self.tags,
        )
        # pylint: disable=too-many-locals
        def get_missing_skills(request: WSGIRequest, character_id: int, pk: int):
            if character_id == 0:
                character_id = request.user.profile.main_character.character_id
            response = get_main_character(request, character_id)[0]

            if not response:
                return 403, {"error": str(_("Permission Denied"))}

            try:
                skill_checker = Doctrine.objects.select_related("skilllist").get(pk=pk)
            except Doctrine.DoesNotExist:
                return 404, {"error": str(_("Doctrine not found"))}

            # Get the skills required for the doctrine
            doctrine_skills = skill_checker.get_skills()

            # Get character audit and skills
            char_obj = EveCharacter.objects.filter(character_id=character_id).first()
            char_name = char_obj.character_name if char_obj else str(character_id)

            audit_id = (
                Character.objects.filter(character_id=char_obj.id)
                .values_list("id", flat=True)
                .first()
                if char_obj
                else None
            )

            character_skills = (
                list(
                    Skill.objects.filter(character_id=audit_id).select_related(
                        "skill_name"
                    )
                )
                if audit_id
                else []
            )

            missing_skills_list: list[schema.MissingSkillDetail] = []
            clipboard_lines: list[str] = []

            for skill_name, skill_data in doctrine_skills.items():
                needed_level = int(skill_data)
                trained_level = 0
                for skill in character_skills:
                    if skill_name in (skill.skill_name.name_en, skill.skill_name.name):
                        trained_level = skill.trained_skill_level
                        break

                if trained_level < needed_level:
                    missing_skills_list.append(
                        schema.MissingSkillDetail(
                            name=skill_name,
                            trained_level=trained_level,
                            needed_level=needed_level,
                        )
                    )
                    clipboard_lines.append(f"{skill_name} {needed_level}")

            return 200, schema.MissingSkillsResponse(
                character_id=character_id,
                character_name=char_name,
                doctrine_id=skill_checker.pk,
                doctrine_name=skill_checker.skilllist.name,
                missing_skills=missing_skills_list,
                clipboard_export="\n".join(clipboard_lines),
            )

        @api.get(
            "doctrines/{pk}/",
            response={200: schema.DoctrineDetailResponse, 403: dict, 404: dict},
            tags=self.tags,
        )
        # pylint: disable=too-many-nested-blocks
        def get_doctrine_skills(
            request: WSGIRequest, pk: int, character_id: int | None = None
        ):
            perms = request.user.has_perm("corptools_doctrine.basic_access")

            if not perms:
                return 403, {"error": str(_("Permission Denied"))}

            try:
                skilllist = Doctrine.objects.select_related("skilllist").get(pk=pk)
            except Doctrine.DoesNotExist:
                return 404, {"error": str(_("Doctrine not found"))}

            character_skills_dict: dict[str, int] | None = None
            if character_id:
                char_perm = get_main_character(request, character_id)[0]
                if char_perm:
                    char_obj = EveCharacter.objects.filter(
                        character_id=character_id
                    ).first()
                    if char_obj:
                        audit_id = (
                            Character.objects.filter(character_id=char_obj.id)
                            .values_list("id", flat=True)
                            .first()
                        )
                        if audit_id:
                            character_skills_dict = {}
                            skills_qs = Skill.objects.filter(
                                character_id=audit_id
                            ).select_related("skill_name")
                            for s in skills_qs:
                                lvl = max(s.active_skill_level, s.trained_skill_level)
                                if s.skill_name.name_en:
                                    character_skills_dict[s.skill_name.name_en] = lvl
                                if s.skill_name.name:
                                    character_skills_dict[s.skill_name.name] = lvl

            return 200, schema.DoctrineDetailResponse(
                id=skilllist.pk,
                name=skilllist.skilllist.name,
                category=skilllist.category,
                order_weight=skilllist.skilllist.order_weight,
                show_on_audit=skilllist.skilllist.show_on_audit,
                skills={k: int(v) for k, v in skilllist.get_skills().items()},
                character_skills=character_skills_dict,
            )

    def _audit_corporation_members(
        self,
        corporation_id: int,
        character_ids: list[int] | None = None,
        filters: schema.DoctrineAuditFilter | None = None,
    ) -> list[dict[str, Any]]:
        """Audit corporation members for active doctrines, optionally filtered by character IDs or DoctrineAuditFilter."""
        if character_ids is not None and len(character_ids) == 0:
            return []

        eve_chars = EveCharacter.objects.filter(corporation_id=corporation_id)
        if character_ids is not None:
            user_ids = list(
                CharacterOwnership.objects.filter(
                    character__character_id__in=character_ids
                ).values_list("user_id", flat=True)
            )
            eve_chars = eve_chars.filter(
                Q(character_ownership__user_id__in=user_ids)
                | Q(character_id__in=character_ids)
            )

        corp_char_pks = list(eve_chars.values_list("id", flat=True))

        corporation_characters = Character.objects.filter(
            character_id__in=corp_char_pks,
        ).select_related(
            "character",
            "character__character_ownership",
            "character__character_ownership__user",
            "character__character_ownership__user__profile",
            "character__character_ownership__user__profile__main_character",
        )

        filter_obj = filters or schema.DoctrineAuditFilter()
        doctrines = filter_obj.get_doctrines()

        users, main_characters, all_characters = self._process_corporation_members(
            corporation_characters
        )

        response_skill_list = skills.get_accounts_skill_list_v2(
            users=users, doctrines=doctrines
        )
        self._process_user_skills_v2(
            response_skill_list, main_characters, all_characters, doctrines
        )

        return list(main_characters.values())

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

    def _process_corporation_members(self, corporation_members: list[Character]):
        """Process corporation members and build character data structures."""
        users = set()
        main_characters = {}
        all_characters = {}
        user_characters = defaultdict(list)

        # Create a dictionary to hold all characters
        for member in corporation_members:
            # Store all character data for later use
            all_characters[member.character.character_id] = self._create_character_data(
                member.character
            )

            # Check if the user has a main character and skip if not, since we won't be able to link them to a user account for skill retrieval
            try:
                assert member.character.character_ownership.user.profile.main_character
            except (AssertionError, ObjectDoesNotExist):
                continue

            # Process users with main characters
            user = member.character.character_ownership.user
            if user.profile.main_character:
                users.add(user.id)
                main_char = user.profile.main_character
                user_characters[user.id].append(member.character.character_id)

                # Ensure main character is stored in all_characters
                if main_char.character_id not in all_characters:
                    all_characters[main_char.character_id] = (
                        self._create_character_data(main_char)
                    )

                # Only add if we haven't processed this main character yet
                if main_char.character_id not in main_characters:
                    main_characters[main_char.character_id] = {
                        "user_id": user.id,
                        "character": self._create_character_data(main_char),
                        "alts": [],
                        "doctrines": {},
                    }

        # Populate corporation alts for each main character
        for main_char_id, main_char_data in main_characters.items():
            uid = main_char_data["user_id"]
            main_char_data["alts"] = [
                all_characters[cid]
                for cid in user_characters[uid]
                if cid != main_char_id and cid in all_characters
            ]

        return users, main_characters, all_characters

    # pylint: disable=too-many-locals
    def _process_user_skills_v2(
        self,
        response_skill_list: dict,
        main_characters: dict[int, dict[str, Any]],
        all_characters: dict[int, dict[str, Any]],
        doctrines: list[Doctrine] | QuerySet[Doctrine] | set[str] | frozenset[str],
    ):
        """Process skill data for each user with optimized caching and fast serialization."""
        processing_started = perf_counter()
        corp_character_ids = set(all_characters.keys())
        main_characters_by_user_id = {
            char_data["user_id"]: char_id
            for char_id, char_data in main_characters.items()
        }

        if isinstance(doctrines, (set, frozenset)):
            active_doctrine_names = doctrines
        elif hasattr(doctrines, "values_list"):
            active_doctrine_names = frozenset(
                doctrines.values_list("skilllist__name", flat=True)
            )
        elif isinstance(doctrines, (list, tuple)):
            active_doctrine_names = frozenset(
                (
                    d.skilllist.name
                    if hasattr(d, "skilllist")
                    else getattr(d, "name", str(d))
                )
                for d in doctrines
            )
        else:
            active_doctrine_names = frozenset()

        processed_users = 0
        users_with_corp_chars = 0

        for raw_user_id, corp_data in response_skill_list.items():
            processed_users += 1
            data_obj = (
                corp_data.get("data")
                if isinstance(corp_data, dict)
                else getattr(corp_data, "data", None)
            )
            if not data_obj:
                continue

            characters = getattr(data_obj, "characters", None) or (
                data_obj.get("characters") if isinstance(data_obj, dict) else None
            )
            if not characters:
                continue

            user_id = raw_user_id.id if hasattr(raw_user_id, "id") else int(raw_user_id)
            main_char_id = main_characters_by_user_id.get(user_id)
            if not main_char_id or main_char_id not in main_characters:
                continue

            # Filter to corporation characters and collect alts in a single fast pass
            corp_skills_list = {}
            corp_alt_ids = []
            for char_data in characters:
                char_id = (
                    char_data.character.character_id
                    if hasattr(char_data, "character")
                    else char_data.get("character", {}).get("character_id")
                )
                if char_id in corp_character_ids:
                    corp_skills_list[char_id] = char_data
                    if char_id != main_char_id and char_id in all_characters:
                        corp_alt_ids.append(char_id)

            if not corp_skills_list:
                continue
            users_with_corp_chars += 1

            # Collect best doctrines for this user across their corp characters
            user_doctrines = self._collect_user_doctrines(
                corp_skills_list, active_doctrine_names
            )

            # Store doctrines pre-converted to dicts to accelerate Ninja response serialization
            main_characters[main_char_id]["doctrines"] = {
                name: (doc.model_dump() if hasattr(doc, "model_dump") else doc)
                for name, doc in user_doctrines.items()
            }

            # Set corp alts for main character
            main_characters[main_char_id]["alts"] = [
                all_characters[cid] for cid in corp_alt_ids
            ]

        processing_ms = round((perf_counter() - processing_started) * 1000, 2)
        logger.debug(
            "Corp doctrines timing: process_user_skills=%sms users_seen=%s users_with_corp_chars=%s",
            processing_ms,
            processed_users,
            users_with_corp_chars,
        )

    def _collect_user_doctrines(
        self, corp_skills_list: dict, active_doctrine_names: set[str]
    ) -> dict:
        """Collect the best doctrine skill data for the user across all their characters."""
        return _collect_user_doctrines(corp_skills_list, active_doctrine_names)

"""Manage API endpoints for AA CorpTools Doctrine Checker."""

# Standard Library
import json

# Third Party
from ninja import NinjaAPI

# Django
from django.core.handlers.wsgi import WSGIRequest
from django.db import transaction
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.authentication.models import UserProfile
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from corptools.models.audits import CharacterAudit, CorporationAudit
from corptools.models.skills import SkillList

# AA CorpTools Doctrine
from corptools_doctrine import __title__, forms
from corptools_doctrine.api import schema
from corptools_doctrine.api.helpers import get_manage_permission
from corptools_doctrine.helpers.eveonline import (
    get_alliance_logo_url,
    get_character_portrait_url,
    get_corporation_logo_url,
)
from corptools_doctrine.models import Doctrine
from corptools_doctrine.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)


class CharacterOverviewSchema(schema.CharacterSchema):
    actions: str | None = None


class CorporationOverviewSchema(schema.CorporationSchema):
    actions: str | None = None


class ManageApiEndpoints:
    tags = ["Manage Doctrine"]

    # pylint: disable=too-many-statements
    def __init__(self, api: NinjaAPI):
        @api.get(
            "manage/",
            response={200: list[schema.ManageDoctrineSchema], 403: str},
            tags=self.tags,
            summary="List all doctrines for management",
        )
        def manage_doctrines(request: WSGIRequest):
            """
            Manage Doctrines.

            Retrieves a list of doctrines that the user has permission to manage.
            """
            main_char = getattr(
                getattr(request.user, "profile", None), "main_character", None
            )
            if not main_char:
                return 403, str(_("Permission Denied"))

            has_perm = get_manage_permission(request, main_char.character_id)[0]
            if not has_perm:
                return 403, str(_("Permission Denied"))

            doctrine_qs = (
                Doctrine.objects.select_related("skilllist")
                .all()
                .order_by("skilllist__order_weight", "skilllist__name")
            )

            response_doctrines_list: list[schema.ManageDoctrineSchema] = []
            for doctrine in doctrine_qs:
                try:
                    skills_dict = doctrine.get_skills()
                    skill_count = len(skills_dict)
                except Exception:  # pylint: disable=broad-exception-caught
                    skill_count = 0

                response_doctrines_list.append(
                    schema.ManageDoctrineSchema(
                        id=doctrine.pk,
                        name=doctrine.skilllist.name,
                        category=doctrine.category,
                        order_weight=doctrine.skilllist.order_weight,
                        show_on_audit=doctrine.skilllist.show_on_audit,
                        skill_count=skill_count,
                    )
                )
            return 200, response_doctrines_list

        @api.post(
            "manage/doctrine/",
            response={200: schema.ManageDoctrineSchema, 400: dict, 403: dict},
            tags=self.tags,
            summary="Create a new doctrine",
        )
        def create_doctrine(
            request: WSGIRequest, payload: schema.DoctrineCreateRequest
        ):
            """Create a new doctrine from a skill list."""
            main_char = getattr(
                getattr(request.user, "profile", None), "main_character", None
            )
            if (
                not main_char
                or not get_manage_permission(request, main_char.character_id)[0]
            ):
                return 403, {"message": str(_("Permission Denied"))}

            form = forms.SkillListForm(
                {
                    "name": payload.name,
                    "category": payload.category or "",
                    "order_weight": payload.order_weight,
                    "skill_list": payload.skill_list,
                }
            )
            if not form.is_valid():
                errors = [
                    str(err)
                    for error_list in form.errors.values()
                    for err in error_list
                ]
                return 400, {"message": " ".join(errors)}

            parsed_skills = form.get_parsed_skills()
            if not parsed_skills:
                return 400, {
                    "message": str(_("Your skill plan is empty. Please add skills."))
                }

            with transaction.atomic():
                skilllist = SkillList.objects.create(
                    name=form.cleaned_data["name"],
                    skill_list=json.dumps(parsed_skills, ensure_ascii=False),
                    order_weight=form.cleaned_data["order_weight"],
                )
                doctrine = Doctrine.objects.create(
                    skilllist=skilllist,
                    category=form.cleaned_data["category"] or None,
                )

            logger.info(
                f"Doctrine '{doctrine.skilllist.name}' (ID: {doctrine.pk}) created by '{request.user.username}'."
            )
            return 200, schema.ManageDoctrineSchema(
                id=doctrine.pk,
                name=doctrine.skilllist.name,
                category=doctrine.category,
                order_weight=doctrine.skilllist.order_weight,
                show_on_audit=doctrine.skilllist.show_on_audit,
                skill_count=len(parsed_skills),
            )

        @api.put(
            "manage/doctrine/{pk}/",
            response={
                200: schema.ManageDoctrineSchema,
                400: dict,
                403: dict,
                404: dict,
            },
            tags=self.tags,
            summary="Update an existing doctrine",
        )
        def update_doctrine(
            request: WSGIRequest, pk: int, payload: schema.DoctrineUpdateRequest
        ):
            """Update doctrine category, order weight, visibility, or name."""
            main_char = getattr(
                getattr(request.user, "profile", None), "main_character", None
            )
            if (
                not main_char
                or not get_manage_permission(request, main_char.character_id)[0]
            ):
                return 403, {"message": str(_("Permission Denied"))}

            try:
                doctrine = Doctrine.objects.select_related("skilllist").get(pk=pk)
            except Doctrine.DoesNotExist:
                return 404, {"message": str(_("Doctrine not found"))}

            with transaction.atomic():
                if payload.name is not None and payload.name.strip():
                    new_name = payload.name.strip()
                    existing = SkillList.objects.filter(name__iexact=new_name).exclude(
                        pk=doctrine.skilllist.pk
                    )
                    if existing.exists():
                        return 400, {
                            "message": str(
                                _("Skill list with this name already exists")
                            )
                        }
                    doctrine.skilllist.name = new_name

                if payload.category is not None:
                    doctrine.category = (
                        payload.category.strip() if payload.category else None
                    )

                if payload.order_weight is not None:
                    if payload.order_weight < 0 or payload.order_weight >= 1000:
                        return 400, {
                            "message": str(_("Order weight must be between 0 and 999"))
                        }
                    doctrine.skilllist.order_weight = payload.order_weight

                if payload.show_on_audit is not None:
                    doctrine.skilllist.show_on_audit = payload.show_on_audit

                doctrine.skilllist.save()
                doctrine.save()

            try:
                skill_count = len(doctrine.get_skills())
            except Exception:  # pylint: disable=broad-exception-caught
                skill_count = 0

            logger.info(
                f"Doctrine (ID: {pk}) updated by user '{request.user.username}'."
            )
            return 200, schema.ManageDoctrineSchema(
                id=doctrine.pk,
                name=doctrine.skilllist.name,
                category=doctrine.category,
                order_weight=doctrine.skilllist.order_weight,
                show_on_audit=doctrine.skilllist.show_on_audit,
                skill_count=skill_count,
            )

        @api.delete(
            "manage/doctrine/{pk}/",
            response={200: dict, 403: dict, 404: dict},
            tags=self.tags,
            summary="Delete a doctrine",
        )
        def delete_doctrine(request: WSGIRequest, pk: int):
            """Delete a doctrine and its associated skilllist."""
            main_char = getattr(
                getattr(request.user, "profile", None), "main_character", None
            )
            if (
                not main_char
                or not get_manage_permission(request, main_char.character_id)[0]
            ):
                return 403, {"success": False, "message": str(_("Permission Denied"))}

            try:
                doctrine = Doctrine.objects.select_related("skilllist").get(pk=pk)
                with transaction.atomic():
                    doctrine.skilllist.delete()
                    doctrine.delete()
                logger.info(
                    f"Doctrine (ID: {pk}) deleted by user '{request.user.username}'."
                )
                return 200, {
                    "success": True,
                    "message": str(_("Doctrine deleted successfully.")),
                }
            except Doctrine.DoesNotExist:
                return 404, {
                    "success": False,
                    "message": str(_("Doctrine not found.")),
                }

        @api.get(
            "account/overview/",
            response={200: list[CharacterOverviewSchema], 403: dict},
            tags=self.tags,
            summary="Overview of characters with doctrines",
        )
        def get_account_overview(request: WSGIRequest):
            """Get an overview of characters with doctrines."""
            chars_visible = Doctrine.objects.visible_eve_characters(request.user)

            if chars_visible is None:
                return 403, {"message": str(_("Permission Denied"))}

            chars_ids = chars_visible.values_list("character_id", flat=True)

            accounts = UserProfile.objects.filter(
                main_character__isnull=False,
                main_character__character_id__in=chars_ids,
            ).select_related(
                "main_character",
            )

            response_character_list: list[CharacterOverviewSchema] = []
            for account in accounts:
                if account.main_character is None:
                    continue
                char = account.main_character
                response_character_list.append(
                    CharacterOverviewSchema(
                        character_icon=get_character_portrait_url(
                            character_id=char.character_id,
                            size=32,
                            character_name=char.character_name,
                            as_html=False,
                        ),
                        character_name=char.character_name,
                        character_id=char.character_id,
                        corporation_id=char.corporation_id,
                        corporation_name=char.corporation_name,
                        alliance_id=char.alliance_id,
                        alliance_name=char.alliance_name,
                        actions=f"/doctrine/{char.character_id}/",
                    )
                )
            return 200, response_character_list

        @api.get(
            "corporation/overview/",
            response={200: list[CorporationOverviewSchema], 403: dict},
            tags=self.tags,
            summary="Overview of corporations with doctrines",
        )
        def get_corporation_overview(request: WSGIRequest):
            """Get an overview of corporations with doctrines."""
            doctrine_visible = Doctrine.objects.visible_eve_corporations(request.user)

            if doctrine_visible is None:
                return 403, {"message": str(_("Permission Denied"))}

            corp_ids = doctrine_visible.distinct().values_list(
                "corporation_id", flat=True
            )

            existing_corp_ids = (
                CharacterAudit.objects.filter(
                    character__corporation_id__in=corp_ids,
                )
                .select_related("character")
                .distinct()
                .values_list("character__corporation_id", flat=True)
            )

            corporations = CorporationAudit.objects.filter(
                corporation__corporation_id__in=existing_corp_ids,
            ).select_related(
                "corporation",
                "corporation__alliance",
            )

            response_corporation_list: list[CorporationOverviewSchema] = []
            for corporation in corporations:
                alliance_id = getattr(
                    corporation.corporation.alliance, "alliance_id", None
                )
                alliance_name = getattr(
                    corporation.corporation.alliance, "alliance_name", ""
                )
                response_corporation_list.append(
                    CorporationOverviewSchema(
                        corporation_icon=get_corporation_logo_url(
                            corporation_id=corporation.corporation.corporation_id,
                            size=32,
                            corporation_name=corporation.corporation.corporation_name,
                            as_html=False,
                        ),
                        corporation_id=corporation.corporation.corporation_id,
                        corporation_name=corporation.corporation.corporation_name,
                        alliance_icon=(
                            get_alliance_logo_url(
                                alliance_id=alliance_id,
                                size=32,
                                alliance_name=alliance_name,
                                as_html=False,
                            )
                            if alliance_id
                            else None
                        ),
                        alliance_id=alliance_id,
                        alliance_name=alliance_name,
                        actions=f"/corporation/{corporation.corporation.corporation_id}/",
                    )
                )
            return 200, response_corporation_list

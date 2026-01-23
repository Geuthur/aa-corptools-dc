# Standard Library
from typing import Any

# Third Party
from jsonschema import ValidationError
from ninja import NinjaAPI, Schema

# Django
from django.core.handlers.wsgi import WSGIRequest
from django.db import transaction
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.authentication.models import UserProfile
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from corptools.models.audits import CharacterAudit, CorporationAudit
from corptools.models.skills import SkillList

# AA CorpTools Doctrine
from corptools_doctrine import __title__
from corptools_doctrine.api import schema
from corptools_doctrine.api.helpers import (
    get_manage_permission,
)
from corptools_doctrine.helpers.eveonline import (
    get_alliance_logo_url,
    get_character_portrait_url,
    get_corporation_logo_url,
)
from corptools_doctrine.helpers.icons import (
    generate_edit_active_html,
    generate_edit_category_html,
    generate_edit_name_html,
    generate_edit_order_weight_html,
    get_doctrine_delete_button,
    get_doctrine_skills_button,
)
from corptools_doctrine.models import Doctrine
from corptools_doctrine.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)


class DataTableSchema(Schema):
    html: str
    sort: Any
    filter: str | None = None


class DoctrineOverviewSchema(Schema):
    name: DataTableSchema
    skills: DataTableSchema
    active: DataTableSchema
    ordering: DataTableSchema
    category: DataTableSchema
    actions: Any


class CharacterOverviewSchema(schema.Character):
    actions: Any


class CorporationOverviewSchema(schema.Corporation):
    actions: Any


class ManageApiEndpoints:
    tags = ["Manage Doctrine"]

    # pylint: disable=too-many-statements
    def __init__(self, api: NinjaAPI):
        @api.get(
            "manage/",
            response={200: list[DoctrineOverviewSchema], 403: str},
            tags=self.tags,
        )
        def manage_doctrines(request):
            """
            Manage Doctrines.

            This endpoint retrieves a list of doctrines that the user has permission to manage,
            along with relevant details and actions.
            """
            character_id = request.user.profile.main_character.character_id
            response = get_manage_permission(request, character_id)[0]

            if not response:
                return 403, str(_("Permission Denied"))

            doctrine_obj = Doctrine.objects.all().order_by("skilllist__name")

            response_doctrines_list: list[DoctrineOverviewSchema] = []
            for doctrine in doctrine_obj:
                response_doctrines_list.append(
                    DoctrineOverviewSchema(
                        name=DataTableSchema(
                            html=generate_edit_name_html(doctrine),
                            sort=doctrine.skilllist.name,
                        ),
                        skills=DataTableSchema(
                            html=get_doctrine_skills_button(doctrine),
                            sort=None,
                        ),
                        active=DataTableSchema(
                            html=generate_edit_active_html(doctrine),
                            sort=doctrine.skilllist.show_on_audit,
                        ),
                        ordering=DataTableSchema(
                            html=generate_edit_order_weight_html(doctrine),
                            sort=doctrine.skilllist.order_weight,
                        ),
                        category=DataTableSchema(
                            html=generate_edit_category_html(doctrine),
                            sort=doctrine.category,
                        ),
                        actions=get_doctrine_delete_button(doctrine),
                    )
                )
            return response_doctrines_list

        @api.get(
            "account/overview/",
            response={200: list[CharacterOverviewSchema], 403: dict},
            tags=self.tags,
        )
        def get_account_overview(request: WSGIRequest):
            """
            Get an overview of characters with doctrines.

            This endpoint retrieves a list of characters that have doctrines
            associated with them, along with relevant details and actions.

            Args:
                request (WSGIRequest): The HTTP request object.
            Returns:
                list[CharacterOverviewSchema] | dict: A list of character overviews
                or a permission denied message.
            """
            chars_visible = Doctrine.objects.visible_eve_characters(request.user)

            if chars_visible is None:
                return 403, _("Permission Denied")

            chars_ids = chars_visible.values_list("character_id", flat=True)

            accounts = UserProfile.objects.filter(
                main_character__isnull=False, main_character__character_id__in=chars_ids
            )

            response_character_list: list[CharacterOverviewSchema] = []
            for account in accounts:
                # Skip accounts without a main character
                if account.main_character is None:
                    continue
                response_character_list.append(
                    CharacterOverviewSchema(
                        character_icon=get_character_portrait_url(
                            character_id=account.main_character.character_id,
                            size=32,
                            character_name=account.main_character.character_name,
                            as_html=True,
                        ),
                        character_name=account.main_character.character_name,
                        character_id=account.main_character.character_id,
                        corporation_id=account.main_character.corporation_id,
                        corporation_name=account.main_character.corporation_name,
                        alliance_id=account.main_character.alliance_id,
                        alliance_name=account.main_character.alliance_name,
                        actions=format_html(
                            '<a href="{}" class="btn btn-primary btn-sm" title="{}">{}</a>',
                            reverse(
                                "corptools_doctrine:doctrine",
                                args=[account.main_character.character_id],
                            ),
                            _("View Overview"),
                            _("View"),
                        ),
                    )
                )
            return response_character_list

        @api.get(
            "corporation/overview/",
            response={200: list[CorporationOverviewSchema], 403: dict},
            tags=self.tags,
        )
        def get_corporation_overview(request: WSGIRequest):
            """
            Get an overview of corporations with doctrines.

            This endpoint retrieves a list of corporations that have doctrines
            associated with them, along with relevant details and actions.

            Args:
                request (WSGIRequest): The HTTP request object.
            Returns:
                list[CorporationOverviewSchema] | dict: A list of corporation overviews
                or a permission denied message.
            """
            doctrine_visible = Doctrine.objects.visible_eve_corporations(request.user)

            if doctrine_visible is None:
                return 403, _("Permission Denied")

            # Collect unique corporation IDs from visible corporations
            corp_ids = doctrine_visible.distinct().values_list(
                "corporation_id", flat=True
            )

            # Get existing corporation IDs from characters
            existing_corp_ids = (
                CharacterAudit.objects.filter(
                    character__corporation_id__in=corp_ids,
                )
                .select_related(
                    "character",
                )
                .distinct()
                .values_list("character__corporation_id", flat=True)
            )

            corporations = CorporationAudit.objects.filter(
                corporation__corporation_id__in=existing_corp_ids,
            ).select_related(
                "corporation",
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
                            as_html=True,
                        ),
                        corporation_id=corporation.corporation.corporation_id,
                        corporation_name=corporation.corporation.corporation_name,
                        alliance_icon=(
                            get_alliance_logo_url(
                                alliance_id=alliance_id,
                                size=32,
                                alliance_name=alliance_name,
                                as_html=True,
                            )
                            if alliance_id
                            else None
                        ),
                        alliance_id=alliance_id,
                        alliance_name=alliance_name,
                        actions=format_html(
                            '<a href="{}" class="btn btn-primary btn-sm" title="{}">{}</a>',
                            reverse(
                                "corptools_doctrine:corporation_doctrine",
                                args=[corporation.corporation.corporation_id],
                            ),
                            _("View Overview"),
                            _("View"),
                        ),
                    )
                )
            return response_corporation_list

        @api.post(
            "manage/doctrine/{pk}/delete/",
            response={200: dict, 403: dict},
            tags=self.tags,
        )
        def delete_doctrine(request: WSGIRequest, pk: int):
            """
            Delete a Doctrine by its primary key.

            This endpoint allows authorized users to delete a Doctrine entry
            from the system.

            Args:
                request (WSGIRequest): The HTTP request object.
                pk (int): The primary key of the Doctrine to be deleted.

            Returns:
                dict[str, str]: A dictionary containing the status message.
            """
            character_id = request.user.profile.main_character.character_id
            response = get_manage_permission(request, character_id)[0]

            if not response:
                msg = str(_("Permission Denied"))
                return 200, {"success": False, "message": msg}

            try:
                doctrine = Doctrine.objects.get(pk=pk)
                doctrine.skilllist.delete()
                doctrine.delete()
                logger.info(
                    f"Doctrine '{doctrine}' (ID: {doctrine.pk}) deleted by user '{request.user.username}' (ID: {request.user.id})."
                )
                msg = str(_("Doctrine deleted successfully."))
                return 200, {"success": True, "message": msg}
            except Doctrine.DoesNotExist:
                msg = str(_("Doctrine not found."))
                return 200, {"success": False, "message": msg}

        @api.post(
            "manage/doctrine/{pk}/delete/",
            response={200: dict, 403: dict},
            tags=self.tags,
        )
        # pylint: disable=too-many-return-statements
        def edit_doctrine(request: WSGIRequest, pk: int):
            """
            Edit a Doctrine by its primary key.

            This endpoint allows updating specific fields of a Doctrine's associated SkillList.

            Args:
                request (WSGIRequest): The HTTP request object.
                pk (int): The primary key of the Doctrine to be edited.
            Returns:
                dict[str, str]: A dictionary containing the status message.
            """
            # Check permissions
            perms = get_manage_permission(
                request, request.user.profile.main_character.character_id
            )[0]
            if not perms:
                return 403, {"message": _("Permission Denied")}

            # Get skilllist object
            try:
                skill_checker = Doctrine.objects.get(pk=pk)
            except Doctrine.DoesNotExist:
                return 404, {"message": _("Skill Checker not found")}

            # Get field data
            field_name = request.POST.get("name")
            field_value = request.POST.get("value")
            if not field_name or field_value is None:
                return 400, {"message": _("Invalid field data")}

            # Update field within a transaction
            with transaction.atomic():
                # Process field update
                try:
                    result = self._update_skilllist_field(
                        skill_checker, field_name, field_value
                    )
                    if not result["success"]:
                        return 400, {"message": result["message"]}

                    # Save changes
                    skill_checker.skilllist.save()
                    skill_checker.save()
                    logger.info(
                        "Skilllist %s field '%s' updated to '%s' by %s",
                        skill_checker,
                        field_name,
                        field_value,
                        request.user.username,
                    )
                    return 200, {"message": result["message"]}

                except ValidationError as e:
                    return 400, {"message": str(e)}
                # pylint: disable=broad-except
                except Exception as e:
                    logger.error("Error updating skilllist: %s", str(e))
                    return 500, {"message": _("An error occurred while updating")}

    def _update_skilllist_field(
        self, skill_checker: Doctrine, field_name: str, field_value: str
    ):
        """Helper function to update a specific field of a skilllist"""
        if field_name == "name":
            return self._update_name_field(skill_checker, field_value)
        if field_name == "show_on_audit":
            return self._update_show_on_audit_field(skill_checker, field_value)
        if field_name == "order_weight":
            return self._update_order_weight_field(skill_checker, field_value)
        if field_name == "category":
            return self._update_category_field(skill_checker, field_value)
        return {"success": False, "message": _("Invalid field name")}

    @staticmethod
    def _update_name_field(skill_checker: Doctrine, field_value: str):
        """Update the name field of a skilllist"""
        if not field_value.strip():
            return {"success": False, "message": _("Name cannot be empty")}

        name = field_value.strip()
        names = SkillList.objects.filter(name__iexact=name)
        if names.exists() and names.first().pk != skill_checker.skilllist.pk:
            return {
                "success": False,
                "message": _("Skill list with this name already exists"),
            }

        skill_checker.skilllist.name = name
        return {"success": True, "message": _("Name updated successfully")}

    @staticmethod
    def _update_show_on_audit_field(skill_checker: Doctrine, field_value: str):
        """Update the show_on_audit field of a skilllist"""
        if field_value.lower() in ["true", "1", "yes", "on"]:
            skill_checker.skilllist.show_on_audit = True
        elif field_value.lower() in ["false", "0", "no", "off"]:
            skill_checker.skilllist.show_on_audit = False
        else:
            return {"success": False, "message": _("Invalid show_on_audit value")}

        return {
            "success": True,
            "message": _("Show on audit status updated successfully"),
        }

    @staticmethod
    def _update_order_weight_field(skill_checker: Doctrine, field_value: str):
        """Update the order weight field of a skilllist"""
        try:
            order_weight = int(field_value)
            if order_weight < 0 or order_weight >= 1000:
                return {
                    "success": False,
                    "message": _("Order weight must be between 0 and 999"),
                }
            skill_checker.skilllist.order_weight = order_weight
            return {"success": True, "message": _("Order Weight updated successfully")}
        except ValueError:
            return {
                "success": False,
                "message": _("Order Weight must be a valid number"),
            }

    @staticmethod
    def _update_category_field(skill_checker: Doctrine, field_value):
        """Update the category field of a skilllist"""
        if not field_value.strip():
            return {"success": False, "message": _("Category cannot be empty")}

        skill_checker.category = field_value.strip()
        return {"success": True, "message": _("Category updated successfully")}

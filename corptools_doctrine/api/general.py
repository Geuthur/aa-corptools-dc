"""General API endpoints: User data, Menu navigation, and Settings."""

# Standard Library
from http import HTTPStatus

# Third Party
from ninja import NinjaAPI

# Django
from django.core.handlers.wsgi import WSGIRequest
from django.utils.translation import gettext as _

# AA CorpTools Doctrine
from corptools_doctrine.api import schema
from corptools_doctrine.helpers.eveonline import get_character_portrait_url


class ApiEndpoints:
    tags = ["General"]

    def __init__(self, api: NinjaAPI):
        @api.get(
            "menu/",
            response={HTTPStatus.OK: schema.MenuSchema},
            tags=self.tags,
            summary="Get Doctrine Checker navigation menu",
        )
        def get_menu(request: WSGIRequest):
            left_menu: list[schema.MenuLink] = [
                schema.MenuLink(
                    name=_("Doctrines"),
                    link="/",
                ),
            ]

            if (
                request.user.has_perm("corptools_doctrine.corp_access")
                or request.user.is_superuser
            ):
                left_menu.append(
                    schema.MenuLink(
                        name=_("Corporation Doctrines"),
                        link="/corporation/",
                    )
                )

            left_menu.append(
                schema.MenuLink(
                    name=_("Overview"),
                    link="/overview/",
                )
            )

            right_menu: list[schema.MenuLink] = []
            if (
                request.user.has_perm("corptools_doctrine.manage_access")
                or request.user.has_perm("corptools_doctrine.admin_access")
                or request.user.is_superuser
            ):
                right_menu.append(
                    schema.MenuLink(
                        name=_("Manage"),
                        link="/manage/",
                    )
                )

            return {
                "left_links": left_menu,
                "right_links": right_menu,
            }

        @api.get(
            "user/",
            response={HTTPStatus.OK: schema.UserData},
            tags=self.tags,
            summary="Get current user details and permissions",
        )
        def get_user(request: WSGIRequest):
            user = request.user
            profile = getattr(user, "profile", None)
            main_char = getattr(profile, "main_character", None)

            char_id = main_char.character_id if main_char else 0
            char_name = main_char.character_name if main_char else user.username
            corp_id = main_char.corporation_id if main_char else 0
            corp_name = main_char.corporation_name if main_char else ""
            alliance_id = main_char.alliance_id if main_char else None
            alliance_name = main_char.alliance_name if main_char else None

            portrait = (
                get_character_portrait_url(char_id, as_html=False) if char_id else None
            )

            permissions = {
                "basic_access": user.has_perm("corptools_doctrine.basic_access"),
                "corp_access": user.has_perm("corptools_doctrine.corp_access"),
                "alliance_access": user.has_perm("corptools_doctrine.alliance_access"),
                "manage_access": user.has_perm("corptools_doctrine.manage_access"),
                "admin_access": user.has_perm("corptools_doctrine.admin_access")
                or user.is_superuser,
            }

            return {
                "user_id": user.pk,
                "character_id": char_id,
                "character_name": char_name,
                "corporation_id": corp_id,
                "corporation_name": corp_name,
                "alliance_id": alliance_id,
                "alliance_name": alliance_name,
                "portrait": portrait,
                "is_admin": permissions["admin_access"],
                "permissions": permissions,
            }

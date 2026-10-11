# Django
from django.core.exceptions import ObjectDoesNotExist
from django.core.handlers.wsgi import WSGIRequest
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo
from allianceauth.services.hooks import get_extension_logger

# AA CorpTools Doctrine
from corptools_doctrine import __title__
from corptools_doctrine.models import Doctrine
from corptools_doctrine.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)


def get_manage_permission(
    request: WSGIRequest, character_id: int
) -> tuple[bool, EveCharacter | None]:
    """Check if the user has permission to manage."""
    perms = True
    main_char = EveCharacter.objects.select_related(
        "character_ownership",
        "character_ownership__user__profile",
        "character_ownership__user__profile__main_character",
    ).get(character_id=character_id)

    try:
        main_char = main_char.character_ownership.user.profile.main_character
    except ObjectDoesNotExist:
        pass

    # check access
    visible = Doctrine.objects.manage_to(request.user)
    if main_char not in visible:
        account_chars = (
            request.user.profile.main_character.character_ownership.user.character_ownerships.all()
        )
        if main_char in account_chars:
            pass
        else:
            perms = False
    return perms, main_char


def get_main_character(
    request: WSGIRequest, character_id: int
) -> tuple[bool, EveCharacter | None]:
    perms = True
    main_char = EveCharacter.objects.select_related(
        "character_ownership",
        "character_ownership__user__profile",
        "character_ownership__user__profile__main_character",
    ).get(character_id=character_id)
    try:
        main_char = main_char.character_ownership.user.profile.main_character
    except ObjectDoesNotExist:
        pass

    # check access
    visible = Doctrine.objects.visible_eve_characters(request.user)
    if main_char not in visible:
        account_chars = (
            request.user.profile.main_character.character_ownership.user.character_ownerships.all()
        )
        if main_char in account_chars:
            pass
        else:
            perms = False
    return perms, main_char


def get_corporation(request, corporation_id) -> tuple[bool, EveCorporationInfo | None]:
    perms = True
    try:
        corporation = EveCorporationInfo.objects.get(corporation_id=corporation_id)
    except ObjectDoesNotExist:
        return False, None

    # check access
    visible = Doctrine.objects.visible_eve_corporations(request.user)
    if corporation not in visible:
        perms = False
    return perms, corporation


# pylint: disable=too-many-branches
def _collect_user_doctrines(corp_skills_list: dict, doctrines) -> dict:
    """Collect the best doctrine skill data for the user across all their characters."""
    user_doctrines = {}
    best_missing_counts = {}

    if hasattr(doctrines, "values_list"):
        active_doctrine_names = set(doctrines.values_list("skilllist__name", flat=True))
    elif isinstance(doctrines, (set, frozenset)):
        active_doctrine_names = doctrines
    elif isinstance(doctrines, (list, tuple)):
        active_doctrine_names = {
            d.skilllist.name if hasattr(d, "skilllist") else getattr(d, "name", str(d))
            for d in doctrines
        }
    else:
        active_doctrine_names = set()

    for character_data in corp_skills_list.values():
        doctrines_data = (
            character_data.get("doctrines")
            if isinstance(character_data, dict)
            else getattr(character_data, "doctrines", None)
        )
        if not doctrines_data:
            continue

        if isinstance(doctrines_data, dict):
            doctrine_items = doctrines_data.items()
        else:
            doctrine_items = (
                (getattr(d, "name", getattr(d, "doctrine_name", "")), d)
                for d in doctrines_data
            )

        for doctrine_name, doctrine_data in doctrine_items:
            if doctrine_name not in active_doctrine_names:
                continue

            # Early exit: if already 100% doctrine ready (0 missing skills),
            # no alt can have fewer than 0 missing skills.
            if best_missing_counts.get(doctrine_name) == 0:
                continue

            current_skills = (
                doctrine_data.get("skills")
                if isinstance(doctrine_data, dict)
                else getattr(doctrine_data, "skills", None)
            )
            current_missing_count = len(current_skills) if current_skills else 0

            if doctrine_name not in user_doctrines:
                user_doctrines[doctrine_name] = doctrine_data
                best_missing_counts[doctrine_name] = current_missing_count
            elif current_missing_count < best_missing_counts[doctrine_name]:
                user_doctrines[doctrine_name] = doctrine_data
                best_missing_counts[doctrine_name] = current_missing_count

    return user_doctrines

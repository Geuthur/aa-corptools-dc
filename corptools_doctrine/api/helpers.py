# Django
from django.core.exceptions import ObjectDoesNotExist
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet
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


def _collect_user_doctrines(
    corp_skills_list: dict, doctrines: list[QuerySet[Doctrine]]
) -> dict:
    """Collect the best doctrine skill data for the user across all their characters."""
    user_doctrines = {}

    # Process each character's skill data
    for __, character_data in corp_skills_list.items():
        # character_data is a CharacterDoctrineDataSchema object
        if not character_data.doctrines:
            continue

        for doctrine_key, doctrine_data in character_data.doctrines.items():
            # Filter out inactive skill lists
            if doctrine_key not in doctrines.values_list("skilllist__name", flat=True):
                continue
            if doctrine_key not in user_doctrines:
                user_doctrines[doctrine_key] = doctrine_data
            else:
                # Take the best result (fewer missing skills) across all chars
                # Empty skills dict means all skills are trained
                current_missing_count = len(doctrine_data.skills)
                existing_missing_count = len(user_doctrines[doctrine_key].skills)

                # Prefer the character with fewer missing skills (0 is best)
                if current_missing_count < existing_missing_count:
                    user_doctrines[doctrine_key] = doctrine_data

    return user_doctrines

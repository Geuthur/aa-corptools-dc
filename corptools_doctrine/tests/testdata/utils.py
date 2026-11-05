# Third Party
from evesde_factory.utils import add_character_to_user

# Django
from django.contrib.auth.models import User

# Alliance Auth
from allianceauth.authentication.backends import StateBackend
from allianceauth.authentication.models import CharacterOwnership
from allianceauth.eveonline.models import EveCharacter
from allianceauth.tests.auth_utils import AuthUtils

# Alliance Auth (External Libs)
# Corptools
from corptools.models.audits import CharacterAudit, CorporationAudit
from corptools.models.eve_models import EveItemCategory, EveItemGroup, EveItemType


def create_user_from_evecharacter(
    character_id: int,
    permissions: list[str] | None = None,
    scopes: list[str] | None = None,
) -> tuple[User, CharacterOwnership]:
    """Create new allianceauth user from EveCharacter object.

    Args:
        character_id (int): ID of eve character
        permissions (list[str] | None): list of permission names, e.g. `"my_app.my_permission"`
        scopes (list[str] | None): list of scope names
    Returns:
        tuple(User, CharacterOwnership): Created Alliance Auth User and CharacterOwnership
    """
    auth_character = EveCharacter.objects.get(character_id=character_id)
    user = AuthUtils.create_user(auth_character.character_name.replace(" ", "_"))
    character_ownership = add_character_to_user(
        user, auth_character, is_main=True, scopes=scopes
    )
    if permissions:
        for permission_name in permissions:
            user = AuthUtils.add_permission_to_user_by_name(permission_name, user)
    return user, character_ownership


def create_owner(
    eve_character: EveCharacter, owner_type="character", **kwargs
) -> CharacterAudit | CorporationAudit:
    """
    Create a Corp Tools Owner (CharacterAudit or CorporationAudit) from an EveCharacter.
    The type of owner created depends on the owner_type parameter.
    Args:
        eve_character (EveCharacter): The EveCharacter to create the owner from.
        owner_type (str, optional): Type of owner, either "character" or "corporation"
    Returns:
        (CharacterAudit or CorporationAudit): The created Corp Tools owner.

    """
    if owner_type == "character":
        owner = CharacterAudit.objects.get_or_create(
            character=eve_character,
        )[0]
        return owner
    if owner_type == "corporation":
        owner = CorporationAudit.objects.get_or_create(
            corporation=eve_character.corporation,
        )[0]
        return owner
    raise ValueError("owner_type must be either 'character' or 'corporation'")


def create_owner_from_user(
    user: User, owner_type="character", **kwargs
) -> CharacterAudit | CorporationAudit:
    """
    Create a CharacterAudit or CorporationAudit from a user.
    The type of owner created depends on the owner_type parameter.

    Args:
        user (User): The user to create the owner from.
        owner_type (str): Type of owner, either "character" or "corporation"
    """
    eve_character = user.profile.main_character
    if not eve_character:
        raise ValueError("User needs to have a main character.")

    return create_owner(eve_character, owner_type=owner_type, **kwargs)


def create_owner_from_evecharacter(
    character_id: int, owner_type="character", **kwargs
) -> CharacterAudit | CorporationAudit:
    """
    Create a CharacterAudit or CorporationAudit from an existing EveCharacter.
    The type of owner created depends on the owner_type parameter.

    Args:
        character_id (int): ID of the EveCharacter to create the owner from.
        owner_type (str): Type of owner, either "character" or "corporation"
    Returns:
        CharacterAudit | CorporationAudit: The created Corp Tools owner.
    """

    _, character_ownership = create_user_from_evecharacter_with_access(
        character_id, disconnect_signals=True
    )
    return create_owner(character_ownership.character, owner_type=owner_type, **kwargs)


def create_user_from_evecharacter_with_access(
    character_id: int, disconnect_signals: bool = True, owner_type="character"
) -> tuple[User, CharacterOwnership]:
    """
    Create user with basic access from an existing EveCharacter and use it as main.

    Args:
        character_id (int): ID of eve character
        disconnect_signals (bool, optional): Whether to disconnect signals during user creation. Defaults to True.
        owner_type (str, optional): Type of owner, either "character" or "corporation"
    Returns:
        tuple(User, CharacterOwnership): Created Alliance Auth User and CharacterOwnership
    """
    auth_character = EveCharacter.objects.get(character_id=character_id)
    username = StateBackend.iterate_username(auth_character.character_name)
    user = AuthUtils.create_user(username, disconnect_signals=disconnect_signals)
    user = AuthUtils.add_permission_to_user_by_name(
        "corptools_doctrine.basic_access", user, disconnect_signals=disconnect_signals
    )

    character_ownership = add_character_to_user(
        user,
        auth_character,
        is_main=True,
        disconnect_signals=disconnect_signals,
    )
    return user, character_ownership


def add_new_permission_to_user(
    user: User,
    permission_name: str,
    disconnect_signals: bool = True,
) -> User:
    """Add a new permission to an existing allianceauth user.

    Args:
        user (User): Alliance Auth User
        permission_name (str): Permission name, e.g. `"my_app.my_permission"`
        disconnect_signals (bool, optional): Whether to disconnect signals during addition. Defaults to True.
    Returns:
        User: Updated Alliance Auth User
    """
    return AuthUtils.add_permission_to_user_by_name(
        permission_name, user, disconnect_signals=disconnect_signals
    )


def add_auth_character_to_user(
    user: User,
    character_id: int,
    disconnect_signals: bool = True,
    owner_type="character",
) -> CharacterOwnership:
    """Add an existing :class:`EveCharacter` to a User.

    Args:
        user (User): Alliance Auth User
        character_id (int): ID of eve character
        disconnect_signals (bool, optional): Whether to disconnect signals during addition. Defaults to True.
        owner_type (str, optional): Type of owner, either "character" or "corporation"
    Returns:
        CharacterOwnership: The created CharacterOwnership instance.
    """
    auth_character = EveCharacter.objects.get(character_id=character_id)

    return add_character_to_user(
        user,
        auth_character,
        is_main=False,
        disconnect_signals=disconnect_signals,
    )


def add_owner_to_user(
    user: User,
    character_id: int,
    disconnect_signals: bool = True,
    owner_type="character",
    **kwargs,
) -> CharacterAudit | CorporationAudit:
    """
    Add a CharacterAudit or CorporationAudit character to a user.
    The type of owner created depends on the owner_type parameter.

    Args:
        user (User): Alliance Auth User
        character_id (int): ID of eve character
        disconnect_signals (bool, optional): Whether to disconnect signals during addition. Defaults to True.
        owner_type (str): Type of owner, either "character" or "corporation"
    Returns:
        CharacterOwner | CorporationOwner: The created owner.
    """
    character_ownership = add_auth_character_to_user(
        user,
        character_id,
        disconnect_signals=disconnect_signals,
    )
    return create_owner(character_ownership.character, owner_type=owner_type, **kwargs)


def create_eveitemtype(
    type_id: int, name: str, published: bool = True, **kwargs
) -> EveItemType:
    """
    Create a EveItemType object.

    Args:
        type_id (int): The type ID of the item.
        name (str): The name of the item.
        published (bool): Whether the item is published.
        **kwargs: Additional fields for EveItemType.
    Returns:
        EveItemType: The created EveItemType object.
    """
    params = {
        "type_id": type_id,
        "name": name,
        "published": published,
    }
    kwargs.update(params)

    item = EveItemType(**kwargs)
    item.save()
    return item


def create_evegroup(group_id: int, name: str, **kwargs):
    """
    Create an EveItemGroup object.

    Args:
        group_id (int): The group ID of the item group.
        name (str): The name of the item group.
        **kwargs: Additional fields for EveItemGroup.
    Returns:
        EveItemGroup: The created EveItemGroup object.
    """
    params = {
        "group_id": group_id,
        "name": name,
    }
    kwargs.update(params)

    group = EveItemGroup(**kwargs)
    group.save()
    return group


def create_evecategory(category_id: int, name: str, **kwargs):
    """
    Create an EveItemCategory object.

    Args:
        category_id (int): The category ID of the item category.
        name (str): The name of the item category.
        **kwargs: Additional fields for EveItemCategory.
    Returns:
        EveItemCategory: The created EveItemCategory object.
    """
    params = {
        "category_id": category_id,
        "name": name,
    }
    kwargs.update(params)

    category = EveItemCategory(**kwargs)
    category.save()
    return category

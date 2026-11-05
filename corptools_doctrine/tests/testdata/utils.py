# Django
from django.contrib.auth.models import User

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter

# Alliance Auth (External Libs)
# Corptools
from corptools.models.audits import CharacterAudit, CorporationAudit
from corptools.models.eve_models import EveItemCategory, EveItemGroup, EveItemType


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

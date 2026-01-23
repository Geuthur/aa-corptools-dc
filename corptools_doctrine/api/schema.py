# Third Party
from ninja import Schema


class Message(Schema):
    message: str


class Character(Schema):
    character_icon: str | None = None
    character_name: str
    character_id: int
    corporation_id: int
    corporation_name: str
    alliance_id: int | None = None
    alliance_name: str | None = None


class Corporation(Schema):
    corporation_icon: str | None = None
    corporation_id: int
    corporation_name: str
    alliance_icon: str | None = None
    alliance_id: int | None = None
    alliance_name: str | None = None


class CharacterDoctrines(Schema):
    character: Character
    doctrines: dict
    # skills: dict


class CorporationDoctrines(Schema):
    character: Character
    doctrines: dict
    alts: list[Character] | None = None

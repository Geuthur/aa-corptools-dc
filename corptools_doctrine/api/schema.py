# Third Party
from ninja import FilterSchema, Schema

# Django
from django.db.models import Q, QuerySet

# AA CorpTools Doctrine
from corptools_doctrine.models import Doctrine

# ---------------------------------------------------------------------------
# General / Navigation / User Schemas
# ---------------------------------------------------------------------------


class MenuLink(Schema):
    name: str
    link: str
    is_external: bool = False


class MenuSchema(Schema):
    left_links: list[MenuLink]
    right_links: list[MenuLink]


class UserData(Schema):
    user_id: int
    character_id: int
    character_name: str
    corporation_id: int
    corporation_name: str
    alliance_id: int | None = None
    alliance_name: str | None = None
    portrait: str | None = None
    is_admin: bool = False
    permissions: dict[str, bool] = {}


# ---------------------------------------------------------------------------
# Character & Corporation Schemas
# ---------------------------------------------------------------------------


class CharacterSchema(Schema):
    character_icon: str | None = None
    character_name: str
    character_id: int
    corporation_id: int
    corporation_name: str
    alliance_id: int | None = None
    alliance_name: str | None = None


class CorporationSchema(Schema):
    corporation_icon: str | None = None
    corporation_id: int
    corporation_name: str
    alliance_icon: str | None = None
    alliance_id: int | None = None
    alliance_name: str | None = None


class CharacterDoctrines(Schema):
    character: CharacterSchema
    doctrines: dict


class CorporationDoctrines(Schema):
    character: CharacterSchema
    doctrines: dict
    alts: list[CharacterSchema] | None = None


class CorporationMemberOverview(Schema):
    character: CharacterSchema
    alts: list[CharacterSchema] | None = None


class ActiveDoctrineOverview(Schema):
    id: int
    name: str
    category: str
    order: int


class CorporationMembersResponse(Schema):
    corporation_id: int
    corporation_name: str
    members: list[CorporationMemberOverview]
    doctrines: list[ActiveDoctrineOverview]


class DoctrineAuditFilter(FilterSchema):
    category: str | None = None
    doctrine_ids: list[int] | None = None

    def filter_category(self, value: str | None) -> Q:
        if not value or value == "ALL":
            return Q()
        return Q(category=value)

    def filter_doctrine_ids(self, value: list[int] | None) -> Q:
        if not value:
            return Q()
        return Q(id__in=value)

    def get_doctrines(self, base_qs: QuerySet | None = None) -> list:
        if base_qs is None:
            base_qs = Doctrine.objects.filter(
                skilllist__show_on_audit=True
            ).select_related("skilllist")
        return list(self.filter(base_qs))

    def get_required_skill_names(self, doctrines: list | None = None) -> set[str]:
        if doctrines is None:
            doctrines = self.get_doctrines()
        return {
            skill_name
            for doctrine in doctrines
            for skill_name in doctrine.get_skills().keys()
        }


class AuditMembersRequest(Schema):
    character_ids: list[int] | None = None
    category: str | None = None
    doctrine_ids: list[int] | None = None

    def to_filter(self) -> DoctrineAuditFilter:
        return DoctrineAuditFilter(
            category=self.category,
            doctrine_ids=self.doctrine_ids,
        )


class DoctrineSkillsSchema(Schema):
    skill_name: str
    required_level: int


class DoctrineSchema(Schema):
    id: int = 0
    name: str
    skills: list[DoctrineSkillsSchema] | None = None
    order: int
    category: str
    html: str
    character_id: int | None = None


class CharacterSkillsSchema(Schema):
    name: str
    skill_group: str
    sp_total: int
    active_level: int
    trained_level: int


class CharacterDoctrineSchema(Schema):
    character: CharacterSchema
    skills: list[CharacterSkillsSchema]
    doctrines: list[DoctrineSchema]


class CharacterSkillListSchema(Schema):
    characters: list[CharacterDoctrineSchema]
    doctrines: str = ""
    account: str = ""


# ---------------------------------------------------------------------------
# Modal & Management Schemas
# ---------------------------------------------------------------------------


class MissingSkillDetail(Schema):
    name: str
    trained_level: int
    needed_level: int


class MissingSkillsResponse(Schema):
    character_id: int
    character_name: str
    doctrine_id: int
    doctrine_name: str
    missing_skills: list[MissingSkillDetail]
    clipboard_export: str


class DoctrineDetailResponse(Schema):
    id: int
    name: str
    category: str | None = None
    order_weight: int
    show_on_audit: bool
    skills: dict[str, int]
    character_skills: dict[str, int] | None = None


class ManageDoctrineSchema(Schema):
    id: int
    name: str
    category: str | None = None
    order_weight: int
    show_on_audit: bool
    skill_count: int


class DoctrineUpdateRequest(Schema):
    name: str | None = None
    category: str | None = None
    order_weight: int | None = None
    show_on_audit: bool | None = None


class DoctrineCreateRequest(Schema):
    name: str
    category: str | None = None
    order_weight: int = 1
    skill_list: str

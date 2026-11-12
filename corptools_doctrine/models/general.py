"""Models for General."""

# Standard Library
from typing import Any

# Django
from django.db import models
from django.utils.translation import gettext_lazy as _


class General(models.Model):
    """A model defining commonly used properties, permissions, and helper methods for Corp Tools Doctrine."""

    class Permission(models.TextChoices):
        BASIC_ACCESS = "basic_access", _("Can access this app, Corp Tools Doctrine.")
        CORP_ACCESS = "corp_access", _(
            "Can view Characters from own Corporation, Corp Tools Doctrine."
        )
        ALLIANCE_ACCESS = "alliance_access", _(
            "Can view Characters from own Alliance, Corp Tools Doctrine."
        )
        MANAGE_ACCESS = "manage_access", _("Can manage this app, Corp Tools Doctrine.")
        ADMIN_ACCESS = "admin_access", _(
            "Gives full access to this app, Corp Tools Doctrine."
        )

    class Meta:
        managed = False
        default_permissions = ()  # Remove standard permissions

    # Inject dynamic permissions
    Meta.permissions = Permission.choices

    @classmethod
    def get_perm(cls, perm: "str | Permission") -> str:
        """Return full permission string 'corptools_doctrine.<codename>'."""
        codename = perm.value if isinstance(perm, cls.Permission) else perm
        return f"corptools_doctrine.{codename}"

    @classmethod
    def has_perm(cls, user: Any, perm: "str | General.Permission") -> bool:
        """Check if user has permission."""
        if not user or not hasattr(user, "has_perm"):
            return False
        return user.has_perm(cls.get_perm(perm))

    @classmethod
    def has_any_perm(cls, user: Any, *perms: "str | General.Permission") -> bool:
        """Return True if user has any of the specified permissions."""
        if not user or not hasattr(user, "has_perm"):
            return False
        return any(user.has_perm(cls.get_perm(p)) for p in perms)

    @classmethod
    def has_management_access(cls, user: Any) -> bool:
        """Check if user has any management permission."""
        return cls.has_any_perm(
            user,
            cls.Permission.MANAGE_ACCESS,
            cls.Permission.ADMIN_ACCESS,
        )

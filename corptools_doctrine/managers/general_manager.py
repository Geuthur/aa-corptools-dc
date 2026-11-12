"""Manager for General: app rules that Django cannot check itself.

The API, the menu hook and the access querysets check permissions only through
this manager. The Django views keep `@permissions_required(...)`.
General is unmanaged, so this manager never queries the database.
"""

# Django
from django.db import models

# Alliance Auth
from allianceauth.authentication.models import User


class GeneralManager(models.Manager):
    @staticmethod
    def has_basic_access(user: User) -> bool:
        """True if the user may use the app (basic_access)."""
        return bool(user.has_perm("corptools_doctrine.basic_access"))

    @staticmethod
    def has_admin_access(user: User) -> bool:
        """True for superusers and users with admin_access."""
        return bool(
            user.is_superuser or user.has_perm("corptools_doctrine.admin_access")
        )

    @staticmethod
    def has_corp_access(user: User) -> bool:
        """True for superusers and users with corp_access."""
        return bool(
            user.is_superuser or user.has_perm("corptools_doctrine.corp_access")
        )

    @staticmethod
    def has_alliance_access(user: User) -> bool:
        """True for superusers and users with alliance_access."""
        return bool(
            user.is_superuser or user.has_perm("corptools_doctrine.alliance_access")
        )

    @staticmethod
    def has_manage_access(user: User) -> bool:
        """True if the user has manage_access itself."""
        return bool(user.has_perm("corptools_doctrine.manage_access"))

    @staticmethod
    def has_management_access(user: User) -> bool:
        """True if the user may manage (manage_access or admin access)."""
        return GeneralManager.has_manage_access(
            user
        ) or GeneralManager.has_admin_access(user)

# Standard Library

# Django
from django.db import models
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# AA CorpTools Doctrine
from corptools_doctrine import __title__
from corptools_doctrine.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)


class General(models.Model):
    """A model defining commonly used properties and methods for Corp Tools Doctrine."""

    class Meta:
        managed = False
        default_permissions = ()
        permissions = (
            ("basic_access", "Can access this app, Corp Tools Doctrine."),
            (
                "corp_access",
                "Can view Characters from own Corporation, Corp Tools Doctrine.",
            ),
            (
                "alliance_access",
                "Can view Characters from own Alliance, Corp Tools Doctrine.",
            ),
            ("manage_access", "Can manage this app, Corp Tools Doctrine."),
            (
                "admin_access",
                "Gives full access to this app, Corp Tools Doctrine.",
            ),
        )

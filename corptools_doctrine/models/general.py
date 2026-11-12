"""Models for General."""

# Django
from django.db import models
from django.utils.translation import gettext_lazy as _

# AA CorpTools Doctrine
from corptools_doctrine.managers.general import GeneralManager


class General(models.Model):
    """A model defining commonly used properties and permissions for Corp Tools Doctrine."""

    objects = GeneralManager()

    class Meta:
        managed = False
        default_permissions = ()
        permissions = (
            ("basic_access", _("Can access this app, Corp Tools Doctrine.")),
            (
                "corp_access",
                _("Can view Characters from own Corporation, Corp Tools Doctrine."),
            ),
            (
                "alliance_access",
                _("Can view Characters from own Alliance, Corp Tools Doctrine."),
            ),
            ("manage_access", _("Can manage this app, Corp Tools Doctrine.")),
            (
                "admin_access",
                _("Gives full access to this app, Corp Tools Doctrine."),
            ),
        )

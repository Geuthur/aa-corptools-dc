"""
App Settings
"""

# Django
from django.conf import settings

# Set Naming on Auth Hook
AA_CORPTOOLS_DOCTRINE_APP_NAME = getattr(
    settings, "AA_CORPTOOLS_DOCTRINE_APP_NAME", "Doctrine Checker"
)

AA_CORPTOOLS_DOCTRINE_CACHE = getattr(settings, "AA_CORPTOOLS_DOCTRINE_CACHE", True)

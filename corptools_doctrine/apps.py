"""App Configuration"""

# Django
from django.apps import AppConfig

# AA CorpTools Doctrine
from corptools_doctrine import __version__


class DoctrineCheckerConfig(AppConfig):
    """App Config"""

    default_auto_field = "django.db.models.AutoField"
    name = "corptools_doctrine"
    label = "corptools_doctrine"
    verbose_name = f"AA CorpTools Doctrine v{__version__}"

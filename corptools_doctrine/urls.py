"""App URLs"""

# Django
from django.urls import path, re_path

# AA CorpTools Doctrine
from corptools_doctrine import views
from corptools_doctrine.api import api

app_name: str = "corptools_doctrine"  # pylint: disable=invalid-name

urlpatterns = [
    # -- Main URLs
    path(
        "view/doctrine/",
        views.doctrine,
        name="doctrine",
    ),
    path(
        "<int:character_id>/view/doctrine/",
        views.doctrine,
        name="doctrine",
    ),
    path(
        "<int:corporation_id>/view/corporation_doctrine/",
        views.corporation_doctrine,
        name="corporation_doctrine",
    ),
    path(
        "view/overview/",
        views.overview,
        name="overview",
    ),
    path(
        "view/corporation_overview/",
        views.corporation_overview,
        name="corporation_overview",
    ),
    path(
        "view/administration/",
        views.manage,
        name="administration",
    ),
    # -- Administration
    path(
        "view/doctrine/add/",
        views.add_doctrine,
        name="add_doctrine",
    ),
    path(
        "manage/doctrine/add/",
        views.ajax_doctrine,
        name="ajax_doctrine",
    ),
    # -- API System
    re_path(r"^api/", api.urls),
]

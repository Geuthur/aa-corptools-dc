"""App URLs"""

# Django
from django.urls import path, re_path

# Alliance Auth
from allianceauth.authentication.decorators import decorate_url_patterns

# AA CorpTools Doctrine
from corptools_doctrine import views
from corptools_doctrine.api import api
from corptools_doctrine.api.auth import basic_access_required

app_name: str = "corptools_doctrine"  # pylint: disable=invalid-name

# Every URL of the API (endpoints, schema and docs) requires `basic_access`
api_patterns, api_app_name, api_namespace = api.urls
api_patterns = decorate_url_patterns(
    (api_patterns, api_app_name), basic_access_required
)[0]

urlpatterns = [
    # -- API System
    re_path(r"^api/", (api_patterns, api_app_name, api_namespace)),
    # -- React Frontend SPA
    path("", views.react_base, name="react_base"),
    re_path(
        r"^(?!api/).*$",
        views.react_base,
        name="react_base_catchall",
    ),
]

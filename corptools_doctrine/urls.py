"""App URLs"""

# Django
from django.urls import path, re_path

# AA CorpTools Doctrine
from corptools_doctrine import views
from corptools_doctrine.api import api

app_name: str = "corptools_doctrine"  # pylint: disable=invalid-name

urlpatterns = [
    # -- API System
    re_path(r"^api/", api.urls),
    # -- React Frontend SPA
    path("", views.react_base, name="react_base"),
    re_path(
        r"^(?!api/).*$",
        views.react_base,
        name="react_base_catchall",
    ),
]

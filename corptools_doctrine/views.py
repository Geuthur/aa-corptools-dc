"""App Views"""

# Django
from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from django.utils.translation import gettext as _

# Alliance Auth
from allianceauth.authentication.decorators import permissions_required

# AA CorpTools Doctrine
from corptools_doctrine import __version__


@login_required
@permissions_required(["corptools_doctrine.basic_access"])
def react_base(
    request: WSGIRequest, *args, **kwargs
):  # pylint: disable=unused-argument
    """React Frontend SPA Base View."""
    context = {
        "app_name": "corptools_doctrine",
        "title": _("Doctrine Checker"),
        "version": __version__,
    }
    return render(
        request, "corptools_doctrine/react_corptools_doctrine.html", context=context
    )

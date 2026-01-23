"""App Views"""

# Standard Library
import json

# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

# Alliance Auth
from allianceauth.authentication.decorators import permissions_required
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from corptools.models.skills import SkillList

# AA CorpTools Doctrine
from corptools_doctrine import __title__, forms
from corptools_doctrine.models import Doctrine
from corptools_doctrine.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)


@login_required
@permissions_required(["corptools_doctrine.basic_access"])
def doctrine(request: WSGIRequest, character_id=None):
    if character_id is None:
        character_id = request.user.profile.main_character.character_id

    context = {
        "title": _("Doctrine"),
        "character_id": character_id,
    }
    return render(request, "corptools_doctrine/view-doctrine.html", context=context)


@login_required
@permissions_required(["corptools_doctrine.corp_access"])
def corporation_doctrine(request: WSGIRequest, corporation_id=None):
    character_id = request.user.profile.main_character.character_id
    if corporation_id is None:
        corporation_id = request.user.profile.main_character.corporation_id

    context = {
        "title": _("Corporation Doctrine"),
        "character_id": character_id,
        "corporation_id": corporation_id,
        "forms": {
            "skilllist": forms.SkillListForm(),
        },
    }
    return render(
        request, "corptools_doctrine/view-corporation-doctrine.html", context=context
    )


@login_required
@permissions_required(["corptools_doctrine.basic_access"])
def overview(request: WSGIRequest):
    context = {
        "title": _("Account Overview"),
    }
    return render(
        request, "corptools_doctrine/view-character-overview.html", context=context
    )


@login_required
@permissions_required(["corptools_doctrine.corp_access"])
def corporation_overview(request: WSGIRequest):
    context = {
        "title": _("Corporation Overview"),
    }
    return render(
        request, "corptools_doctrine/view-corporation-overview.html", context=context
    )


@login_required
@permissions_required(
    ["corptools_doctrine.manage_access", "corptools_doctrine.admin_access"]
)
def manage(request: WSGIRequest):
    context = {
        "title": _("Doctrine Manage"),
    }
    return render(request, "corptools_doctrine/view-manage.html", context=context)


@login_required
@permissions_required(
    ["corptools_doctrine.manage_access", "corptools_doctrine.admin_access"]
)
def add_doctrine(request: WSGIRequest):
    context = {
        "title": _("Add Doctrine"),
        "forms": {
            "skilllist": forms.SkillListForm(),
        },
    }
    return render(request, "corptools_doctrine/view-doctrine-add.html", context=context)


@login_required
@permissions_required(
    ["corptools_doctrine.manage_access", "corptools_doctrine.admin_access"]
)
def ajax_doctrine(request: WSGIRequest):
    if request.method == "POST":
        form = forms.SkillListForm(request.POST)
        if form.is_valid():
            # skill_list = form.cleaned_data["skill_list"]
            name = form.cleaned_data["name"]
            category = form.cleaned_data["category"]
            order_weight = form.cleaned_data["order_weight"]

            # Get parsed skills from the form
            parsed_skills = form.get_parsed_skills()

            # Check if the skill list is empty
            if not parsed_skills:
                messages.error(
                    request, _("Your skill plan is empty. Please add skills.")
                )
                return redirect("corptools_doctrine:doctrine")

            skilllist = SkillList(
                name=name,
                skill_list=json.dumps(parsed_skills, ensure_ascii=False),
                order_weight=order_weight,
            )

            # Save returns None, so call save() on the instance and keep the instance
            skilllist.save()

            Doctrine.objects.create(
                skilllist=skilllist,
                category=category,
            )

            messages.success(
                request,
                _("Skill plan '{}' with {} skills saved successfully.").format(
                    name, len(parsed_skills)
                ),
            )
            return redirect("corptools_doctrine:doctrine")

        # Collect form errors and display them
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                if field == "__all__":
                    error_messages.append(str(error))
                else:
                    field_label = form.fields[field].label or field
                    error_messages.append(f"{field_label}: {error}")

        if error_messages:
            messages.error(
                request,
                _("There was an error with your skill plan: ")
                + " ".join(error_messages),
            )
        else:
            messages.error(
                request,
                _(
                    "There was an error with your skill plan. Please check the form and try again."
                ),
            )
    else:
        messages.error(
            request, _("There was an error processing your request. Please try again.")
        )
    return redirect("corptools_doctrine:doctrine")

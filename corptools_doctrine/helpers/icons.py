# Django
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

# AA CorpTools Doctrine
from corptools_doctrine.models import Doctrine


def get_doctrine_delete_button(doctrine: Doctrine) -> str:
    """
    Generate a Delete Skillplan button for the Skillplan Modal view.

    This function creates a HTML Delete Skillplan button for deleting skillplans to the according doctrine.
    When clicked, it triggers a modal to confirm the deletion of the according skillplan.

    Args:
        doctrine (Doctrine): The doctrine object to be viewed.
    Returns:
        String: HTML string containing the info button.
    """

    # Generate the URL for the add payment Request
    button_request_delete_url = reverse(
        "corptools_doctrine:api:delete_doctrine",
        kwargs={
            "pk": doctrine.pk,
        },
    )

    # Define the icon, color and tooltip for the delete button
    color = "danger"
    icon = '<i class="fa-solid fa-trash"></i>'
    title = _("Delete Skillplan")

    # Create the HTML for the delete skillplan icon button
    payments_delete_button = (
        "<button "
        f'data-action="{button_request_delete_url}" '
        f'class="btn btn-{color} btn-sm btn-square me-2" '
        'data-bs-toggle="modal" '
        'data-bs-tooltip="aa-corptools-doctrine" '
        'data-bs-target="#corptools-request-skillplan-accept-delete" '
        f'title="{title}">{icon}</button>'
    )
    return payments_delete_button


def get_doctrine_skills_button(doctrine: Doctrine) -> str:
    """
    Generate a Skillplan button for the Skillplan Modal view.

    This function creates a HTML info button to view the skills of the according doctrine.
    When clicked, it triggers a modal to show the skills of the according skillplan.

    Args:
        doctrine (Doctrine): The doctrine object to be viewed.
    Returns:
        String: HTML string containing the info button.
    """

    # Generate the URL for the add payment Request
    button_request_delete_url = reverse(
        "corptools_doctrine:api:get_doctrine_skills",
        kwargs={
            "pk": doctrine.pk,
        },
    )

    # Define the icon, color and tooltip for the delete button
    color = "primary"
    icon = f'{len(doctrine.get_skills())} <i class="fa-solid fa-book-open"></i>'
    title = _("View Doctrine")

    # Create the HTML for the delete skillplan icon button
    payments_delete_button = (
        "<button "
        f'data-action="{button_request_delete_url}" '
        f'class="btn btn-{color} btn-sm btn-square me-2" '
        'data-bs-toggle="modal" '
        'data-bs-tooltip="aa-corptools-doctrine" '
        'data-bs-target="#corptools-request-doctrine-skills" '
        f'title="{title}">{icon}</button>'
    )
    return payments_delete_button


def generate_edit_name_html(
    doctrine: Doctrine,
) -> str:
    """
    Generate HTML for an editable name field.

    This function creates an HTML anchor tag that allows inline editing of the name field
    of a Doctrine skill list.
    """
    url = reverse(
        viewname="corptools_doctrine:api:edit_doctrine",
        kwargs={"pk": doctrine.pk},
    )
    title = _("Enter name")

    html = (
        "<a class='editable' href='#' data-type='text' "
        "href='#' "
        f"data-pk='{doctrine.pk}' "
        "data-name='name' "
        f"data-url='{url}' "
        f"data-title='{title}'>{doctrine.skilllist.name}</a>"
    )
    return html


def generate_edit_active_html(
    doctrine: Doctrine,
) -> str:
    """
    Generate HTML for an editable active field.

    This function creates an HTML anchor tag that allows inline editing of the active field
    of a Doctrine skill list.
    """
    url = reverse(
        viewname="corptools_doctrine:api:edit_doctrine",
        kwargs={"pk": doctrine.pk},
    )
    title = _("Enter active")

    active_text = _("Active")
    inactive_text = _("Inactive")
    if doctrine.skilllist.show_on_audit:
        button_html = f"<button class='btn btn-success btn-sm'>{active_text}</button>"
    else:
        button_html = f"<button class='btn btn-danger btn-sm'>{inactive_text}</button>"

    # Build anchor with data attributes first, render the button HTML as the anchor content.
    html = (
        "<a class='editable-boolean no_underline' "
        "href='#' "
        "data-type='select' "
        f"data-pk='{doctrine.pk}' "
        "data-name='show_on_audit' "
        f"data-url='{url}' "
        f"data-title='{title}' "
        f'data-source=\'[{{"value": true, "text": "{active_text}"}}, {{"value": false, "text": "{inactive_text}"}}]\' '
        f"data-value='{str(doctrine.skilllist.show_on_audit).lower()}'>"
        f"{button_html}</a>"
    )
    return html


def generate_edit_order_weight_html(
    doctrine: Doctrine,
) -> str:
    """
    Generate HTML for an editable order weight field.

    This function creates an HTML anchor tag that allows inline editing of the order weight field
    of a Doctrine skill list.
    """
    url = reverse(
        viewname="corptools_doctrine:api:edit_doctrine",
        kwargs={"pk": doctrine.pk},
    )
    title = _("Enter order weight")

    html = (
        "<a class='editable' "
        "href='#' "
        "data-type='number' "
        f"data-pk='{doctrine.pk}' "
        "data-name='order_weight' "
        f"data-url='{url}' "
        f"data-title='{title}'>{doctrine.skilllist.order_weight}</a>"
    )
    return html


def generate_edit_category_html(
    doctrine: Doctrine,
) -> str:
    """
    Generate HTML for an editable category field.

    This function creates an HTML anchor tag that allows inline editing of the category field
    of a Doctrine skill list.
    """
    url = reverse(
        viewname="corptools_doctrine:api:edit_doctrine",
        kwargs={"pk": doctrine.pk},
    )
    title = _("Enter category")

    html = (
        "<a class='editable' "
        "href='#' "
        "data-type='text' "
        f"data-pk='{doctrine.pk}' "
        "data-name='category' "
        f"data-url='{url}' "
        f"data-title='{title}'>{doctrine.category}</a>"
    )

    return html

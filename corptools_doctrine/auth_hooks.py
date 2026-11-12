"""Hook into Alliance Auth"""

# Django
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook

# AA CorpTools Doctrine
from corptools_doctrine import urls


class MADoctrineCheckerMenuItem(MenuItemHook):
    """This class ensures only authorized users will see the menu entry"""

    def __init__(self):
        # setup menu entry for sidebar
        MenuItemHook.__init__(
            self,
            _("Doctrine Checker"),
            "fas fa-book fa-fw",
            "corptools_doctrine:react_base",
            navactive=["corptools_doctrine:"],
        )

    def render(self, request):
        """Render the menu item"""

        if request.user.has_perm("corptools_doctrine.basic_access"):
            return MenuItemHook.render(self, request)

        return ""


@hooks.register("menu_item_hook")
def register_skillchecker_menu():
    """Register the menu item"""

    return MADoctrineCheckerMenuItem()


@hooks.register("url_hook")
def register_urls():
    """Register app urls"""

    return UrlHook(urls, "corptools_doctrine", r"^corptools_doctrine/")

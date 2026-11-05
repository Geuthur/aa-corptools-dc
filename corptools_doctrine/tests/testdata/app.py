# Third Party
import factory

# AA EVE SDE Factory
from evesde_factory.allianceauth import EveCharacterFactory, UserFactory
from evesde_factory.utils import add_character_to_user

# AA CorpTools Doctrine
from corptools_doctrine import __app_name__


class UserMainFactory(UserFactory):
    """Generate a User object with a main character and default permissions for Corp Tools Doctrine."""

    permissions__ = [f"{__app_name__}.basic_access"]
    scopes__ = ["publicData"]

    # pylint: disable=no-self-argument
    @factory.post_generation
    def main_character(obj, create, _, **kwargs):
        if not create:
            return
        if "character" in kwargs:
            character = kwargs["character"]
        else:
            character_name = f"{obj.first_name} {obj.last_name}"
            character = EveCharacterFactory(character_name=character_name)

        add_character_to_user(
            user=obj,
            character=character,
            is_main=True,
            scopes=obj._main_character_scopes,
        )

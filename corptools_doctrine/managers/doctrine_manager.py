# Standard Library
from typing import TYPE_CHECKING

# Django
from django.db import models

# Alliance Auth
from allianceauth.authentication.models import User
from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo
from allianceauth.services.hooks import get_extension_logger

# AA CorpTools Doctrine
from corptools_doctrine import __title__
from corptools_doctrine.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)

if TYPE_CHECKING:
    # AA CorpTools Doctrine
    from corptools_doctrine.models import Doctrine as DoctrineContext


class DoctrineQuerySet(models.QuerySet["DoctrineContext"]):
    def manage_to(self, user: User) -> models.QuerySet[EveCharacter]:
        qs = EveCharacter.objects.get_queryset()
        # superusers get all visible
        if user.is_superuser:
            logger.debug("Returning all Data for superuser %s.", user)
            return qs.all()

        if user.has_perm("corptools_doctrine.admin_access"):
            logger.debug("Returning all Data for %s.", user)
            return qs.all()

        if user.has_perm("corptools_doctrine.manage_access"):
            try:
                char = user.profile.main_character
                char: EveCharacter

                assert char
                # build all accepted queries
                queries = [models.Q(character_ownership__user=user)]

                if user.has_perm("corptools_doctrine.corp_access"):
                    queries.append(models.Q(corporation_id=char.corporation_id))

                if user.has_perm("corptools_doctrine.alliance_access"):
                    queries.append(models.Q(alliance_id=char.alliance_id))

                logger.debug(
                    "%s queries for user %s visible chracters.", len(queries), user
                )
                # filter based on queries
                query = queries.pop()
                for q in queries:
                    query |= q
                return qs.filter(query)
            except AssertionError:
                logger.debug("User %s has no main character. Nothing visible.", user)
                return qs.none()

        logger.debug("User %s has no permission. Nothing visible.", user)
        return qs.none()


class DoctrineManager(models.Manager["DoctrineContext"]):
    def get_queryset(self):
        return DoctrineQuerySet(self.model, using=self._db)

    @staticmethod
    def visible_eve_characters(user: User):
        qs = EveCharacter.objects.get_queryset()
        if user.is_superuser:
            logger.debug("Returning all characters for superuser %s.", user)
            return qs.all()

        if user.has_perm("corptools_doctrine.admin_access"):
            logger.debug("Returning all characters for %s.", user)
            return qs.all()

        try:
            char = user.profile.main_character
            char: EveCharacter

            assert char
            # build all accepted queries
            queries = [models.Q(character_ownership__user=user)]

            if user.has_perm("corptools_doctrine.corp_access"):
                queries.append(models.Q(corporation_id=char.corporation_id))

            if user.has_perm("corptools_doctrine.alliance_access"):
                queries.append(models.Q(alliance_id=char.alliance_id))

            if len(queries) == 0:
                return qs.none()

            logger.debug(
                "%s queries for user %s visible chracters.", len(queries), user
            )
            # filter based on queries
            query = queries.pop()
            for q in queries:
                query |= q
            return qs.filter(query)
        except AssertionError:
            logger.debug("User %s has no main character. Nothing visible.", user)
            return qs.none()

    @staticmethod
    def visible_eve_corporations(user: User):
        qs = EveCorporationInfo.objects.get_queryset()
        if user.is_superuser:
            logger.debug("Returning all corporations for superuser %s.", user)
            return qs.all()

        if user.has_perm("corptools_doctrine.admin_access"):
            logger.debug("Returning all corporations for %s.", user)
            return qs.all()

        try:
            char = user.profile.main_character
            char: EveCharacter

            assert char
            # build all accepted queries
            queries = [models.Q(corporation_id=char.corporation_id)]

            if user.has_perm("corptools_doctrine.corp_access"):
                queries.append(models.Q(corporation_id=char.corporation_id))

            if user.has_perm("corptools_doctrine.alliance_access"):
                queries.append(models.Q(alliance_id=char.alliance_id))

            if len(queries) == 0:
                return qs.none()

            logger.debug(
                "%s queries for user %s visible corporations.", len(queries), user
            )
            # filter based on queries
            query = queries.pop()
            for q in queries:
                query |= q
            return qs.filter(query)
        except AssertionError:
            logger.debug("User %s has no main character. Nothing visible.", user)
            return qs.none()

    def manage_to(self, user):
        return self.get_queryset().manage_to(user)

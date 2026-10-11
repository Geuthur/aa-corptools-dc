# Standard Library
import socket
from unittest.mock import Mock

# Third Party
from evesde_factory.eve_sde import ItemTypeFactory

# Django
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.handlers.wsgi import WSGIRequest
from django.test import RequestFactory, TestCase

# AA CorpTools Doctrine
from corptools_doctrine.tests.testdata.load_allianceauth import load_allianceauth
from corptools_doctrine.tests.testdata.utils import (
    create_evecategory,
    create_evegroup,
    create_eveitemtype,
    create_owner_from_user,
    create_user_from_evecharacter,
)


class SocketAccessError(Exception):
    """Error raised when a test script accesses the network"""


class NoSocketsTestCase(TestCase):
    """Variation of Django's TestCase class that prevents any network use.

    Example:

        .. code-block:: python

            class TestMyStuff(BaseTestCase):
                def test_should_do_what_i_need(self): ...

    """

    @classmethod
    def setUpClass(cls):
        cls.socket_original = socket.socket
        socket.socket = cls.guard
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        socket.socket = cls.socket_original
        return super().tearDownClass()

    @staticmethod
    def guard(*args, **kwargs):
        raise SocketAccessError("Attempted to access network")


class DoctrineCheckerTestCase(NoSocketsTestCase):
    """
    Preloaded Testcase class for Corp Tools Doctrine tests without Network access.

    Pre-Load:
        * Alliance Auth Characters, Corporation, Alliance Data
        * Taken User IDs: 1001, 1002, 1003, 1004, 1005

    Available Request Factory:
        `self.factory`

    Available test users:
        * `user` User with standard Corp Tools Doctrine access.
            * 'corptools_doctrine.basic_access' Permission
            * Character ID 1001
            * Corporation ID 2001
            * Alliance ID 3001
        * `user2` Second user with standard Corp Tools Doctrine access.
            * 'corptools_doctrine.basic_access' Permission
            * Character ID 1002
            * Corporation ID 2002
            * Alliance ID 3002
        * `superuser` Superuser.
            * Access to whole Application
            * Character ID 1003
        * `manage_own_user` User with manage own corporation access.
            * 'corptools_doctrine.basic_access' Permission
            * 'corptools_doctrine.corp_access' Permission
            * 'corptools_doctrine.alliance_access' Permission
            * 'corptools_doctrine.manage_access' Permission
            * Character ID 1004
            * Corporation ID 2001
            * Alliance ID 3001
        * `manage_user` User with manage corporations access.
            * 'corptools_doctrine.basic_access' Permission
            * 'corptools_doctrine.corp_access' Permission
            * 'corptools_doctrine.alliance_access' Permission
            * 'corptools_doctrine.manage_access' Permission
            * Character ID 1005
            * Corporation ID 2001
            * Alliance ID 3001

    Example:
        .. code-block:: python

            class TestMyDoctrineStuff(DoctrineCheckerTestCase):
                def test_should_do_what_i_need(self):
                    user = self.user
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Initialize Alliance Auth test data
        load_allianceauth()

        # Request Factory
        cls.factory = RequestFactory()

        # User with Standard Access - Corporation 2001
        cls.user, cls.user_character = create_user_from_evecharacter(
            character_id=1001,
            permissions=["corptools_doctrine.basic_access"],
        )
        cls.useraudit = create_owner_from_user(user=cls.user)
        # User with Standard Access - Corporation 2002
        cls.no_access, cls.no_access_character = create_user_from_evecharacter(
            character_id=1002,
        )
        cls.no_accessaudit = create_owner_from_user(user=cls.no_access)
        # User with Superuser Access - Corporation 2003
        cls.superuser, cls.superuser_character = create_user_from_evecharacter(
            character_id=1003,
            permissions=[],
        )
        cls.superuser.is_superuser = True
        cls.superuser.save()
        cls.superuseraudit = create_owner_from_user(user=cls.superuser)
        # User with Manage Own Corporation Access - Corporation 2001
        cls.manage_own_user, cls.manage_own_character = create_user_from_evecharacter(
            character_id=1004,
            permissions=[
                "corptools_doctrine.basic_access",
                "corptools_doctrine.corp_access",
                "corptools_doctrine.alliance_access",
                "corptools_doctrine.manage_access",
            ],
        )
        cls.manage_own_audit = create_owner_from_user(user=cls.manage_own_user)
        # User with Manage Alliance - Corporation 2001
        cls.manage_user, cls.manage_character = create_user_from_evecharacter(
            character_id=1005,
            permissions=[
                "corptools_doctrine.basic_access",
                "corptools_doctrine.corp_access",
                "corptools_doctrine.alliance_access",
                "corptools_doctrine.manage_access",
                "corptools_doctrine.admin_access",
            ],
        )
        cls.manage_audit = create_owner_from_user(user=cls.manage_user)

        cls.category = create_evecategory(
            category_id=16,
            name="Skill",
        )

        cls.group = create_evegroup(
            group_id=257,
            name="Spaceship Command",
            category=cls.category,
        )

        cls.evetype = create_eveitemtype(
            type_id=17940,
            name="Mining Barge",
            published=True,
            group=cls.group,
        )

        cls.item_type = ItemTypeFactory(
            id=17940,
            name="Mining Barge",
            group__id=257,
            group__name="Spaceship Command",
            group__category__id=16,
            group__category__name="Skill",
        )

    def _middleware_process_request(self, request: WSGIRequest):
        """Helper method to process middleware for a request."""
        session_middleware = SessionMiddleware(Mock())
        session_middleware.process_request(request)
        message_middleware = MessageMiddleware(Mock())
        message_middleware.process_request(request)

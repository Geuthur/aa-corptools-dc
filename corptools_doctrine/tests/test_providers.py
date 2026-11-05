# Django
from django.test import override_settings

# AA CorpTools Doctrine
from corptools_doctrine.providers import esi
from corptools_doctrine.tests import AuthTestCase


class TestEsiClient(AuthTestCase):
    @override_settings(DEBUG=False)
    def test_client_loads_with_debug_disabled(self):
        # when
        client = esi.client
        # then
        self.assertTrue(hasattr(client.Status, "GetStatus"))

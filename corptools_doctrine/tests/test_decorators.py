# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# AA CorpTools Doctrine
from corptools_doctrine import __title__
from corptools_doctrine.decorators import (
    log_timing,
)
from corptools_doctrine.providers import AppLogger
from corptools_doctrine.tests import DoctrineCheckerTestCase


class TestDecorators(DoctrineCheckerTestCase):
    def test_log_timing(self):
        # given
        logger = AppLogger(get_extension_logger(__name__), __title__)

        @log_timing(logger)
        def trigger_log_timing():
            return "Log Timing"

        # when
        result = trigger_log_timing()
        # then
        self.assertEqual(result, "Log Timing")

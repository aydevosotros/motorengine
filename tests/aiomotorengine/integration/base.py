import motorengine.aiomotorengine
import mongoengine

from tests.aiomotorengine import AsyncTestCase


class BaseIntegrationTest(AsyncTestCase):
    def setUp(self, auto_connect=True):
        # super(AsyncTestCase, self).setUp(auto_connect=auto_connect)
        super().setUp(auto_connect=False)
        if auto_connect:
            self.db = motorengine.aiomotorengine.connect(
                "test", host="localhost", port=27017, io_loop=self.io_loop
            )
            mongoengine.connect("test", host="localhost", port=27017)

    def tearDown(self):
        motorengine.connection.cleanup()
        super().tearDown()

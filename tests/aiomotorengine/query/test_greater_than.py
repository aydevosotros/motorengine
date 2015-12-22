from preggy import expect

from motorengine.query.greater_than import GreaterThanQueryOperator
from tests.aiomotorengine import AsyncTestCase


class TestGreaterThanQueryOperator(AsyncTestCase):
    def test_to_query(self):
        query = GreaterThanQueryOperator()
        expect(query).not_to_be_null()
        expect(query.to_query("field_name", 10)).to_be_like({
            "field_name": {
                "$gt": 10
            }
        })

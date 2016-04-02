#!/usr/bin/env python
# -*- coding: utf-8 -*-

from preggy import expect

from motorengine import URLField
from tests import AsyncTestCase


class TestURLField(AsyncTestCase):
    def test_create_url_field(self):
        field = URLField(db_field="test", required=True)
        expect(field.db_field).to_equal("test")
        expect(field.required).to_be_true()

    def test_validate_enforces_URLs(self):
        field = URLField()

        expect(field.validate("some non url")).to_be_false()
        expect(field.validate("http://www.globo.com/")).to_be_true()
        expect(field.validate(None)).to_be_true()

    def test_none_to_son(self):
        field = URLField()
        expect(field.to_son(None)).to_be_null()

    def test_none_from_son(self):
        field = URLField()
        expect(field.from_son(None)).to_be_null()

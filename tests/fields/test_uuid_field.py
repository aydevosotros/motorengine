#!/usr/bin/env python
# -*- coding: utf-8 -*-

from uuid import uuid4

from preggy import expect

from motorengine import UUIDField
from tests import AsyncTestCase


class TestUUIDField(AsyncTestCase):
    def test_create_uuid_field(self):
        field = UUIDField(db_field="test")
        expect(field.db_field).to_equal("test")

    def test_validate_enforces_uuid(self):
        field = UUIDField()
        uuid = uuid4()

        expect(field.validate("123")).to_be_false()
        expect(field.validate(uuid)).to_be_true()
        expect(field.validate(str(uuid))).to_be_true()
        expect(field.validate(None)).to_be_true()

    def test_is_empty(self):
        field = UUIDField()

        uuid = uuid4()

        expect(field.is_empty(uuid)).to_be_false()
        expect(field.is_empty("")).to_be_true()
        expect(field.is_empty(None)).to_be_true()

    def test_to_son(self):
        field = UUIDField()

        uuid = uuid4()

        expect(field.to_son(uuid)).to_equal(uuid)
        expect(field.to_son(str(uuid))).to_equal(uuid)
        expect(field.to_son(None)).to_be_null()

    def test_none_from_son(self):
        field = UUIDField()
        expect(field.from_son(None)).to_be_null()

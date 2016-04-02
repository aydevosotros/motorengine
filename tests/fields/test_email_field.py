#!/usr/bin/env python
# -*- coding: utf-8 -*-

from preggy import expect

from motorengine import EmailField
from tests import AsyncTestCase


class TestEmailField(AsyncTestCase):
    def test_create_email_field(self):
        field = EmailField(db_field="test", required=True)
        expect(field.db_field).to_equal("test")
        expect(field.required).to_be_true()

    def test_validate_enforces_emails(self):
        field = EmailField()

        expect(field.validate("some non email")).to_be_false()
        expect(field.validate("someone.else@gmail.com")).to_be_true()
        expect(field.validate(None)).to_be_true()

    def test_none_to_son(self):
        field = EmailField()
        expect(field.to_son(None)).to_be_null()

    def test_none_from_son(self):
        field = EmailField()
        expect(field.from_son(None)).to_be_null()

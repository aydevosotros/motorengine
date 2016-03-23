#!/usr/bin/env python
# -*- coding: utf-8 -*-

from preggy import expect
from datetime import datetime

from motorengine import DateTimeField
from tests import AsyncTestCase


class TestDateTimeField(AsyncTestCase):
    def test_create_datetime_field(self):
        field = DateTimeField(db_field="test")
        expect(field.db_field).to_equal("test")

    def test_to_son(self):
        field = DateTimeField()

        dt = datetime(2010, 11, 12, 13, 14, 15)

        expect(field.to_son(dt)).to_equal(dt)
        expect(field.to_son(None)).to_be_null()

    def test_from_son(self):
        field = DateTimeField()

        dt = datetime(2010, 11, 12, 13, 14, 15)

        expect(field.from_son(dt)).to_equal(dt)

    def test_to_son_from_string(self):
        field = DateTimeField()

        dt_str = "2010-11-12 13:14:15"
        dt = datetime(2010, 11, 12, 13, 14, 15)

        expect(field.to_son(dt_str)).to_equal(dt)

    def test_from_son_from_string(self):
        field = DateTimeField()

        dt_str = "2010-11-12 13:14:15"
        dt = datetime(2010, 11, 12, 13, 14, 15)

        expect(field.from_son(dt_str)).to_equal(dt)

    def test_validate(self):
        dt = datetime(2010, 11, 12, 13, 14, 15)
        field = DateTimeField()

        expect(field.validate(None)).to_be_true()
        expect(field.validate(dt)).to_be_true()
        expect(field.validate("qwieiqw")).to_be_false()

    def test_document_with_auto_insert_datetime_field(self):
        from motorengine import Document

        class Model(Document):
            created = DateTimeField(
                auto_now_on_insert=True, auto_now_on_update=False
            )

        self.drop_coll(Model.__collection__)

        model = Model()

        expect(model.created).to_be_null()

        model.save(callback=self.stop)
        self.wait()
        created = model.created

        expect(isinstance(created, datetime)).to_be_true()
        expect(created).to_equal(model.created)

        now_before = datetime.now()
        Model.objects.create(callback=self.stop)
        model = self.wait()
        created = model.created

        expect(created).to_equal(model.created)

        now_after = datetime.now()

        expect(model._id).not_to_be_null()
        expect(model.created).to_be_greater_or_equal_to(now_before)
        expect(model.created).to_be_lesser_or_equal_to(now_after)

        model.save(callback=self.stop)
        self.wait()

        expect(created).to_equal(model.created)

    def test_document_with_auto_update_datetime_field(self):
        from motorengine import Document

        class Model(Document):
            created = DateTimeField(
                auto_now_on_insert=True, auto_now_on_update=True
            )

        self.drop_coll(Model.__collection__)

        Model.objects.create(callback=self.stop)
        model = self.wait()

        model_id = model._id
        Model.objects.get(model_id, callback=self.stop)
        model = self.wait()

        created = model.created

        expect(created).to_equal(model.created)

        model.save(callback=self.stop)
        self.wait()
        now_after = datetime.now()

        expect(model.created).to_be_greater_or_equal_to(created)
        expect(model.created).to_be_lesser_or_equal_to(now_after)
        created = model.created
        expect(created).to_equal(model.created)

    def test_embedded_document_with_auto_insert_datetime_field(self):
        from motorengine import Document
        from motorengine import EmbeddedDocumentField

        class Model(Document):
            created = DateTimeField(
                auto_now_on_insert=True, auto_now_on_update=False
            )

        class Doc(Document):
            embedded = EmbeddedDocumentField(
                embedded_document_type=Model, required=True
            )

        self.drop_coll(Doc.__collection__)
        self.drop_coll(Model.__collection__)

        doc = Doc(embedded=Model())

        expect(doc.embedded.created).to_be_null()

        doc.save(callback=self.stop)
        self.wait()

        expect(doc.embedded.created).not_to_be_null()
        expect(isinstance(doc.embedded.created, datetime)).to_be_true()

    def test_embedded_document_with_auto_update_datetime_field(self):
        from motorengine import Document
        from motorengine import EmbeddedDocumentField

        class Model(Document):
            created = DateTimeField(
                auto_now_on_insert=True, auto_now_on_update=True
            )

        class Doc(Document):
            embedded = EmbeddedDocumentField(
                embedded_document_type=Model, required=False
            )

        self.drop_coll(Doc.__collection__)
        self.drop_coll(Model.__collection__)

        Doc.objects.create(callback=self.stop)
        doc = self.wait()

        expect(doc.embedded).to_be_null()

        doc = Doc(embedded=Model())

        expect(doc.embedded.created).to_be_null()

        now_before = datetime.now()
        doc.save(callback=self.stop)
        self.wait()
        now_after = datetime.now()

        expect(doc.embedded.created).not_to_be_null()
        expect(isinstance(doc.embedded.created, datetime)).to_be_true()
        expect(doc.embedded.created).to_be_greater_or_equal_to(now_before)
        expect(doc.embedded.created).to_be_lesser_or_equal_to(now_after)

        created = doc.embedded.created

        doc.save(callback=self.stop)
        self.wait()

        expect(doc.embedded.created).not_to_be_null()
        expect(isinstance(doc.embedded.created, datetime)).to_be_true()
        expect(doc.embedded.created).to_be_greater_than(created)
        expect(doc.embedded.created).to_be_lesser_or_equal_to(datetime.now())

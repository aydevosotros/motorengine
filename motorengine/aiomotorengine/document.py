import six
import asyncio

import motorengine.document
from motorengine.aiomotorengine.metaclasses import DocumentMetaClass


class BaseDocument(motorengine.document.BaseDocument):

    @classmethod
    @asyncio.coroutine
    def ensure_index(cls):
        return (yield from cls.objects.ensure_index())

    @asyncio.coroutine
    def save(self, alias=None):
        '''
        Creates or updates the current instance of this document.
        '''
        return (yield from self.objects.save(self, alias=alias))

    @asyncio.coroutine
    def delete(self, alias=None):
        '''
        Deletes the current instance of this Document.

        .. testsetup:: saving_delete_one

            import asyncio
            from motorengine.aiomotorengine import Document, StringField, connect

            class User(Document):
                __collection__ = "UserDeletingInstance"
                name = StringField()

            io_loop = asyncio.get_event_loop()
            connect("test", host="localhost", port=27017, io_loop=io_loop)

        .. testcode:: saving_delete_one

            async def create_user():
                user = User(name="Bernardo")
                user = await user.save()
                number_of_deleted_items = await user.delete()
                assert number_of_deleted_items == 1

            io_loop.run_until_complete(create_user())
        '''
        return (yield from self.objects.remove(instance=self, alias=alias))

    @asyncio.coroutine
    def load_references(self, fields=None, alias=None):

        references = self.find_references(document=self, fields=fields)
        reference_count = len(references)

        if not reference_count:  # there are no references
            return {
                'loaded_reference_count': reference_count,
                'loaded_values': []
            }

        for (
            dereference_function, document_id, values_collection,
            field_name, fill_values_method
        ) in references:
            doc = yield from dereference_function(document_id)
            if fill_values_method is None:
                fill_values_method = self.fill_values_collection

            fill_values_method(values_collection, field_name, doc)

        return {
            'loaded_reference_count': reference_count,
            'loaded_values': values_collection
        }


class Document(six.with_metaclass(DocumentMetaClass, BaseDocument)):
    '''
    Base class for all documents specified in MotorEngine.
    '''
    pass

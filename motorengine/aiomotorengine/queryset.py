import sys
import asyncio

from pymongo.errors import DuplicateKeyError
from easydict import EasyDict as edict
from bson.objectid import ObjectId

from motorengine.aiomotorengine.aggregation.base import Aggregation
from motorengine.aiomotorengine import get_connection
from motorengine.errors import (
    UniqueKeyViolationError, PartlyLoadedDocumentError
)

import motorengine.queryset


class QuerySet(motorengine.queryset.QuerySet):

    def _get_connection_function(self):
        return get_connection

    @asyncio.coroutine
    def create(self, alias=None, **kwargs):
        '''
        Creates and saved a new instance of the document.

        .. testsetup:: saving_create

            import asyncio
            from motorengine.aiomotorengine import Document, StringField, connect

            class User(Document):
                __collection__ = "UserCreatingInstances"
                name = StringField()

            io_loop = asyncio.get_event_loop()
            connect("test", host="localhost", port=27017, io_loop=io_loop)

        .. testcode:: saving_create

            async def create_user():
                user = await User.objects.create(name="Bernardo")
                assert user.name == "Bernardo"

            io_loop.run_until_complete(create_user())
        '''
        document = self.__klass__(**kwargs)
        return (yield from self.save(document=document, alias=alias))

    @asyncio.coroutine
    def save(self, document, alias=None):
        if document.is_partly_loaded:
            msg = (
                "Partly loaded document {0} can't be saved. Document should "
                "be loaded without 'only', 'exclude' or 'fields' "
                "QuerySet's modifiers"
            )
            raise PartlyLoadedDocumentError(
                msg.format(document.__class__.__name__)
            )

        self.update_field_on_save_values(document, document._id is not None)
        if self.validate_document(document):
            yield from self.ensure_index(alias=alias)
            return (yield from self.save_document(document, alias=alias))

    @asyncio.coroutine
    def save_document(self, document, alias=None):
        ''' Insert or update document '''
        doc = document.to_son()

        if document._id is not None:
            try:
                yield from self.coll(alias).update({'_id': document._id}, doc)
            except DuplicateKeyError as e:
                raise UniqueKeyViolationError.from_pymongo(
                    str(e), self.__klass__
                )
        else:
            try:
                doc_id = yield from self.coll(alias).insert(doc)
            except DuplicateKeyError as e:
                raise UniqueKeyViolationError.from_pymongo(
                    str(e), self.__klass__
                )
            document._id = doc_id
        return document

    @asyncio.coroutine
    def bulk_insert(self, documents, alias=None):
        '''
        Inserts all documents passed to this method in one go.
        '''

        is_valid = True
        docs_to_insert = []

        for document_index, document in enumerate(documents):
            self.update_field_on_save_values(
                document, document._id is not None
            )
            try:
                is_valid = is_valid and self.validate_document(document)
            except Exception:
                err = sys.exc_info()[1]
                raise ValueError((
                    "Validation for document %d in the documents "
                    "you are saving failed with: %s"
                ) % (
                    document_index,
                    str(err)
                ))

            if not is_valid:
                return

            docs_to_insert.append(document.to_son())

        if not is_valid:
            return

        doc_ids = yield from self.coll(alias).insert(docs_to_insert)

        for object_index, object_id in enumerate(doc_ids):
            documents[object_index]._id = object_id
        return documents

    @asyncio.coroutine
    def update(self, definition, alias=None):

        definition = self.transform_definition(definition)

        update_filters = {}
        if self._filters:
            update_filters = self.get_query_from_filters(self._filters)

        update_arguments = dict(
            spec=update_filters,
            document={'$set': definition},
            multi=True,
        )
        res = yield from self.coll(alias).update(**update_arguments)

        return edict({
            "count": int(res['n']),
            "updated_existing": res['updatedExisting']
        })

    @asyncio.coroutine
    def delete(self, alias=None):
        '''
        Removes all instances of this document that match the specified filters (if any).

        .. testsetup:: saving_delete

            import asyncio
            from motorengine.aiomotorengine import Document, StringField, connect

            class User(Document):
                __collection__ = "UserDeletingInstances"
                name = StringField()

            io_loop = asyncio.get_event_loop()
            connect("test", host="localhost", port=27017, io_loop=io_loop)

        .. testcode:: saving_delete

            async def saving_delete():
                user = User(name="Bernardo")
                await user.save()

                number_of_deleted_items = await User.objects.filter(name="Bernardo").delete()
                assert number_of_deleted_items == 1

            io_loop.run_until_complete(saving_delete())
        '''

        return (yield from self.remove(alias=alias))

    @asyncio.coroutine
    def remove(self, instance=None, alias=None):

        if instance is not None:
            if hasattr(instance, '_id') and instance._id:
                res = yield from self.coll(alias).remove(instance._id)
        else:
            if self._filters:
                remove_filters = self.get_query_from_filters(self._filters)
                res = yield from self.coll(alias).remove(remove_filters)
            else:
                res = yield from self.coll(alias).remove()
        return res['n']

    @asyncio.coroutine
    def get(self, id=None, alias=None, **kwargs):
        '''
        Gets a single item of the current queryset collection using it's id.

        In order to query a different database, please specify the `alias` of the database to query.
        '''

        from motorengine.aiomotorengine import Q

        if id is None and not kwargs:
            raise RuntimeError("Either an id or a filter must be provided to get")

        if id is not None:
            if not isinstance(id, ObjectId):
                id = ObjectId(id)

            filters = {
                "_id": id
            }
        else:
            filters = Q(**kwargs)
            filters = self.get_query_from_filters(filters)

        instance = yield from self.coll(alias).find_one(
            filters, fields=self._loaded_fields.to_query(self.__klass__)
        )
        if instance is None:
            return None
        else:
            doc = self.__klass__.from_son(
                instance,
                # if _loaded_fields is not empty then
                # document is partly loaded
                _is_partly_loaded=bool(self._loaded_fields),
                # set projections for references (if any)
                _reference_loaded_fields=self._reference_loaded_fields
            )
            if self.is_lazy:
                return doc
            else:
                yield from doc.load_references()
                return doc

    @asyncio.coroutine
    def find_all(self, lazy=None, alias=None):
        '''
        Returns a list of items in the current queryset collection that match specified filters (if any).

        In order to query a different database, please specify the `alias` of the database to query.

        Usage::

            result = await User.objects.find_all()
            # do something with result
            # users is None if no users found
        '''
        to_list_arguments = {}
        if self._limit is not None:
            to_list_arguments['length'] = self._limit
        else:
            to_list_arguments['length'] = motorengine.queryset.DEFAULT_LIMIT

        cursor = self._get_find_cursor(alias=alias)

        self._filters = {}

        docs = yield from cursor.to_list(**to_list_arguments)

        # if _loaded_fields is not empty then documents are partly loaded
        is_partly_loaded = bool(self._loaded_fields)

        result = []
        for doc in docs:
            obj = self.__klass__.from_son(
                doc,
                # set projections for references (if any)
                _reference_loaded_fields=self._reference_loaded_fields,
                _is_partly_loaded=is_partly_loaded
            )

            if (lazy is not None and not lazy) or not obj.is_lazy:
                yield from obj.load_references(obj._fields)

            result.append(obj)

        return result

    @asyncio.coroutine
    def count(self, alias=None):
        '''
        Returns the number of documents in the collection that match the specified filters, if any.
        '''
        cursor = self._get_find_cursor(alias=alias)
        self._filters = {}
        return (yield from cursor.count())

    @property
    def aggregate(self):
        return Aggregation(self)

    @asyncio.coroutine
    def ensure_index(self, alias=None):
        fields_with_index = []
        for field_name, field in self.__klass__._fields.items():
            if field.unique or field.sparse:
                fields_with_index.append(field)

        created_indexes = []

        for field in fields_with_index:
            res = yield from self.coll(alias).ensure_index(
                field.db_field,
                unique=field.unique,
                sparse=field.sparse
            )
            created_indexes.append(res)

        return len(created_indexes)

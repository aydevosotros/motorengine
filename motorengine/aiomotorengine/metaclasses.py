import motorengine.metaclasses
from motorengine.aiomotorengine.queryset import QuerySet


class DocumentMetaClass(motorengine.metaclasses.DocumentMetaClass):
    query_set_class = QuerySet
